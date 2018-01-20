import json
from django.db import models


class BinaryOptions(models.Model):
    """ Options that specify how the associated Binary is to be treated """
    target = models.CharField(max_length=128)
    architecture = models.CharField(max_length=128)
    extra_options = models.CharField(max_length=256, default='{"flags" : [] }')
    base_address = models.CharField(max_length=18)

    def get_options_map(self):
        return json.loads(self.extra_options)

    def get_extra_options(self):
        return self.get_options_map()["flags"]

    def set_extra_options(self, options):
        o = self.get_options_map()
        o["flags"] = options
        self.extra_options = json.dumps(o)

    def reset_extra_options(self):
        self.extra_options = '{ "flags" : [] }'

    def get_endian(self):
        options = self.get_extra_options()
        endian = 'DEFAULT'
        if 'LITTLE' in options:
            endian = 'LITTLE'
        elif 'BIG' in options:
            endian = 'BIG'

        return endian

    def set_endian(self, endian):
        o = self.get_options_map()
        o["endian"] = endian
        self.extra_options = json.dumps(o)
