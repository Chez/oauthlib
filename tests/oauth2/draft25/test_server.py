# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from ...unittest import TestCase
import mock
import sys

from oauthlib.oauth2 import draft25
from oauthlib.oauth2.draft25 import grant_types, tokens


if sys.version_info[0] == 3:
    from imp import reload


class AuthorizationEndpointTest(TestCase):

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def setUp(self):
        reload(grant_types)     # grant_types indirectly import common
        mock_validator = mock.MagicMock()
        auth_code = grant_types.AuthorizationCodeGrant(request_validator=mock_validator)
        auth_code.save_authorization_code = mock.MagicMock()
        implicit = grant_types.ImplicitGrant(request_validator=mock_validator)
        implicit.save_token = mock.MagicMock()
        response_types = {
                'code': auth_code,
                'token': implicit,
        }

        # TODO(ib-lundgren): Figure out where in the import order the monkey
        # patching of oauthlib.common.generate_token breaks.
        class MockToken(tokens.BearerToken):
            def __call__(self, request, refresh_token=False):
                token = super(MockToken, self).__call__(request,
                        refresh_token=refresh_token)
                token['access_token'] = 'abc'
                return token

        token = MockToken()
        token.save_token = mock.MagicMock()
        self.endpoint = draft25.AuthorizationEndpoint(
                default_token=token, response_types=response_types)

    def test_authorization_grant(self):
        uri = 'http://i.b/l?response_type=code&client_id=me&scope=all+of+them'
        uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
        uri, headers, body = self.endpoint.create_authorization_response(uri)
        self.assertURLEqual(uri, 'http://back.to/me?code=abc')

    def test_implicit_grant(self):
        uri = 'http://i.b/l?response_type=token&client_id=me&scope=all+of+them'
        uri += '&redirect_uri=http%3A%2F%2Fback.to%2Fme'
        uri, headers, body = self.endpoint.create_authorization_response(uri)
        self.assertURLEqual(uri, 'http://back.to/me#access_token=abc&expires_in=3600&token_type=Bearer', parse_fragment=True)

    def test_missing_type(self):
        pass

    def test_invalid_type(self):
        pass


class TokenEndpointTest(TestCase):

    @mock.patch('oauthlib.common.generate_token', new=lambda: 'abc')
    def setUp(self):
        reload(grant_types)     # grant_types indirectly import common
        mock_validator = mock.MagicMock()
        auth_code = grant_types.AuthorizationCodeGrant(request_validator=mock_validator)
        password = grant_types.ResourceOwnerPasswordCredentialsGrant(request_validator=mock_validator)
        client = grant_types.ClientCredentialsGrant(request_validator=mock_validator)
        supported_types = {
                'authorization_code': auth_code,
                'password': password,
                'client_credentials': client,
        }
        self.endpoint = draft25.TokenEndpoint(grant_types=supported_types)

    def test_authorization_grant(self):
        pass

    def test_password_grant(self):
        pass

    def test_client_grant(self):
        pass

    def test_missing_type(self):
        pass

    def test_invalid_type(self):
        pass


class ResourceEndpointTest(TestCase):

    def setUp(self):
        self.endpoint = draft25.ResourceEndpoint()

    def test_token_validation(self):
        pass

    def test_token_estimation(self):
        pass
