# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import unittest
from . import mocks


class OAuth1ProviderTest(unittest.TestCase):

    def test_name(self):
        provider = mocks.MockOAuth1Provider(**mocks.OAUTH1_CREDENTIALS)
        self.assertEqual('mockoauth1provider', provider.name)
        self.assertEqual('Mock OAuth1 Provider', provider.verbose_name)
        self.assertEqual('Mock OAuth1 Provider', str(provider))

    def test_get_token(self):
        provider = mocks.MockOAuth1Provider(token=mocks.OAUTH1_VALID_TOKEN_DICT, **mocks.OAUTH1_CREDENTIALS)
        self.assertDictEqual(mocks.OAUTH1_VALID_TOKEN_DICT, provider.get_token())

    @mocks.patch_responses(mocks.OAUTH1_REQUEST_TOKEN_RESPONSE_1)
    def test_get_request_token(self, responses):
        provider = mocks.MockOAuth1Provider(**mocks.OAUTH1_CREDENTIALS)
        request_token = provider.get_request_token('https://example.org/callback')
        self.assertEqual(mocks.OAUTH1_REQUEST_TOKEN, request_token)

    def test_get_authorization_url(self):
        provider = mocks.MockOAuth1Provider(**mocks.OAUTH1_CREDENTIALS)
        authorization_url = provider.get_authorization_url(mocks.OAUTH1_REQUEST_TOKEN)
        self.assertEqual(mocks.OAUTH1_GET_AUTHORIZATION_URL_EXPECTED_RESULT, authorization_url)

    @mocks.patch_responses(mocks.OAUTH1_ACCESS_TOKEN_RESPONSE_1)
    def test_get_access_token(self, responses):
        provider = mocks.MockOAuth1Provider(**mocks.OAUTH1_CREDENTIALS)
        access_token = provider.get_access_token('https://example.org/callback?oauth_verifier=verifier&oauth_token=token', mocks.OAUTH1_REQUEST_TOKEN)
        self.assertEqual(mocks.OAUTH1_ACCESS_TOKEN, access_token)

    @mocks.patch_responses(mocks.OAUTH1_REQUEST_RESPONSE)
    def test_request(self, responses):
        provider = mocks.MockOAuth1Provider(token=mocks.OAUTH1_VALID_TOKEN_DICT, **mocks.OAUTH1_CREDENTIALS)
        response = provider.request('https://example.org/profile')
        self.assertDictEqual(mocks.OAUTH1_REQUEST_EXPECTED_RESULT, response.json())

    @mocks.patch_responses(mocks.OAUTH1_REQUEST_RESPONSE)
    def test_get_profile(self, responses):
        provider = mocks.MockOAuth1Provider(token=mocks.OAUTH1_ACCESS_TOKEN, **mocks.OAUTH1_CREDENTIALS)
        self.assertDictEqual(mocks.OAUTH1_GET_PROFILE_EXPECTED_RESULT, provider.get_profile())

    @mocks.patch_responses(mocks.OAUTH1_REQUEST_TOKEN_RESPONSE_1, mocks.OAUTH1_ACCESS_TOKEN_RESPONSE_1)
    def test_oauth1_dance(self, responses):
        provider = mocks.MockOAuth1Provider(**mocks.OAUTH1_CREDENTIALS)
        dance = provider.dance({}, 'https://example.org/callback')
        authorization_url = dance.get_authorization_url()
        self.assertEqual(mocks.OAUTH1_GET_AUTHORIZATION_URL_EXPECTED_RESULT, authorization_url)
        token = dance.get_access_token('https://example.org/callback?oauth_verifier=verifier&oauth_token=token')
        self.assertDictEqual(mocks.OAUTH1_ACCESS_TOKEN, token)
