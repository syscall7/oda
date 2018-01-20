from oda.libs.odb.ops.load_operation import LoadOperation
from oda.libs.odb.ops.operation import Operation

__author__ = 'davis'


class ModifySettingsFactory(object):
    @staticmethod
    def set_architecture(arch):
        return ModifySettingsOperation({'architecture': arch})

    @staticmethod
    def set_base_address(base_address):
        return ModifySettingsOperation({'base_address': base_address})

    @staticmethod
    def set_endian(endian):
        return ModifySettingsOperation({'endian': endian})

    @staticmethod
    def set_values(values):
        return ModifySettingsOperation(values)



class ModifySettingsOperation(Operation):

    def __init__(self, options):
        super(ModifySettingsOperation, self).__init__()

        self.object_id = -1

        self.options = options

    @staticmethod
    def deserialize(d):
        op = ModifySettingsOperation(d['options'])
        Operation.deserialize(op, d)
        return op

    def serialize(self):
        d = {
            'options': self.options,
        }
        d.update(super().serialize())
        return d

    def __str__(self):
        return "Modified settings"

    def operate(self, odb_file):
        self.object_id = odb_file.get_object_id()

        options = odb_file.get_binary().options

        if self.options.get('architecture'):
            options.architecture = self.options.get('architecture')

        if self.options.get('base_address'):
            options.base_address = self.options.get('base_address')

        if self.options.get('endian'):
            options.endian = self.options.get('endian')

        if self.options.get('selected_opts'):
            options.selected_opts = self.options.get('selected_opts')

        odb_file.get_binary().options = options