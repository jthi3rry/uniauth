# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import calendar
import requests
from copy import copy
from datetime import datetime, timedelta
from pytz import utc
from oauthlib.common import urldecode, generate_token
from oauthlib.oauth2.rfc6749.clients import WebApplicationClient
from oauthlib.oauth2.rfc6749.errors import TokenExpiredError

from .base import BaseAuthConsumer, BaseAuthDance


class OAuth2Dance(BaseAuthDance):

    @property
    def _state_stash_key(self):
        return "oauth2_state_{0}".format(self.client.__class__.__name__.lower())

    def get_authorization_url(self, **params):
        state = generate_token()
        self.stash[self._state_stash_key] = state
        return self.client.get_authorization_url(self.redirect_uri, state, **params)

    def get_access_token(self, callback_uri):
        return self.client.get_access_token(self.redirect_uri, self.stash.pop(self._state_stash_key, None), callback_uri)


class OAuth2Consumer(BaseAuthConsumer):

    client_class = WebApplicationClient

    token_method = "POST"
    token_type = "Bearer"

    authorization_params = {}

    request_method = "GET"
    request_extra_params = {}

    @property
    def authorization_url(self):  # pragma: no cover
        """
        Authorization url for provider

        """
        raise NotImplementedError()

    @property
    def access_token_url(self):  # pragma: no cover
        """
        Access token url for provider

        """
        raise NotImplementedError()

    def __init__(self, client_id, client_secret, scope, token=None, refresh_token_callback=None, **client_kwargs):
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.client = self.client_class(self.client_id, token_type=self.token_type, token=self.denormalize_token_data(token), **client_kwargs)
        self.refresh_token_callback = refresh_token_callback

    def dance(self, stash, redirect_uri):
        return OAuth2Dance(self, stash=stash, redirect_uri=redirect_uri)

    def denormalize_token_data(self, data):
        """
        Transforms normalized token into OAuth2 specific format

        """
        if not data:
            return

        return {"access_token": data.get("token"),
                "refresh_token": data.get("extra"),
                "expires_at": calendar.timegm(data.get("expires_at").utctimetuple()) if data.get("expires_at", False) else 0,
                "scope": data.get("scope").split(" ")}

    def normalize_token_data(self, token):
        """
        Transforms token into a generic format

        """
        token = copy(token)
        print(token)
        if token.get("expires_at", False):
            token["expires_at"] = datetime.fromtimestamp(token.get("expires_at"), tz=utc)

        if token.get("expires_in", False):
            token["expires_at"] = datetime.utcnow().replace(tzinfo=utc) + timedelta(seconds=int(token.get("expires_in")))

        return {"token": token.get("access_token"),
                "extra": token.get("refresh_token", None),
                "expires_at": token.get("expires_at"),
                "scope": " ".join(token.get("scope", []))}

    def get_authorization_url(self, redirect_uri, state, **params):
        """
        Returns authorization url to redirect user to to obtain grant code

        First step of the oauth2 dance

        """
        return self.client.prepare_request_uri(self.authorization_url, redirect_uri, self.scope, state, **self.get_authorization_params(**params))

    def get_authorization_params(self, **kwargs):
        """
        Extra params for authorization url

        """
        params = self.authorization_params.copy()
        params.update(kwargs)
        return params

    def get_access_token(self, redirect_uri, state, callback_uri):
        """
        Returns normalized access token

        Last step of the OAuth2 dance

        :redirect_uri: original authorization redirect absolute uri (must be allowed for oauth2 credentials)
        :state: original authorization state (must be identical to the one sent when requesting code)
        :callback_uri: absolute uri of the current request as redirected by provider after authorization step (must contain code or error)
        :return: dict denormalized token

        """
        self.client.parse_request_uri_response(callback_uri, state)
        payload = self.client.prepare_request_body(redirect_uri=redirect_uri, client_secret=self.client_secret)
        response = requests.request(self.token_method, self.access_token_url, data=payload, headers={"content-type": "application/x-www-form-urlencoded"})
        response.raise_for_status()
        return self.normalize_token_data(self.client.parse_request_body_response(self.normalize_token_response(response)))

    def refresh_token(self):
        """
        Refreshes the token when requesting a resource with an expired token

        """
        payload = self.client.prepare_refresh_body(refresh_token=self.client.refresh_token, client_id=self.client_id, client_secret=self.client_secret)
        response = requests.request(self.token_method, self.access_token_url, data=dict(urldecode(payload)), headers={"content-type": "application/x-www-form-urlencoded"})
        response.raise_for_status()
        return self.normalize_token_data(self.client.parse_request_body_response(self.normalize_token_response(response)))

    def normalize_token_response(self, response):
        """
        Fix response content to match what's expected by oauthlib (json string)

        """
        return response.text

    def request(self, url, method=None, auto_refresh_token=True, refresh_token_callback=None, **kwargs):
        try:
            url, headers, body = self.client.add_token(url, http_method=method or self.request_method, body=kwargs.get('data', None), headers=kwargs.get('headers', None))
            response = requests.request(method or self.request_method, url=url, headers=headers, data=body, params=self.get_request_extra_params(**kwargs.get('params', {})))
            response.raise_for_status()
            return response
        except TokenExpiredError:
            if not (auto_refresh_token and self.client.refresh_token):
                raise
            refreshed_token = self.refresh_token()
            callback = refresh_token_callback or self.refresh_token_callback
            if callback:
                callback(refreshed_token)
            return self.request(url, method, **kwargs)

    def get_request_extra_params(self, **kwargs):
        """
        Extra params for requesting resources

        """
        params = self.request_extra_params.copy()
        params.update(kwargs)
        return params

    def get_token(self):
        """
        Return normalised

        """
        return self.normalize_token_data(self.client.token)
