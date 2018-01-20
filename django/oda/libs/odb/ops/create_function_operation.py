import logging
from oda.libs.odb.ops.operation import Validator, ValidationError

from oda.libs.odb.ops.operation import Operation
from oda.libs.odb.structures.function import Function
from oda.libs.odb.structures.symbol import Symbol

logger = logging.getLogger(__name__)

class DupNameValidator(Validator):
    def validate(self, operation, odb_file):
        v = next((f for f in odb_file.get_structure_list(Function) if f.name == operation.name), None)
        if v is not None:
            raise ValidationError('Cannot Use Duplicate Function Name')

class DupVmaValidator(Validator):
    def validate(self, operation, odb_file):
        v = next((f for f in odb_file.get_structure_list(Function) if f.vma ==
                  operation.vma), None)
        if v is not None:
            raise ValidationError('Function already exists at address 0x%x' %
                                  operation.vma)

class CreateFunctionOperation(Operation):

    def __init__(self, vma, name, args="", retval="", sym_type="t"):
        super().__init__(validators=[DupNameValidator(), DupVmaValidator()])
        self.object_id = -1
        self.name = name
        self.vma = vma
        self.args = args
        self.retval = retval
        self.sym_type = sym_type

    @staticmethod
    def deserialize(d):
        op = CreateFunctionOperation(vma=d['vma'],
                                     name=d['name'],
                                     args=d['args'],
                                     retval=d['retval'],
                                     sym_type=d['sym_type'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
            'name': self.name,
            'args': self.args,
            'retval': self.retval,
            'sym_type': self.sym_type,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):

        # TODO: Verify that the given address is already code
        # TODO: Verify that the given function name does not already exist

        self.object_id = odb_file.get_object_id()

        func = odb_file.create_item(Function, {
            'name': self.name,
            'vma': self.vma,
            'sym_type': self.sym_type,
            'xrefs': set([]),
            'retval': self.retval,
            'args': self.args,
        })

        odb_file.insert_item(func)

        symbols = {sym.vma: sym for sym in odb_file.get_structure_list(Symbol)}
        if self.vma not in symbols.keys():
            odb_file.insert_item(odb_file.create_item(Symbol, {
                'name': func.name,
                'vma': func.vma,
                'base': 0,
                'sym_type': self.sym_type,
                'value': func.vma,
                'xrefs': set([])
            }))

        self.item = func

    def __str__(self):
        return "Created function '%s' at address 0x%x" % (self.name,
                                                          self.vma)

class EditFunctionOperation(Operation):

    def __init__(self, vma, name, args, retval):
        super(EditFunctionOperation, self).__init__()
        self.object_id = -1
        self.name = name
        self.vma = vma
        self.args = args
        self.retval = retval

    @staticmethod
    def deserialize(d):
        op = EditFunctionOperation(vma=d['vma'],
                                   name=d['name'],
                                   args=d['args'],
                                   retval=d['retval'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
            'name': self.name,
            'args': self.args,
            'retval': self.retval,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):
        self.object_id = odb_file.get_object_id()

        functions = {f.vma: f for f in odb_file.get_structure_list(Function)}
        symbols = {sym.vma: sym for sym in odb_file.get_structure_list(Symbol)}

        if (self.vma in functions.keys()):
            f = functions[self.vma]
            s = symbols[self.vma]

            if self.name != None:
                f.name = self.name
                s.name = self.name

            if self.args != None:
                f.args = self.args

            if self.retval != None:
                f.retval = self.retval
        else:
            raise Exception("Cannot edit a function that does not already exist!")

    def __str__(self):
        return "Edited function '%s' at address 0x%x" % (self.name, self.vma)

class DeleteFunctionOperation(Operation):

    def __init__(self, vma):
        super(DeleteFunctionOperation, self).__init__()
        self.object_id = -1
        self.vma = vma

    @staticmethod
    def deserialize(d):
        op = DeleteFunctionOperation(vma=d['vma'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'vma': self.vma,
        }
        d.update(super().serialize())
        return d

    def operate(self, odb_file):
        functions = {f.vma: f for f in odb_file.get_structure_list(Function)}
        symbols = {sym.vma: sym for sym in odb_file.get_structure_list(Symbol)}

        if (self.vma in functions.keys()):
            odb_file.remove_item(functions[self.vma])
            odb_file.remove_item(symbols[self.vma])
        else:
            raise Exception("Cannot delete a function that does not already exist!")

    def __str__(self):
        return "Deleted function at address 0x%x" % (self.vma)
