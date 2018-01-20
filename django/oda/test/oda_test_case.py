import os
from django.test import TestCase
from rest_framework.test import APITestCase
from oda.apps.odaweb.management.commands.setup_oda import load_examples
from oda.apps.odaweb.models import OdaUser


class OdaApiTestCase(APITestCase):
    TEST_USERNAME = "APITEST"

    def setUp(self):
        self.user = OdaUser(username=self.TEST_USERNAME)
        self.user.save()
        load_examples(self.user)
        self.client.force_login(self.user)


class OdaLibTestCase(TestCase):
    def get_test_bin_path(self, relpath):
        cwd = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(cwd, 'test_binaries', relpath)
        return path
