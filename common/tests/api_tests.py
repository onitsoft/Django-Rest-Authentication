import json


import requests
from django.contrib.staticfiles import finders
from django.test import LiveServerTestCase
from provider.oauth2.models import Client, AccessToken, RefreshToken
from profiles.models import User


class APITest(LiveServerTestCase):
    """
    Test case for the API endpoints
    """

    def setUp(self):
        self.base_url = self.live_server_url

        self.user = User.objects.create_user(
            email='user@example.com', password='test')

        self.auth = ('user@example.com', 'test')

    def assertResponseStatus(self, res, status_code):
        """
        Assert that the response status matches.
        """

        self.assertEquals(
            res.status_code, status_code,
            'Bad status, response: {}, status={}, expected={}'.format(
                res.content, res.status_code, status_code)
        )

    def assertResponseOk(self, res):
        self.assertResponseStatus(res, 200)

    def assertResponseCreated(self, res):
        self.assertResponseStatus(res, 201)

    def assertResponseDeleted(self, res):
        self.assertResponseStatus(res, 204)

    def assertResponseBadRequest(self, res):
        self.assertResponseStatus(res, 400)

    def assertResponseUnauthorized(self, res):
        self.assertResponseStatus(res, 401)

    def assertResponseForbidden(self, res):
        self.assertResponseStatus(res, 403)

    def assertResponseNotFound(self, res):
        self.assertResponseStatus(res, 404)

    def assertResponseMethodNotAllowed(self, res):
        self.assertResponseStatus(res, 405)


class AuthenticationTestCase(APITest):
    """Testing the Authentication process"""

    def test_auth_required(self):
        url = self.base_url + '/users/me/'
        res = requests.get(url)

        self.assertResponseUnauthorized(res)

    def _create_oauth2_client(self):
        self.oauth2_client = Client.objects.create(client_type=0)

    def test_oauth2_get_token_fail(self):
        url = self.base_url + '/oauth2/access_token/'
        self._create_oauth2_client()

        res = requests.post(url, data={
            'client_id': self.oauth2_client.client_id,
            'client_secret': self.oauth2_client.client_secret,
            'username': self.user.email,
            'password': 'bad_password',
            'grant_type': 'password',
        })

        self.assertResponseBadRequest(res)
        self.assertEquals(res.json()['error'], 'invalid_grant')

    def test_oauth2_get_token(self):
        url = self.base_url + '/oauth2/access_token/'

        self._create_oauth2_client()

        res = requests.post(url, data={
            'client_id': self.oauth2_client.client_id,
            'client_secret': self.oauth2_client.client_secret,
            'username': self.user.email,
            'password': 'test',
            'grant_type': 'password',
        })

        self.assertResponseOk(res)
        data = res.json()

        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_oauth2_token_authentication(self):
        self._create_oauth2_client()

        token = AccessToken.objects.create(client=self.oauth2_client, user=self.user)
        headers = {'Authorization': 'Bearer ' + token.token}

        url = self.base_url + '/users/me/'
        res = requests.get(url, headers=headers)

        self.assertResponseOk(res)

    def test_oauth2_token_refresh(self):
        self._create_oauth2_client()

        token = AccessToken.objects.create(client=self.oauth2_client, user=self.user)
        refresh_token = RefreshToken.objects.create(client=self.oauth2_client,
                                                    access_token=token,
                                                    user=self.user)

        url = self.base_url + '/oauth2/access_token/'
        res = requests.post(url, data={
            'client_id': self.oauth2_client.client_id,
            'client_secret': self.oauth2_client.client_secret,
            'refresh_token': refresh_token.token,
            'grant_type': 'refresh_token',
        })

        self.assertResponseOk(res)
        data = res.json()
        self.assertIn('access_token', data)
        self.assertIn('refresh_token', data)

    def test_web_login_sets_cookie(self):
        url = self.base_url + '/login'
        res = requests.post(url, data={
            'email': self.user.email,
            'password': 'test',
        })

        self.assertResponseOk(res)
        self.assertIn('sessionid', res.cookies)

        cookies = res.cookies

        url = self.base_url + '/users/me'
        res = requests.get(url, cookies=cookies)

        self.assertResponseOk(res)

    def test_web_login_email_case_insensetive(self):
        url = self.base_url + '/login'
        res = requests.post(url, data={
            'email': self.user.email.upper(),
            'password': 'test',
        })

        self.assertResponseOk(res)

    def test_web_login_twice_fails(self):
        url = self.base_url + '/login'
        data = {
            'email': self.user.email,
            'password': 'test',
        }

        res = requests.post(url, data=data)
        self.assertResponseOk(res)

        cookies = res.cookies

        res = requests.post(url, data=data, cookies=cookies)

        self.assertResponseBadRequest(res)

    def test_web_login_bad_cred(self):
        url = self.base_url + '/login'
        data = {
            'email': self.user.email,
            'password': 'wrongpass',
        }

        res = requests.post(url, data=data)
        self.assertResponseBadRequest(res)

    def test_web_logout(self):
        url = self.base_url + '/login'
        data = {
            'email': self.user.email,
            'password': 'test',
        }

        res = requests.post(url, data=data)
        self.assertResponseOk(res)

        cookies = res.cookies

        url = self.base_url + '/logout'
        res = requests.get(url, cookies=cookies)

        self.assertResponseOk(res)

        url = self.base_url + '/users/me'
        res = requests.get(url, cookies=cookies)

        self.assertResponseUnauthorized(res)


