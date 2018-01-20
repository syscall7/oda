import os
import shutil
import logging

from tempfile import NamedTemporaryFile
from subprocess import check_call

import idb
from django.conf import settings

from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.ops.comment_operations import CreateCommentOperation
from oda.libs.odb.ops.create_function_operation import CreateFunctionOperation

logger = logging.getLogger(__name__)


class OdaIdbImportException(Exception):
    """Base exception class for all IDB import exceptions"""

class IdbImportOperation(Operation):

    def __init__(self):
        super().__init__()
        self.object_id = -1

    def __str__(self):
        return "Imported IDA Pro database"

    @staticmethod
    def deserialize(d):
        op = IdbImportOperation()
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
        }
        d.update(super().serialize())
        return d

    def import_comments(self, odb_file, db, api):

        # get all the segments and iterate
        segnames = idb.analysis.SegStrings(db).strings
        segs = idb.analysis.Segments(db).segments
        for seg in segs.values():
            ea = seg.startEA
            name = segnames[seg.name_index]

            # for each item in the segment
            while ea < seg.endEA:
                try:
                    # if this item has a comment
                    flags = api.idc.GetFlags(ea)
                    if api.ida_bytes.has_cmt(flags):
                        cmt = None

                        # first try to get a 'repeatable' comment
                        try:
                            cmt = api.idc.GetCommentEx(ea, True)
                        except:
                            pass

                        # if that didn't work, get the 'non-repeatable' comment
                        if not cmt:
                            try:
                                cmt = api.idc.GetCommentEx(ea, False)
                            except:
                                pass

                        if cmt:
                            logger.info("Found comment '%s' at 0x%x" % (cmt, ea))
                            odb_file.execute(CreateCommentOperation(ea, cmt))
                        else:
                            logger.error("Could not retrieve comment at 0x%x" % ea)

                    ea = api.idc.NextHead(ea)

                except Exception as e:
                    logger.warning("Failed to retrieve comment in segment %s "
                                   "at address 0x%x, skipping rest of segment"
                                   % (name, ea))
                    break

    def import_symbols(self, odb_file, db, api):

        functions = idb.analysis.Functions(db)

        for (addr, func) in functions.functions.items():
            try:
                name = api.idc.GetFunctionName(addr)
                flags = api.idc.GetFunctionFlags(addr)
                sym_type = 't'
                if flags & api.ida_funcs.FUNC_THUNK or \
                   flags & api.ida_funcs.FUNC_LIB:
                    sym_type = "U"
                    if name.startswith("."):
                        name = name[1:]
                odb_file.execute(CreateFunctionOperation(addr, name,
                                                         sym_type=sym_type))

            except Exception as e:
                logger.warning("Failed to lookup function name at 0x%x" % addr)


    def operate(self, odb_file):

        # parse the .idb file
        db = idb.from_buffer(odb_file.binary.idb_file().read())
        api = idb.IDAPython(db)

        self.import_symbols(odb_file, db, api)
        self.import_comments(odb_file, db, api)


class Elf(object):

    FLAGS_ALLOC = "alloc"
    FLAGS_LOAD = "alloc"
    FLAGS_RO = "readonly"
    FLAGS_CODE = "code"
    FLAGS_CONTENTS = "contents"
    FLAGS_DATA = "data"

    def __init__(self, path, target, arch):
        self.path = path
        self.target = target
        self.arch = arch

        # track number of duplicate section names
        self.sections = {}

    def add_section(self, name, addr, contents, flags):
        """"Inject sections into the ELF"""

        # deconflict duplicate section names
        if name in self.sections.keys():
            self.sections[name] += 1
            name = "%s.dup.%d" % (name, self.sections[name])
        else:
            self.sections[name] = 0

        infile = NamedTemporaryFile(delete=False)
        with open(infile.name, "wb") as f:
            logger.debug("Creating input file %s for section %s" % (
                infile.name, name))
            f.write(contents)

        logger.debug("Converting section %s to ELF format" % name)

        # if we already have an output ELF file, just insert the new section
        if os.path.getsize(self.path) > 0:
            # next, add it to the final ELF file
            try:
                logger.debug("Adding section %s" % name)
                check_call(["objcopy",
                            "--add-section",
                            "%s=%s" % (name, infile.name),
                            self.path,])
            except Exception as e:
                raise OdaIdbImportException("Failed to add section")
            finally:
                os.unlink(infile.name)

        # else, if we haven't created the output ELF yet, do that now
        else:
            try:
                check_call(["objcopy",
                        "-I", "binary",
                        "-O", self.target,
                        "-B", self.arch,
                        "--rename-section",
                        ".data=%s" % (name),
                        infile.name,
                        self.path])
            except Exception as e:
                raise OdaIdbImportException("Failed to create section")
            finally:
                os.unlink(infile.name)

        # set the section flags
        try:
            logger.debug("Setting section flags for %s" % name)
            check_call(["objcopy",
                        "--change-section-address",
                        "%s=0x%x" % (name,addr),
                        "--set-section-flags",
                        "%s=%s" % (name, ','.join(flags)),
                        self.path])
        except Exception as e:
            raise OdaIdbImportException("Failed to set section flags")
            os.unlink(infile.name)

    def add_symbols(self, symbols):
        """ Inject symbols into the ELF """
        for (name, addr) in symbols:
            # set the section flags
            try:
                logger.debug("Adding function %s", name)
                check_call(["objcopy",
                            "--add-symbol",
                            "%s=0x%x,function,global" % (name,addr),
                            self.path])
            except Exception as e:
                raise OdaIdbImportException("Failed to add symbol %s" %
                                            name)


