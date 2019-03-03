from rest_framework import status
from django.contrib.auth.models import Group

from oda.apps.odaweb.models import OdaUser
from oda.test.oda_test_case import OdaApiTestCase

class UserGroupsUnitTest(OdaApiTestCase):
    urls = 'oda.urls'

    def test_simple_create(self):
        response = self.client.post(
            '/odaapi/api/usergroups/',
            {'name': 'mygroup'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], 'mygroup')
        self.assertEqual(response.data['users'][0]['username'], self.TEST_USERNAME)

    def test_duplicate_create(self):
        response = self.client.post(
            '/odaapi/api/usergroups/',
            {'name': 'mygroup'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post(
            '/odaapi/api/usergroups/',
            {'name': 'mygroup'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


    def test_get_list(self):
        response = self.client.get(
            '/odaapi/api/usergroups/',
            format='json'
        )
        self.assertEqual(response.data, [])

        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)

        response = self.client.get(
            '/odaapi/api/usergroups/',
            format='json'
        )
        self.assertEqual(response.data[0]['name'], 'mygroup')

        otheruser = OdaUser(username='otheruser')
        otheruser.save()
        othergroup = Group.objects.create(name='othergroup')
        otheruser.groups.add(othergroup)

        response = self.client.get(
            '/odaapi/api/usergroups/',
            format='json'
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'mygroup')

    def test_get_detail(self):
        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)

        response = self.client.get(
            '/odaapi/api/usergroups/' + str(group.pk) + '/',
            format='json'
        )
        self.assertEqual(response.data['name'], 'mygroup')

    def test_get_detail_non_owner(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()
        othergroup = Group.objects.create(name='othergroup')
        otheruser.groups.add(othergroup)

        response = self.client.get(
            '/odaapi/api/usergroups/' + str(othergroup.pk) + '/',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)

        response = self.client.put(
            '/odaapi/api/usergroups/' + str(group.pk) + '/',
            {'name': 'mygroup2'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'mygroup2')

    def test_update_non_owner(self):
        otheruser = OdaUser(username='otheruser')
        otheruser.save()
        othergroup = Group.objects.create(name='othergroup')
        otheruser.groups.add(othergroup)

        response = self.client.put(
            '/odaapi/api/usergroups/' + str(othergroup.pk) + '/',
            {'name': 'mygroup2'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_add(self):
        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)

        response = self.client.get(
            '/odaapi/api/usergroups/' + str(group.pk) + '/',
            format='json'
        )
        self.assertEqual(response.data['name'], 'mygroup')
        self.assertEqual(response.data['users'][0]['username'], self.TEST_USERNAME)

        otheruser = OdaUser(username='otheruser')
        otheruser.save()

        response = self.client.post(
            '/odaapi/api/usergroups/' + str(group.pk) + '/user/',
            {'username': 'otheruser'},
            format='json'
        )
        self.assertEqual(response.data['users'][1]['username'], 'otheruser')

    def test_user_remove(self):
        group = Group.objects.create(name='mygroup')
        self.user.groups.add(group)
        otheruser = OdaUser(username='otheruser')
        otheruser.save()
        otheruser.groups.add(group)

        response = self.client.delete(
            '/odaapi/api/usergroups/' + str(group.pk) + '/user/',
            {'username': 'otheruser'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(
            '/odaapi/api/usergroups/' + str(group.pk) + '/',
            format='json'
        )
        self.assertEqual(len(response.data['users']), 1)
        self.assertEqual(response.data['users'][0]['username'], self.TEST_USERNAME)

    def test_user_add_non_owner(self):
        group = Group.objects.create(name='mygroup')
        otheruser = OdaUser(username='otheruser')
        otheruser.save()
        otheruser.groups.add(group)

        response = self.client.post(
            '/odaapi/api/usergroups/' + str(group.pk) + '/user/',
            {'username': self.TEST_USERNAME},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_user_remove_non_owner(self):
        group = Group.objects.create(name='mygroup')
        otheruser = OdaUser(username='otheruser')
        otheruser.save()
        otheruser.groups.add(group)

        response = self.client.delete(
            '/odaapi/api/usergroups/' + str(group.pk) + '/user/',
            {'username': self.TEST_USERNAME},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
