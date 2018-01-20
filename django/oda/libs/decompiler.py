import os
from tempfile import NamedTemporaryFile
from subprocess import check_call
from oda.libs.odb.binaries import BinaryString

from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.section import Section

try:
    import snowman
except ImportError:
    print("Failed to load snowman library, decompiler will be unavailable.")
    class snowman(object):
        @staticmethod
        def decompile(path, start, end):
            return "decompiler library not installed."


class OdaDecompilerException(Exception):
    """Base exception class for all decompilation exceptions"""


class OdaDecompilerResults(object):
    def __init__(self, start, end, source):
        self.start = start
        self.end = end
        self.source = source


def bin2elf(path, options):
    f = NamedTemporaryFile(delete=False)

    arch = options.architecture

    # we only support x86 for decompilation at this time
    if 'i386' not in arch:
        raise OdaDecompilerException("Architecture %s not supported" % arch)

    # if this is a 64-bit target, set ELF appropriately
    if '64' in arch == '':
        target = "elf64-x86-64"
    else:
        target = "elf32-i386"

    try:
        check_call(["objcopy",
                    "-I", "binary",
                    "-O", target,
                    "-B", arch,
                    "--rename-section",
                    ".data=.text,alloc,load,readonly,code",
                    path,
                    f.name])
    except Exception as e:
        os.unlink(f.name)
        raise OdaDecompilerException("Failed to create ELF from BinaryStringStorage")

    return f.name


class OdaDecompiler(object):
    def __init__(self, odb_file):
        self.odb_file = odb_file

    def decompile(self, vma):
        options = self.odb_file.get_binary().options
        start = None
        end = None

        # for binary strings, default to the section range containing the given address
        sections = filter(lambda s: s.is_loadable(), self.odb_file.get_structure_list(Section))
        for s in sections:
            if (vma >= s.vma) and (vma < (s.vma + s.size)):
                start = s.vma
                end = s.vma + s.size - 1

        # identify the function containing the given address and limit decompilation to the function bounds
        functions = sorted(self.odb_file.get_structure_list(Function), key=lambda f: f.vma)
        for f in functions:
            if vma >= f.vma:
                start = f.vma
            elif vma < f.vma:
                end = f.vma  # - 1?
                break

        # if we established the address range to decompile
        if (start is not None) and (end is not None):

            # for BinaryStringStorage we have to convert to ELF
            path = self.odb_file.binary.file_handle().name
            if type(self.odb_file.binary) == BinaryString:
                path = bin2elf(path, options)

            source = snowman.decompile(path, start, end)

            # delete the temp ELF file we created above
            if type(self.odb_file.binary) == BinaryString:
                os.unlink(path)
        else:
            raise OdaDecompilerException("Failed to identify function limits")

        return OdaDecompilerResults(start, end, source)