class GenericAPITestCase(APITest):
    def test_api_root_ok(self):
        res = requests.get(self.base_url)
        self.assertResponseOk(res)

    def test_ie_content_type_setting(self):
        res = requests.get(self.base_url, headers={
            # 'Accept': 'text/plain',
            'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0)',
        })

        self.assertResponseOk(res)
        self.assertEquals(res.headers['content-type'], 'text/plain')


    def test_version_check_no_version(self):
        """Endpoint works without a 'version' object to test agains"""
        res = requests.post(self.base_url + '/check_version', data={
            'device_type': 'android',
            'version': '1.7',
        })
        self.assertResponseOk(res)
        data = res.json()
        self.assertEquals(data['result'], 'UP_TO_DATE')

    def test_version_check_bad_request(self):
        res = requests.post(self.base_url + '/check_version', data={})
        self.assertResponseBadRequest(res)


    def test_add_company_location_forbidden(self):
        data = {'name': 'testlocation'}
        url = '{}{}/locations'.format(self.base_url, self.company.pk)

        res = requests.post(url, data=data, auth=self.auth)

        self.assertResponseForbidden(res)

    def test_add_company_location_success(self):
        data = {'name': 'testlocation', 'country': 'IL', 'is_main_location': True}
        url = '{}{}/locations'.format(self.base_url, self.company.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)

        res = requests.post(url, data=data, auth=self.auth)

        self.assertResponseCreated(res)
        data = res.json()
        self.assertEquals(data['is_main_location'], True)
        self.assertEquals(data['country_name'], 'Israel')

    def test_update_company_location_forbidden(self):
        data = {'name': 'testlocation'}
        location = Location.objects.create(name='test')
        CompanyLocation.objects.create(company=self.company, location=location)

        url = '{}{}/locations/{}'.format(self.base_url, self.company.pk, location.pk)

        res = requests.patch(url, data=data, auth=self.auth)

        self.assertResponseForbidden(res)

    def test_update_company_location_success(self):
        data = {'name': 'testlocation'}
        location = Location.objects.create(name='test')
        CompanyLocation.objects.create(company=self.company, location=location)

        url = '{}{}/locations/{}'.format(self.base_url, self.company.pk, location.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)
        res = requests.patch(url, data=data, auth=self.auth)

        self.assertResponseOk(res)

    def test_delete_company_location(self):
        data = {'name': 'testdep'}
        location = Location.objects.create(name='test')
        CompanyLocation.objects.create(company=self.company, location=location)

        url = '{}{}/locations/{}'.format(self.base_url, self.company.pk, location.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)
        res = requests.delete(url, data=data, auth=self.auth)

        self.assertResponseDeleted(res)
        location = self.company.locations.get(name='test')
        self.assertEquals(location.is_active, False)

    def test_add_company_department_success(self):
        data = {'name': 'testdep'}
        url = '{}{}/departments'.format(self.base_url, self.company.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)

        res = requests.post(url, data=data, auth=self.auth)

        self.assertResponseCreated(res)

    def test_update_company_department_success(self):
        data = {'name': 'testdep'}
        department = self.company.departments.create(name='test')
        url = '{}{}/departments/{}'.format(self.base_url, self.company.pk, department.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)

        res = requests.patch(url, data=data, auth=self.auth)

        self.assertResponseOk(res)

    def test_delete_company_department(self):
        data = {'name': 'testdep'}
        department = self.company.departments.create(name='test')
        url = '{}{}/departments/{}'.format(self.base_url, self.company.pk, department.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)

        res = requests.delete(url, data=data, auth=self.auth)

        self.assertResponseDeleted(res)
        department = self.company.departments.get(name='test')
        self.assertEquals(department.status, department.Status.DELETED)

    def test_list_company_roles_unauthorized(self):
        url = '{}{}/roles'.format(self.base_url, self.company.pk)
        res = requests.get(url)

        self.assertResponseUnauthorized(res)

    def test_list_company_roles_forbidden(self):
        url = '{}{}/roles'.format(self.base_url, self.company.pk)
        res = requests.get(url, auth=self.auth)

        self.assertResponseForbidden(res)

    def test_list_company_roles_success(self):
        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)

        url = '{}{}/roles'.format(self.base_url, self.company.pk)
        res = requests.get(url, auth=self.auth)

        self.assertResponseOk(res)
        data = res.json()
        self.assertEquals(len(data), 1)
        self.assertEquals(data[0]['user']['email'], self.user.email)
        self.assertEquals(data[0]['role_type'], Role.RoleType.ADMIN)
        self.assertIn('stats', data[0])
        self.assertIn('applicants_count', data[0]['stats'])
        self.assertIn('view_count', data[0]['stats'])

    def test_update_company_role_success(self):
        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)

        user2 = User.objects.create(email='other@example.com')
        role = user2.roles.create(company=self.company, role_type=Role.RoleType.SCOUTER)

        data = {
            'role_type': Role.RoleType.RECRUITER,  # promote
            'is_active': False,  # disable
        }
        url = '{}{}/roles/{}'.format(self.base_url, self.company.pk, role.pk)
        res = requests.patch(url, data=json.dumps(data), auth=self.auth,
                             headers={'content-type': 'application/json'})

        self.assertResponseOk(res)
        data = res.json()
        self.assertEquals(data['is_active'], False)
        self.assertEquals(data['role_type'], Role.RoleType.RECRUITER)

    def test_list_company_images(self):
        self.company.company_images.create()

        url = '{}{}/images'.format(self.base_url, self.company.pk)

        res = requests.get(url)

        self.assertResponseOk(res)

        data = res.json()
        self.assertEquals(len(data), 1)

    def test_create_image_forbidden(self):
        url = '{}{}/images'.format(self.base_url, self.company.pk)

        res = requests.post(url, auth=self.auth)

        self.assertResponseForbidden(res)

    def test_create_image_success(self):
        url = '{}{}/images'.format(self.base_url, self.company.pk)

        self.user.roles.create(company=self.company, role_type=Role.RoleType.ADMIN)
        filename = finders.find('admin/img/icon_changelink.gif')
        with open(filename, 'rb') as f:
            res = requests.post(url, auth=self.auth,
                                data={'description': 'test'}, files={'image': f})

        self.assertResponseCreated(res)

