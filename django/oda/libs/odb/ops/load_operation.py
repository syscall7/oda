import re
import logging

from oda.libs.odb.disassembler import ofd
from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.section import Section
from oda.libs.odb.structures.parcel import CodeParcel, DataParcel
from oda.libs.odb.structures.symbol import Symbol
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.data_string import DataString
from oda.libs.odb.binaries import BinaryString

logger = logging.getLogger(__name__)


class LoadOperation(Operation):
    def __init__(self):
        super(LoadOperation, self).__init__()

        self.object_id = -1

    @staticmethod
    def deserialize(d):
        op = LoadOperation()
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):
        logger.info("Loading {}".format(odb_file))
        self.object_id = odb_file.get_object_id()

        analyzer = ofd.Ofd(odb_file.get_binary())

        loader = Loader(odb_file, analyzer)

        loader.load()

    def __str__(self):
        return "Loaded project"

class Loader(object):
    def __init__(self, odb_file, analyzer):
        self.odb_file = odb_file
        self.analyzer = analyzer

        # we treat ".data" as a code section for live mode
        if type(odb_file.binary) == BinaryString:
            self.treatAllAsCode = True
        else:
            self.treatAllAsCode = False

    def load(self):
        self.load_symbols()
        self.load_sections()
        self.load_functions()
        self.load_parcels()

        self.load_strings()


    def load_symbols(self):
        #Load Symbols
        for symbol in self.analyzer.symbols():
            # skip empty symbol names
            if symbol.name == '':
                continue
            self.odb_file.insert_item(self.odb_file.create_item(Symbol, {
                'name': symbol.name,
                'vma': symbol.value,
                'base': symbol.base,
                'sym_type': symbol.type,
                'value': symbol.value,
                'xrefs': set([])
            }))

    def load_sections(self):
        #Load Sections
        for section in self.analyzer.sections:
            self.odb_file.insert_item(self.odb_file.create_item(Section, {
                'name': section.name,
                'size': section.size,
                'vma': section.vma,
                'flags': section.flags
            }))

    def load_functions(self):
        funcs = filter(lambda x: x.value != 0 and x.type.lower() in ['t', 'u'],
                       self.analyzer.symbols())
        odb_funcs = [self.odb_file.create_item(Function, {
            'name': f.name,
            'vma': f.value,
            'sym_type': f.type,
            'xrefs': set([]),
            'retval': 'unknown',
            'args': 'unknown'
        }) for f in funcs]

        for f in odb_funcs:
            self.odb_file.insert_item(f)

    def load_parcels(self):
        for sec in self.analyzer.get_loadable_sections().sections:
            # don't make parcels for empty sections
            if sec.size == 0:
                continue

            is_code = self.analyzer.is_code_section(sec)

            if is_code or self.treatAllAsCode:
                class_type = CodeParcel
            else:
                class_type = DataParcel

            self.odb_file.insert_item(self.odb_file.create_item(class_type, {
                'vma_start': sec.vma,
                'vma_end': sec.vma + sec.size,
                'sec_name': sec.name
            }))

    def load_strings(self):
        for s in self.analyzer.get_loadable_sections().sections:
            #print('Section %s, base 0x%08x, size 0x%08x' % (s.name, s.vma, s.size))
            for m in re.finditer("([\t\x20-\x7e]{4,})", self.analyzer.bfd.raw_data(s, s.vma, s.size).decode('iso-8859-1')):

                self.odb_file.insert_item(self.odb_file.create_item(DataString, {
                    'addr': m.start()+s.vma,
                    'value': m.group(1)
                }))
