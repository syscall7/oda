from bfd import FLAGS
from tempfile import NamedTemporaryFile
from shutil import copy
from collections import namedtuple

from django.conf import settings
from django.core.files import File
from oda.libs.odb.odb_file import OdbFile
from oda.test.oda_test_case import OdaLibTestCase
from oda.libs.odb.structures.comment import Comment
from oda.libs.odb.ops.idb_import_operation import IdbImport
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.symbol import Symbol

from oda.libs.odb.ops.idb_import_operation import IdbImportOperation
from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.passive_scan_operation import PassiveScanOperation

from oda.apps.odaweb.models import BinaryFile, BinaryFileModel

IdbTestFile = namedtuple('IdbTestFile',
                         ['fname', 'arch', 'target', 'sections', 'symbols',
                          'comments', ])

class TestIDAImportOperation(OdaLibTestCase):

    def helper_import_idb(self, fname, arch, target):

        # django configuration requires input file to be in /tmp, so copy there
        
        idb_path = NamedTemporaryFile(dir=settings.MEDIA_ROOT, delete=False).name
        copy(self.get_test_bin_path('idb/%s' % fname), idb_path)

        # verify we have a valid .idb file
        idbImport = IdbImport(open(idb_path, "rb"))
        self.assertTrue(idbImport.is_idb())

        # guess the architecture correctly
        actual_arch, actual_target = idbImport.guess_arch()
        self.assertEqual(arch, actual_arch)
        self.assertEqual(target, actual_target)

        # reconstruct as ELF
        elfPath = idbImport.reconstruct_elf()
        self.assertIsNotNone(elfPath)

        # create the binary file
        binary_file = BinaryFile.create_from_idb(File(open(idb_path, "rb")))
        binary_file.binary_options.architecture = arch
        binary_file.binary_options.target = target
        binary_file.binary_options.save()
        binary_file.save()

        # create the ODB file
        odb_file = OdbFile(BinaryFileModel(binary_file.id))
        odb_file.binary.set_the_file(File(open(elfPath, "rb")))
        odb_file.execute(IdbImportOperation())
        odb_file.execute(LoadOperation())
        odb_file.execute(PassiveScanOperation())

        return odb_file

    def test_basic_import(self):

        imports = [
            ('kernel32.i64', 'i386', 'elf64-x86-64'),
            ('ls.idb', 'i386', 'elf32-i386'),
        ]

        for (fname, arch, target) in imports:
            self.helper_import_idb(fname, arch, target)

    def test_comments(self):

        odb_file = self.helper_import_idb('nc.i64', 'i386', 'elf64-x86-64')
        comments = {c.vma: c for c in odb_file.get_structure_list(Comment)}

        self.assertIsNotNone(comments)

        self.assertEqual(
            "this is a comment on the second instruction in main",
            comments[0x401732].comment)

    def test_sections(self):

        fname, arch, target = ('nc.i64', 'i386', 'elf64-x86-64')
        odb_file = self.helper_import_idb(fname, arch, target)

        """
        0 .interp       0000001c  0000000000400238  0000000000400238  00000238  2**0
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        1 .note.ABI-tag 00000020  0000000000400254  0000000000400254  00000254  2**2
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        2 .note.gnu.build-id 00000024  0000000000400274  0000000000400274  00000274  2**2
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        3 .gnu.hash     00000040  0000000000400298  0000000000400298  00000298  2**3
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        4 .dynsym       00000648  00000000004002d8  00000000004002d8  000002d8  2**3
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        5 .dynstr       000002f5  0000000000400920  0000000000400920  00000920  2**0
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        6 .gnu.version  00000086  0000000000400c16  0000000000400c16  00000c16  2**1
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        7 .gnu.version_r 000000c0  0000000000400ca0  0000000000400ca0  00000ca0  2**3
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        8 .rela.dyn     00000090  0000000000400d60  0000000000400d60  00000d60  2**3
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
        9 .rela.plt     00000570  0000000000400df0  0000000000400df0  00000df0  2**3
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
       10 .init         0000001a  0000000000401360  0000000000401360  00001360  2**2
                        CONTENTS, ALLOC, LOAD, READONLY, CODE
       11 .plt          000003b0  0000000000401380  0000000000401380  00001380  2**4
                        CONTENTS, ALLOC, LOAD, READONLY, CODE
       12 .text         00003134  0000000000401730  0000000000401730  00001730  2**4
                        CONTENTS, ALLOC, LOAD, READONLY, CODE
       13 .fini         00000009  0000000000404864  0000000000404864  00004864  2**2
                        CONTENTS, ALLOC, LOAD, READONLY, CODE
       14 .rodata       00001438  0000000000404880  0000000000404880  00004880  2**5
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
       15 .eh_frame_hdr 000000d4  0000000000405cb8  0000000000405cb8  00005cb8  2**2
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
       16 .eh_frame     000004bc  0000000000405d90  0000000000405d90  00005d90  2**3
                        CONTENTS, ALLOC, LOAD, READONLY, DATA
       17 .init_array   00000008  0000000000606df0  0000000000606df0  00006df0  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       18 .fini_array   00000008  0000000000606df8  0000000000606df8  00006df8  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       19 .jcr          00000008  0000000000606e00  0000000000606e00  00006e00  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       20 .dynamic      000001f0  0000000000606e08  0000000000606e08  00006e08  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       21 .got          00000008  0000000000606ff8  0000000000606ff8  00006ff8  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       22 .got.plt      000001e8  0000000000607000  0000000000607000  00007000  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       23 .data         00000018  00000000006071e8  00000000006071e8  000071e8  2**3
                        CONTENTS, ALLOC, LOAD, DATA
       24 .bss          000801f8  0000000000607200  0000000000607200  00007200  2**5
                        ALLOC
       25 .gnu_debuglink 00000010  0000000000000000  0000000000000000  00007200  2**0
                        CONTENTS, READONLY

        """
        def toFlags(flags):

            flagDict = { f.name: f for f in FLAGS}

            bfdFlags = []
            for f in flags:
                bfdFlags.append(flagDict[f])

            return bfdFlags


        expectedSections = (
            #Section(0, '.interp', 0x0000001c, 0x0000000000400238,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.note.ABI-tag', 0x00000020, 0x0000000000400254,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.note.gnu.build-id', 0x00000024, 0x0000000000400274,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.gnu.hash', 0x00000040, 0x0000000000400298,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.dynsym', 0x00000648, 0x00000000004002d8,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.dynstr', 0x000002f5, 0x0000000000400920,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.gnu.version', 0x00000086, 0x0000000000400c16,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.gnu.version_r', 0x000000c0, 0x0000000000400ca0,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.rela.dyn', 0x00000090, 0x0000000000400d60,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            #Section(0, '.rela.plt', 0x00000570, 0x0000000000400df0,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            Section(0, '.init', 0x0000001a, 0x0000000000401360,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                      'SEC_READONLY', 'SEC_CODE'])),
            Section(0, '.plt', 0x000003b0, 0x0000000000401380,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                      'SEC_READONLY', 'SEC_CODE'])),
            Section(0, '.text', 0x00003134, 0x0000000000401730,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                      'SEC_READONLY', 'SEC_CODE'])),
            Section(0, '.fini', 0x00000009, 0x0000000000404864,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                      'SEC_READONLY', 'SEC_CODE'])),
            Section(0, '.rodata', 0x00001438, 0x0000000000404880,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                      'SEC_READONLY', 'SEC_DATA'])),
            Section(0, '.eh_frame_hdr', 0x000000d4, 0x0000000000405cb8,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                      'SEC_READONLY', 'SEC_DATA'])),
            #Section(0, '.eh_frame', 0x000004bc, 0x0000000000405d90,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
            #          'SEC_READONLY', 'SEC_DATA']),
            Section(0, '.init_array', 0x00000008, 0x0000000000606df0,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                       'SEC_DATA'])),
            Section(0, '.fini_array', 0x00000008, 0x0000000000606df8,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                       'SEC_DATA'])),
            Section(0, '.jcr', 0x00000008, 0x0000000000606e00,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                       'SEC_DATA'])),
            #Section(0, '.dynamic', 0x000001f0, 0x0000000000606e08,
            #        ['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD', 'SEC_DATA']),
            Section(0, '.got', 0x00000008, 0x0000000000606ff8,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                       'SEC_DATA'])),
            Section(0, '.got.plt', 0x000001e8, 0x0000000000607000,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                       'SEC_DATA'])),
            Section(0, '.data', 0x00000018, 0x00000000006071e8,
                    toFlags(['SEC_HAS_CONTENTS', 'SEC_ALLOC', 'SEC_LOAD',
                       'SEC_DATA'])),
            Section(0, '.bss', 0x000801f8, 0x0000000000607200,
                    toFlags(['SEC_ALLOC'])),
            #Section(0, '.gnu_debuglink', 0x00000010, 0x0000000000000000,
            #         ['SEC_HAS_CONTENTS', 'SEC_READONLY']),
        )

        actualSections = sorted(odb_file.get_structure_list(Section),
                                key=lambda s: s.vma)

        self.assertEqual(len(expectedSections), len(actualSections))

        for expected,actual in zip(expectedSections, actualSections):
            self.assertEqual(expected.name, actual.name)

            self.assertEqual(expected.size, actual.size,
                             "Size mismatch for section %s" % expected.name)

            self.assertEqual(expected.vma, actual.vma,
                             "VMA mismatch for section %s" % expected.name)

            actualFlags = [f.name for f in actual.flags]
            expectedFlags = [f.name for f in expected.flags]
            self.assertEqual(set(expectedFlags), set(actualFlags),
                             "Flags mismatch for section %s" % expected.name)

    def test_symbols(self):

        fname, arch, target = ('nc.i64', 'i386', 'elf64-x86-64')
        odb_file = self.helper_import_idb(fname, arch, target)

        expectedSymbols = (
            (0x00401360, ".init_proc", 't'),
            (0x00401360, ".init", 't'),
            (0x00401380, "sub_00401380", 't'),
            (0x00401380, ".plt", 't'),
            (0x00401390, "inet_ntop", 'U'),
            (0x004013a0, "arc4random", 'U'),
            (0x004013b0, "__snprintf_chk", 'U'),
            (0x004013c0, "strcasecmp", 'U'),
            (0x004013d0, "__errno_location", 'U'),
            (0x004013e0, "unlink", 'U'),
            (0x004013f0, "warn", 'U'),
            (0x00401400, "__read_chk", 'U'),
            (0x00401410, "setsockopt", 'U'),
            (0x00401420, "strtonum", 'U'),
            (0x00401430, "fcntl", 'U'),
            (0x00401440, "write", 'U'),
            (0x00401450, "shutdown", 'U'),
            (0x00401460, "strlen", 'U'),
            (0x00401470, "__stack_chk_fail", 'U'),
            (0x00401480, "errx", 'U'),
            (0x00401490, "strchr", 'U'),
            (0x004014a0, "__fdelt_chk", 'U'),
            (0x004014b0, "gai_strerror", 'U'),
            (0x004014c0, "getservbyname", 'U'),
            (0x004014d0, "__poll_chk", 'U'),
            (0x004014e0, "alarm", 'U'),
            (0x004014f0, "readpassphrase", 'U'),
            (0x00401500, "close", 'U'),
            (0x00401510, "__strdup", 'U'),
            (0x00401520, "strcspn", 'U'),
            (0x00401530, "read", 'U'),
            (0x00401540, "__libc_start_main", 'U'),
            (0x00401550, "getsockopt", 'U'),
            (0x00401560, "calloc", 'U'),
            (0x00401570, "strcmp", 'U'),
            (0x00401580, "signal", 'U'),
            (0x00401590, "__memcpy_chk", 'U'),
            (0x004015a0, "__gmon_start__", 'U'),
            (0x004015b0, "strtol", 'U'),
            (0x004015c0, "strlcpy", 'U'),
            (0x004015d0, "memcpy", 'U'),
            (0x004015e0, "fileno", 'U'),
            (0x004015f0, "select", 'U'),
            (0x00401600, "err", 'U'),
            (0x00401610, "__recvfrom_chk", 'U'),
            (0x00401620, "listen", 'U'),
            (0x00401630, "mkstemp", 'U'),
            (0x00401640, "poll", 'U'),
            (0x00401650, "bind", 'U'),
            (0x00401660, "getopt", 'U'),
            (0x00401670, "__b64_ntop", 'U'),
            (0x00401680, "accept", 'U'),
            (0x00401690, "exit", 'U'),
            (0x004016a0, "connect", 'U'),
            (0x004016b0, "fwrite", 'U'),
            (0x004016c0, "__fprintf_chk", 'U'),
            (0x004016d0, "getservbyport", 'U'),
            (0x004016e0, "getaddrinfo", 'U'),
            (0x004016f0, "strerror", 'U'),
            (0x00401700, "sleep", 'U'),
            (0x00401710, "freeaddrinfo", 'U'),
            (0x00401720, "socket", 'U'),
            (0x00401730, "main", 't'),
            (0x00401730, ".text", 't'),
            (0x004026ac, "start", 't'),
            (0x004026e0, "sub_004026e0", 't'),
            (0x00402710, "sub_00402710", 't'),
            (0x00402750, "sub_00402750", 't'),
            (0x00402770, "sub_00402770", 't'),
            (0x004027a0, "handler", 't'),
            (0x004027b0, "sub_004027b0", 't'),
            (0x004028e0, "sub_004028e0", 't'),
            (0x00402a70, "sub_00402a70", 't'),
            (0x00402c40, "sub_00402c40", 't'),
            (0x00402d30, "sub_00402d30", 't'),
            (0x00403020, "sub_00403020", 't'),
            (0x00403290, "sub_00403290", 't'),
            (0x00403360, "sub_00403360", 't'),
            (0x00403500, "sub_00403500", 't'),
            (0x00403640, "sub_00403640", 't'),
            (0x00403a80, "sub_00403a80", 't'),
            (0x00403af0, "sub_00403af0", 't'),
            (0x00403b60, "sub_00403b60", 't'),
            (0x00403bb0, "sub_00403bb0", 't'),
            (0x00403c90, "sub_00403c90", 't'),
            (0x00403d20, "sub_00403d20", 't'),
            (0x00403e20, "sub_00403e20", 't'),
            (0x004047d0, "init", 't'),
            (0x00404860, "fini", 't'),
            (0x00404864, ".term_proc", 't'),
            (0x00404864, ".fini", 't'),
            (0x00404880, ".rodata", 'r'),
            (0x00405cb8, ".eh_frame_hdr", 'r'),
            (0x00606df0, ".init_array", 't'),
            (0x00606df8, ".fini_array", 't'),
            (0x00606e00, ".jcr", 'd'),
            (0x00606ff8, ".got", 'd'),
            (0x00607000, ".got.plt", 'd'),
            (0x006071e8, ".data", 'd'),
            (0x00607200, ".bss", 'b'),
        )

        actualSymbols = sorted(odb_file.get_structure_list(Symbol),
                                key=lambda s: s.vma)

        self.assertEqual(len(expectedSymbols), len(actualSymbols))

        for expected,actual in zip(expectedSymbols, actualSymbols):
            self.assertEqual(expected[0], actual.vma)
            self.assertEqual(expected[1], actual.name)
            self.assertEqual(expected[2], actual.type)

