from abc import ABC, abstractstaticmethod, abstractmethod
import logging
from datetime import datetime
from oda.apps.odaweb.models.oda_user import OdaUser
from oda.apps.odaweb.middleware import get_current_user

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    def __init__(self, message, code=None, params=None):
        self.message = message

class Validator(object):
    def validate(self, odb_file):
        return True


class Operation(ABC):
    def __init__(self, validators=[], odaUser=None):
        self.validators = validators
        self.datetime = datetime.now()
        self.opname = self.__class__.__name__

        self.user_id = None
        if odaUser:
            self.user_id = odaUser.id
        else:
            user = get_current_user()
            if user:
                self.user_id = user.id

    @staticmethod
    def deserialize(op, d):
        """Deserialize the operation"""
        op.object_id = d['object_id']
        op.user_id = d['user_id']
        op.datetime = d['datetime']

    def serialize(self):
        """Serialize the operation"""
        d = {
            'object_id': self.object_id,
            'user_id': self.user_id,
            'datetime': self.datetime,
        }
        return d

    @property
    def user(self):
        user = None
        try:
            user = OdaUser.objects.get(id=self.user_id)
        except Exception as e:
            logger.error("Failed to lookup user id %s: %s" % (self.user_id, e))

        return user

    @property
    def desc(self):
        return str(self)

    def validate(self, odb_file):
        for validator in self.validators:
            validator.validate(self, odb_file)

    def operate(self, odb_file):
        pass

    def undo(self, odb_file):
        """Naive undo that should be overridden by more complex operations"""
        if odb_file.operations[-1] != self:
            raise Exception("You can only undo the last function applied")
        odb_file.operations.pop()
        odb_file.remove_item(self.item)
