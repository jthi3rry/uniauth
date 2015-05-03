# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import unittest
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError
from mock import patch
from . import mocks


class OAuth2ProviderTest(unittest.TestCase):

    def test_name(self):
        provider = mocks.MockOAuth2Provider(**mocks.OAUTH2_CREDENTIALS)
        self.assertEqual('mockoauth2provider', provider.name)
        self.assertEqual('Mock OAuth2 Provider', provider.verbose_name)
        self.assertEqual('Mock OAuth2 Provider', str(provider))

    def test_get_token(self):
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_VALID_TOKEN_DICT, **mocks.OAUTH2_CREDENTIALS)
        self.assertDictEqual(mocks.OAUTH2_VALID_TOKEN_DICT, provider.get_token())

    def test_get_authorization_url(self):
        provider = mocks.MockOAuth2Provider(**mocks.OAUTH2_CREDENTIALS)
        authorization_url = provider.get_authorization_url('https://example.org/callback', 'nonce')
        self.assertEqual(mocks.OAUTH2_GET_AUTHORIZATION_URL_EXPECTED_RESULT, authorization_url)

    @mocks.patch_responses(mocks.OAUTH2_EXCHANGE_TOKEN_RESPONSE_1)
    def test_exchange_token_with_expires_at(self, responses):
        provider = mocks.MockOAuth2Provider(**mocks.OAUTH2_CREDENTIALS)
        token = provider.get_access_token('https://example.org/callback', 'nonce', 'https://example.org/callback?code=code&state=nonce')
        self.assertDictEqual(mocks.OAUTH2_EXCHANGE_TOKEN_EXPECTED_RESULT, token)

        request = responses.calls[0].request
        self.assertEqual(responses.POST, request.method)
        self.assertEqual(mocks.OAUTH2_EXCHANGE_TOKEN_EXPECTED_CONTENT_TYPE, request.headers['content-type'])
        self.assertEqual(mocks.OAUTH2_EXCHANGE_TOKEN_EXPECTED_BODY, request.body)

    @mocks.patch_responses(mocks.OAUTH2_EXCHANGE_TOKEN_RESPONSE_2)
    def test_exchange_token_with_expires_in(self, responses):
        provider = mocks.MockOAuth2Provider(**mocks.OAUTH2_CREDENTIALS)
        token = provider.get_access_token('https://example.org/callback', 'nonce', 'https://example.org/callback?code=code&state=nonce')
        expected = mocks.OAUTH2_EXCHANGE_TOKEN_EXPECTED_RESULT.copy()
        token_expires_at = token.pop('expires_at')
        expected_expires_at = expected.pop('expires_at')
        self.assertDictEqual(expected, token)
        # delta less than 5 seconds (very large epsilon)
        self.assertLess((token_expires_at - expected_expires_at).total_seconds(), 5)

    @mocks.patch_responses(mocks.OAUTH2_REFRESH_TOKEN_RESPONSE)
    def test_refresh_token(self, responses):
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_EXPIRED_TOKEN_DICT, **mocks.OAUTH2_CREDENTIALS)
        token = provider.refresh_token()
        self.assertDictEqual(mocks.OAUTH2_REFRESH_TOKEN_EXPECTED_RESULT, token)

        request = responses.calls[0].request
        self.assertEqual(mocks.OAUTH2_REFRESH_TOKEN_EXPECTED_CONTENT_TYPE, request.headers['content-type'])
        self.assertEqual(mocks.OAUTH2_REFRESH_TOKEN_EXPECTED_BODY, request.body)

    @mocks.patch_responses(mocks.OAUTH2_REQUEST_RESPONSE)
    def test_request(self, responses):
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_VALID_TOKEN_DICT, **mocks.OAUTH2_CREDENTIALS)
        response = provider.request('https://example.org/profile')
        self.assertDictEqual(mocks.OAUTH2_REQUEST_EXPECTED_RESULT, response.json())

        request = responses.calls[0].request
        self.assertEqual(mocks.OAUTH2_REQUEST_EXPECTED_AUTHORIZATION, request.headers['Authorization'])

    @mocks.patch_responses(mocks.OAUTH2_REFRESH_TOKEN_RESPONSE, mocks.OAUTH2_REQUEST_RESPONSE)
    def test_request_refreshes_expired_token(self, responses):
        test_token = lambda token: self.assertDictEqual(mocks.OAUTH2_VALID_TOKEN_DICT, token)
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_EXPIRED_TOKEN_DICT, refresh_token_callback=test_token, **mocks.OAUTH2_CREDENTIALS)
        response = provider.request('https://example.org/profile')
        self.assertDictEqual(mocks.OAUTH2_REQUEST_EXPECTED_RESULT, response.json())

    def test_request_disable_auto_refresh(self):
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_EXPIRED_TOKEN_DICT, **mocks.OAUTH2_CREDENTIALS)
        with self.assertRaises(TokenExpiredError):
            provider.request('https://example.org/profile', auto_refresh_token=False)

    @mocks.patch_responses(mocks.OAUTH2_REFRESH_TOKEN_RESPONSE, mocks.OAUTH2_REQUEST_RESPONSE)
    def test_request_refresh_callback_via_arg(self, responses):
        test_token = lambda token: self.assertDictEqual(mocks.OAUTH2_VALID_TOKEN_DICT, token)
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_EXPIRED_TOKEN_DICT, **mocks.OAUTH2_CREDENTIALS)
        response = provider.request('https://example.org/profile', refresh_token_callback=test_token)
        self.assertDictEqual(mocks.OAUTH2_REQUEST_EXPECTED_RESULT, response.json())

    @mocks.patch_responses(mocks.OAUTH2_REFRESH_TOKEN_RESPONSE, mocks.OAUTH2_REQUEST_RESPONSE)
    def test_get_profile(self, responses):
        provider = mocks.MockOAuth2Provider(token=mocks.OAUTH2_VALID_TOKEN_DICT, **mocks.OAUTH2_CREDENTIALS)
        self.assertDictEqual(mocks.OAUTH2_GET_PROFILE_EXPECTED_RESULT, provider.get_profile())

    @patch('uniauth.oauth2.generate_token')
    @mocks.patch_responses(mocks.OAUTH2_EXCHANGE_TOKEN_RESPONSE_1)
    def test_oauth2_dance(self, generate_token, responses):
        generate_token.return_value = "nonce"
        provider = mocks.MockOAuth2Provider(**mocks.OAUTH2_CREDENTIALS)
        dance = provider.dance({}, 'https://example.org/callback')
        authorization_url = dance.get_authorization_url()
        self.assertEqual(mocks.OAUTH2_GET_AUTHORIZATION_URL_EXPECTED_RESULT, authorization_url)
        token = dance.get_access_token('https://example.org/callback?code=code&state=nonce')
        self.assertDictEqual(mocks.OAUTH2_EXCHANGE_TOKEN_EXPECTED_RESULT, token)
