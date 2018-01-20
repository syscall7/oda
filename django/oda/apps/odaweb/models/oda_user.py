from django.contrib.auth.models import AbstractUser
from lazysignup.utils import is_lazy_user


class OdaUser(AbstractUser):

    def is_lazy_user(self):
        return is_lazy_user(self)

