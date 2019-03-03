from rest_framework import status
from django.contrib.auth.models import Group, Permission

from oda.apps.odaweb.models import OdaUser, OdaMaster
from oda.apps.odaweb.models.oda_master import OdaMasterPermission
from oda.test.oda_test_case import OdaApiTestCase

class PermissionsUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_permission_create_user(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()

        response = self.client.post(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'username':   'otheruser',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permission_create_group(self):
        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)

        response = self.client.post(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'usergroup': 'mygroup',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_permission_delete_user(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()

        oda_master = OdaMaster.get_by_short_name('mkdir')
        perm = Permission.objects.get(codename='read_odamaster')

        OdaMasterPermission.objects.create(master=oda_master, user=otheruser, permission=perm)

        response = self.client.delete(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'username': 'otheruser',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_permission_delete_group(self):
        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)

        oda_master = OdaMaster.get_by_short_name('mkdir')
        perm = Permission.objects.get(codename='read_odamaster')

        OdaMasterPermission.objects.create(master=oda_master, group=group, permission=perm)

        response = self.client.delete(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'usergroup': 'mygroup',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_list_permissions(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()

        oda_master = OdaMaster.get_by_short_name('mkdir')
        perm = Permission.objects.get(codename='read_odamaster')

        OdaMasterPermission.objects.create(master=oda_master, user=otheruser, permission=perm)

        response = self.client.get('/odaapi/api/masters/mkdir/permissions/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]['username'], 'otheruser')
        self.assertEqual(response.data[0]['permission'], 'read')

    def test_list_permissions_on_oda_master(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()

        oda_master = OdaMaster.get_by_short_name('mkdir')
        perm = Permission.objects.get(codename='read_odamaster')

        OdaMasterPermission.objects.create(master=oda_master, user=otheruser, permission=perm)

        response = self.client.get('/odaapi/api/masters/mkdir/', format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['permissions'][0]['username'], 'otheruser')
        self.assertEqual(response.data['permissions'][0]['permission'], 'read')

    def test_bad_oda_master(self):
        response = self.client.post(
            '/odaapi/api/masters/does_not_exist/permission/',
            {
                'username':   'otheruser',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('missing', response.data['detail'])

    def test_missing_user(self):
        response = self.client.post(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'username':   'does_not_exist',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('User', response.data['detail'])

    def test_missing_group(self):
        response = self.client.post(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'usergroup':   'does_not_exist',
                'permission': 'read',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Group', response.data['detail'])

    def test_missing_permission(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()

        response = self.client.post(
            '/odaapi/api/masters/mkdir/permission/',
            {
                'username':   'otheruser',
                'permission': 'does_not_exist',
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Permission', response.data['detail'])