class IdbImport(object):
    """Class to convert an .idb file into ODA land"""

    def __init__(self, file):
        self.file = file
        self.db = None

        # determine if valid .idb by attempting to parse the given file
        try:
            self.db = idb.from_buffer(self.file.read())
            self.api = idb.IDAPython(self.db)
        except Exception:
            # nothing to do, self.db will remain as None
            pass

    def is_idb(self):
        """See if this file is a valid .idb file"""
        return self.db is not None

    def guess_arch(self):
        """Extract the processor architecture from the .idb file"""
        assert(self.db is not None)

        segs = idb.analysis.Segments(self.db).segments
        info = self.api.idaapi.get_inf_structure()
        processor = info.procname
        bitness = 0

        # 0: 16-bits
        # 1: 32-bits
        # 2: 64-bits
        for seg in segs.values():
            if seg.bitness > bitness:
                # TODO: why are we getting 3?
                bitness = min(seg.bitness, 2)

        # map process,bitness to arch,target
        mapping = {
            ('metapc',1) : ('i386', 'elf32-i386'),
            ('metapc',2) : ('i386', 'elf64-x86-64'),
        }

        return mapping[(processor, bitness)]

    def describe(self):
        """Generate a description of this .idb file"""
        info = self.api.idaapi.get_inf_structure()
        desc = []
        root = idb.analysis.Root(self.db)
        version_str = root.version_string
        input_file_path = "unknown"
        try:
            input_file_path = root.input_file_path
        except:
            pass
        desc.append("IDA Pro database from version %s" % version_str)
        desc.append("Original file path: %s" % input_file_path)
        desc.append("Processor name: %s" % info.procname)

        return desc

    def get_flags(self, segment, name):
        """Map the segment type and permissions to ELF section flags"""

        loadable = [Elf.FLAGS_ALLOC, Elf.FLAGS_LOAD, Elf.FLAGS_CONTENTS]
        types = {
            0 : [],
            1 : [],
            2 : [Elf.FLAGS_CODE, Elf.FLAGS_RO] + loadable,
            3 : loadable,
        }

        perms = {
            # Not defined
            0 : [],

            # SEGPERM_EXEC
            1 : [Elf.FLAGS_CODE],

            # SEGPERM_WRITE
            2 : [],

            # SEGPERM_EXEC | SEGPERM_WRITE
            3 : [],

            # SEGPERM_READ
            4 : [Elf.FLAGS_RO],

            # SEGPERM_EXEC | SEGPERM_READ
            5 : [Elf.FLAGS_RO],

            # SEGPERM_READ | SEGPERM_WRITE
            6 : [],

            # SEGPERM_EXEC | SEGPERM_READ | SEGPERM_WRITE
            7 : [],
        }

        names = {
            '.rdata' : [Elf.FLAGS_RO] + loadable,
            '.data' :  [Elf.FLAGS_DATA] + loadable,
            '.pdata' :  [Elf.FLAGS_DATA] + loadable,
        }

        flags = []

        if name in names:
            flags.extend(names[name])
        else:
            if segment.type in types:
                flags.extend(types[segment.type])

            if segment.perm in perms:
                flags.extend(perms[segment.perm])

        return set(flags)

    def reconstruct_elf(self):
        """Create an ELF file based on the contents of the .idb file"""

        segs = idb.analysis.Segments(self.db).segments
        segstrings = idb.analysis.SegStrings(self.db).strings
        api = idb.IDAPython(self.db)

        processor = api.idaapi.get_inf_structure().procname
        # TODO: look at bitness from .idb to determine 32/64

        for seg in segs.values():
            logger.debug(
                "Segment %s, perm %s, type %s: 0x%08x (%d) -> 0x%08x (%d)" %
                (segstrings[seg.name_index], seg.perm,
                 seg.type, seg.startEA, seg.startEA, seg.endEA, seg.endEA))

        outfile = NamedTemporaryFile(dir=settings.MEDIA_ROOT, delete=False)

        arch, target = self.guess_arch()

        # we only support x86 for decompilation at this time
        if 'i386' not in arch:
            raise OdaIdbImportException("Architecture %s not supported" % arch)

        elf = Elf(outfile.name, target, arch)
        sections = 0
        for seg in segs.values():
            name = segstrings[seg.name_index]

            if name == "LOAD":
                # skip these for now, since I don't currently have a good way
                #  to distinguish code from data sections
                logger.info("Skipping LOAD section")
                continue

            logger.debug("Segment %s, perm %s, type %s: 0x%08x -> 0x%08x" %
                         (name, seg.perm,
                          seg.type, seg.startEA,
                          seg.endEA))

            end = seg.endEA
            MAX_ATTEMPTS = 2
            for attempt in range(MAX_ATTEMPTS):
                try:
                    data = api.idc.GetManyBytes(seg.startEA, end -
                                                seg.startEA)

                    elf.add_section(name, seg.startEA, data, self.get_flags(
                        seg, name))
                    sections += 1
                    break

                except KeyError as e:
                        end = e.args[0]
                        logger.warning("Truncating section %s, start 0x%x, "
                                       "end 0x%x to stop at 0x%x" %
                                       (name, seg.startEA, seg.endEA, end))
                except Exception as e:
                        logger.warning(e)
                        logger.warning("Skipping section %s, start 0x%x, end 0x%x "
                                       "can't get bytes" % (name, seg.startEA,
                                                            seg.endEA))
                        break

        if sections:
            return outfile.name
        else:
            return None
