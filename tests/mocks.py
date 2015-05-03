# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import functools
import datetime
import six
from pytz import utc
import calendar
import responses

from uniauth.base import ProfileMixin
from uniauth.oauth1 import OAuth1Consumer
from uniauth.oauth2 import OAuth2Consumer


def patch_responses(*resps):
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            responses.start()
            for response in resps:
                responses.add(**response)
            result = f(responses=responses, *args, **kwargs)
            responses.stop()
            responses.reset()
            return result
        return wrapper
    return decorator


class QueryString(six.text_type):

    def __eq__(self, other):
        """
        Compares querystring equivalence

        """
        return six.moves.urllib.parse.parse_qs(self) == six.moves.urllib.parse.parse_qs(other)


TIMEDELTA = datetime.timedelta(days=1)
FUTURE_DATETIME = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=utc) + TIMEDELTA
FUTURE_TIMESTAMP = calendar.timegm(FUTURE_DATETIME.utctimetuple())
PAST = datetime.datetime.utcnow().replace(microsecond=0, tzinfo=utc) - TIMEDELTA


# OAUTH1 MOCKS
class MockOAuth1Provider(ProfileMixin, OAuth1Consumer):
    verbose_name = "Mock OAuth1 Provider"
    request_token_url = "https://example.org/oauth/request_token"
    authorization_url = "https://example.org/oauth/authorize"
    access_token_url = "https://example.org/oauth/token"
    profile_url = "https://example.org/profile"

    def normalize_profile_data(self, data):
        return {"uid": data.get("id"),
                "email": data.get("email"),
                "username": None,
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "gender": None,
                "birthdate": None,
                "avatar_url": None,
                "is_verified": False,}

OAUTH1_CREDENTIALS = {"client_id": "client_id", "client_secret": "client_secret"}
OAUTH1_REQUEST_TOKEN = {"oauth_token": "token", "oauth_token_secret": "secret", "oauth_callback_confirmed": "true"}
OAUTH1_ACCESS_TOKEN = {"token": "token", "extra": "secret", "expires_at": None, "scope": None}
OAUTH1_VALID_TOKEN_DICT = {"token": "AT", "extra": "RT", "scope": None, "expires_at": None}
OAUTH1_GET_AUTHORIZATION_URL_EXPECTED_RESULT = "https://example.org/oauth/authorize?oauth_token=token"
OAUTH1_REQUEST_TOKEN_RESPONSE_1 = {
    "method": responses.GET,
    "url": "https://example.org/oauth/request_token",
    "status": 200,
    "content_type": "x-www-form-urlencoded",
    "body": QueryString("oauth_token=token&oauth_token_secret=secret&oauth_callback_confirmed=true")
}
OAUTH1_ACCESS_TOKEN_RESPONSE_1 = {
    "method": responses.GET,
    "url": "https://example.org/oauth/token",
    "status": 200,
    "content_type": "x-www-form-urlencoded",
    "body": QueryString("oauth_token=token&oauth_token_secret=secret")
}
OAUTH1_REQUEST_RESPONSE = {
    "method": responses.GET,
    "url": "https://example.org/profile",
    "status": 200,
    "content_type": "application/json",
    "body": """{"id": "1", "first_name": "John", "last_name": "Carter", "email": "john.carter@fromearth.org"}""",
}
OAUTH1_REQUEST_EXPECTED_RESULT = {"first_name": "John", "last_name": "Carter", "id": "1", "email": u"john.carter@fromearth.org"}
OAUTH1_GET_PROFILE_EXPECTED_RESULT = {"username": None, "first_name": "John", "last_name": "Carter", "uid": "1", "avatar_url": None, "gender": None, "is_verified": False, "email": "john.carter@fromearth.org", "birthdate": None}


# OAUTH2 MOCKS
class MockOAuth2Provider(ProfileMixin, OAuth2Consumer):
    verbose_name = "Mock OAuth2 Provider"
    authorization_url = "https://example.org/oauth/authorize"
    access_token_url = "https://example.org/oauth/token"
    profile_url = "https://example.org/profile"

    def normalize_profile_data(self, data):
        return {"uid": data.get("id"),
                "email": data.get("email"),
                "username": None,
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "gender": None,
                "birthdate": None,
                "avatar_url": None,
                "is_verified": False,}

