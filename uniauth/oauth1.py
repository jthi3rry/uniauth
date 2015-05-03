# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import requests
from copy import copy
from oauthlib import oauth1
from oauthlib.common import urldecode, add_params_to_uri, urlparse

from .base import BaseAuthConsumer, BaseAuthDance


class OAuth1Dance(BaseAuthDance):

    @property
    def _request_token_stash_key(self):
        return "oauth1_request_token_{0}".format(self.client.__class__.__name__.lower())

    def get_authorization_url(self, **params):
        request_token = self.client.get_request_token(self.redirect_uri)
        self.stash[self._request_token_stash_key] = request_token
        return self.client.get_authorization_url(request_token)

    def get_access_token(self, callback_uri):
        return self.client.get_access_token(callback_uri, self.stash.pop(self._request_token_stash_key, None))


class OAuth1Consumer(BaseAuthConsumer):

    client_class = oauth1.Client
    signature_method = oauth1.SIGNATURE_HMAC
    signature_type = oauth1.SIGNATURE_TYPE_QUERY
    token_method = "GET"

    request_method = "get"
    request_extra_params = {}

    def __init__(self, client_id, client_secret, token=None, **client_kwargs):
        self.client_key = client_id
        self.client_secret = client_secret
        self.client = self.client_class(client_key=self.client_key, client_secret=self.client_secret,
                                        signature_method=self.signature_method, signature_type=self.signature_type,
                                        **client_kwargs)

        self.set_token(self.denormalize_token_data(token))

    @property
    def request_token_url(self):  # pragma: no cover
        """
        Used to retrieve oauth request token and request token secret

        """
        raise NotImplementedError()

    @property
    def authorization_url(self):  # pragma: no cover
        """
        Authorization url for provider

        """
        raise NotImplementedError()


    def access_token_url(self):  # pragma: no cover
        """
        Used to retrieve oauth access token and access token secret

        """
        raise NotImplementedError()

    def dance(self, stash, redirect_uri):
        return OAuth1Dance(self, stash=stash, redirect_uri=redirect_uri)

    def denormalize_token_data(self, data):
        """
        Transforms normalized token into OAuth1 specific format

        """
        if not data:
            return

        return {"oauth_token": data.get("token"),
                "oauth_token_secret": data.get("extra")}

    def normalize_token_data(self, token):
        """
        Transforms token into a generic format

        """
        token = copy(token)
        return {"token": token.get("oauth_token"),
                "extra": token.get("oauth_token_secret"),
                "expires_at": None,
                "scope": None}

    def set_token(self, token):
        if not token:
            return
        self.client.resource_owner_key = token.get('oauth_token')
        self.client.resource_owner_secret = token.get('oauth_token_secret')

    def get_request_token(self, redirect_uri):
        """
        Retrieve oauth token and token secret

        First step of OAuth1

        """
        self.client.callback_uri = redirect_uri
        uri, headers, body = self.client.sign(self.request_token_url)
        response = requests.request(self.token_method, uri, headers=headers, data=body)
        response.raise_for_status()
        return dict(urldecode(response.text))

    def get_authorization_url(self, request_token):
        """
        Returns authorization url to redirect user to to obtain token

        Second step of OAuth1

        """
        return add_params_to_uri(self.authorization_url, params={"oauth_token": request_token.get('oauth_token')})

    def get_access_token(self, callback_uri, request_token):
        """
        Returns access token

        Third and last step of OAuth1

        """
        verifier = dict(urldecode(urlparse.urlparse(callback_uri).query))
        self.client.verifier = verifier.get('oauth_verifier')
        self.client.resource_owner_key = request_token.get('oauth_token')
        self.client.resource_owner_secret = request_token.get('oauth_token_secret')
        uri, headers, body = self.client.sign(self.access_token_url)
        response = requests.request(self.token_method, uri, headers=headers, data=body)
        self.client.verifier = None
        response.raise_for_status()
        token = dict(urldecode(response.text))
        self.set_token(token)
        return self.normalize_token_data(token)

    def request(self, url, method=None, **kwargs):
        url, headers, body = self.client.sign(add_params_to_uri(url, self.get_request_extra_params(**kwargs.get("params", {}))),
                                              http_method=method or self.request_method, headers=kwargs.get('headers', None), body=kwargs.get('data', None))
        response = requests.request(method or self.request_method, url, headers=headers, data=body)
        response.raise_for_status()
        return response

    def get_request_extra_params(self, **kwargs):
        """
        Extra params for requesting resources

        """
        params = self.request_extra_params.copy()
        params.update(kwargs)
        return params

    def get_token(self):
        """
        Return normalised token

        """
        return self.normalize_token_data({"oauth_token": self.client.resource_owner_key, "oauth_token_secret": self.client.resource_owner_secret})