OAUTH2_CREDENTIALS = {"client_id": "client_id", "client_secret": "client_secret", "scope": ["scope1", "scope2"]}
OAUTH2_EXPIRED_TOKEN_DICT = {"token": "AT", "extra": "RT", "scope": "scope1 scope2", "expires_at": PAST}
OAUTH2_VALID_TOKEN_DICT = {"token": "AT", "extra": "RT", "scope": "scope1 scope2", "expires_at": FUTURE_DATETIME}
OAUTH2_VALID_TOKEN_EXPIRES_AT_JSON = """{{"access_token": "AT", "refresh_token": "RT", "expires_at": {}, "scope": "scope1 scope2"}}""".format(FUTURE_TIMESTAMP)
OAUTH2_VALID_TOKEN_EXPIRES_IN_JSON = """{{"access_token": "AT", "refresh_token": "RT", "expires_in": {}, "scope": "scope1 scope2"}}""".format(TIMEDELTA.total_seconds())
OAUTH2_GET_AUTHORIZATION_URL_EXPECTED_RESULT = "https://example.org/oauth/authorize?response_type=code&client_id=client_id&redirect_uri=https%3A%2F%2Fexample.org%2Fcallback&scope=scope1+scope2&state=nonce"
OAUTH2_EXCHANGE_TOKEN_RESPONSE_1 = {
    "method": responses.POST,
    "url": "https://example.org/oauth/token",
    "status": 200,
    "content_type": "application/json",
    "body": OAUTH2_VALID_TOKEN_EXPIRES_AT_JSON
}
OAUTH2_EXCHANGE_TOKEN_RESPONSE_2 = {
    "method": responses.POST,
    "url": "https://example.org/oauth/token",
    "status": 200,
    "content_type": "application/json",
    "body": OAUTH2_VALID_TOKEN_EXPIRES_IN_JSON
}
OAUTH2_EXCHANGE_TOKEN_EXPECTED_CONTENT_TYPE = "application/x-www-form-urlencoded"
OAUTH2_EXCHANGE_TOKEN_EXPECTED_BODY = QueryString("client_id=client_id&client_secret=client_secret&grant_type=authorization_code&code=code&redirect_uri=https%3A%2F%2Fexample.org%2Fcallback")
OAUTH2_EXCHANGE_TOKEN_EXPECTED_RESULT = OAUTH2_VALID_TOKEN_DICT
OAUTH2_REFRESH_TOKEN_RESPONSE = {
    "method": responses.POST,
    "url": "https://example.org/oauth/token",
    "status": 200,
    "content_type": "application/json",
    "body": OAUTH2_VALID_TOKEN_EXPIRES_AT_JSON,
}
OAUTH2_REFRESH_TOKEN_EXPECTED_CONTENT_TYPE = "application/x-www-form-urlencoded"
OAUTH2_REFRESH_TOKEN_EXPECTED_BODY = QueryString("client_secret=client_secret&grant_type=refresh_token&refresh_token=RT&client_id=client_id")
OAUTH2_REFRESH_TOKEN_EXPECTED_RESULT = OAUTH2_VALID_TOKEN_DICT
OAUTH2_REQUEST_RESPONSE = {
    "method": responses.GET,
    "url": "https://example.org/profile",
    "status": 200,
    "content_type": "application/json",
    "body": """{"id": "1", "first_name": "John", "last_name": "Carter", "email": "john.carter@fromearth.org"}""",
}
OAUTH2_REQUEST_EXPECTED_RESULT = {"first_name": "John", "last_name": "Carter", "id": "1", "email": u"john.carter@fromearth.org"}
OAUTH2_REQUEST_EXPECTED_AUTHORIZATION = "Bearer AT"
OAUTH2_GET_PROFILE_EXPECTED_RESULT = {"username": None, "first_name": "John", "last_name": "Carter", "uid": "1", "avatar_url": None, "gender": None, "is_verified": False, "email": "john.carter@fromearth.org", "birthdate": None}
