# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import six
import json

from .base import ProfileMixin
from .oauth1 import OAuth1Consumer
from .oauth2 import OAuth2Consumer

__all__ = ["Google", "Facebook", "LinkedIn", "GitHub", "Bitbucket"]


class Google(ProfileMixin, OAuth2Consumer):

    authorization_url = "https://accounts.google.com/o/oauth2/auth"
    access_token_url = "https://accounts.google.com/o/oauth2/token"
    profile_url = "https://www.googleapis.com/oauth2/v1/userinfo"

    authorization_params = {"approval_prompt": "auto"}
    request_resource_params = {"alt": "json"}

    def normalize_profile_data(self, data):
        return {"uid": data.get("id"),
                "email": data.get("email"),
                "username": data.get("email"),
                "first_name": data.get("given_name"),
                "last_name": data.get("family_name"),
                "gender": data.get("gender")[:1] if data.get("gender", False) else None,
                "birthdate": data.get("dob", None),
                "avatar_url": data.get("picture", None),
                "is_verified": data.get("verified_email", False)}


class Facebook(ProfileMixin, OAuth2Consumer):

    authorization_url = "https://www.facebook.com/dialog/oauth"
    access_token_url = "https://graph.facebook.com/oauth/access_token"
    profile_url = "https://graph.facebook.com/me"

    def normalize_token_response(self, response):
        if "application/json" in response.headers.get("content-type", {}):
            data = json.loads(response.text)
        elif "text/plain" in response.headers.get("content-type", {}):
            data = six.moves.urllib.parse.parse_qs(response.text)
        else:
            raise ValueError("Invalid content-type '{}' for Facebook response".format(response.headers.get("content-type", None)))

        if "expires" in data:
            data["expires_in"] = data.pop("expires")

        if "token_type" not in data:
            data["token_type"] = "Bearer"

        return json.dumps(data)

    def normalize_profile_data(self, data):
        return {"uid": data.get("id"),
                "email": data.get("email"),
                "username": data.get("username"),
                "first_name": data.get("first_name"),
                "last_name": data.get("last_name"),
                "gender": data.get("gender")[:1] if data.get("gender", False) else None,
                "birthdate": data.get("dob", None),
                "avatar_url": "https://graph.facebook.com/{}/picture?type=large&return_ssl_resources=1".format(data.get("id")),
                "is_verified": data.get("verified", False)}


class LinkedIn(ProfileMixin, OAuth2Consumer):

    name = 'linkedin'
    verbose_name = 'LinkedIn'
    authorization_url = "https://www.linkedin.com/uas/oauth2/authorization"
    access_token_url = "https://api.linkedin.com/uas/oauth2/accessToken"
    profile_url = "https://api.linkedin.com/v1/people/~:(id,first-name,last-name,picture-url,email-address)"

    request_resource_params = {"format": "json"}

    def normalize_profile_data(self, data):
        return {"uid": data.get("id"),
                "email": data.get("emailAddress"),
                "username": data.get("emailAddress"),
                "first_name": data.get("firstName"),
                "last_name": data.get("lastName"),
                "gender": None,
                "birthdate": None,
                "avatar_url": data.get("pictureUrl"),
                "is_verified": False}


class GitHub(ProfileMixin, OAuth2Consumer):

    name = 'github'
    verbose_name = 'GitHub'
    authorization_url = "https://github.com/login/oauth/authorize"
    access_token_url = "https://github.com/login/oauth/access_token"
    profile_url = "https://api.github.com/user"

    def normalize_profile_data(self, data):
        return {"uid": data.get("id"),
                "email": data.get("email"),
                "username": data.get("login"),
                "first_name": None,
                "last_name": None,
                "gender": None,
                "birthdate": None,
                "avatar_url": data.get("avatar_url"),
                "is_verified": False}


class Bitbucket(ProfileMixin, OAuth1Consumer):

    request_token_url = "https://bitbucket.org/api/1.0/oauth/request_token"
    authorization_url = "https://bitbucket.org/api/1.0/oauth/authenticate"
    access_token_url = "https://bitbucket.org/api/1.0/oauth/access_token"
    profile_url = "https://bitbucket.org/api/1.0/user"

    def normalize_profile_data(self, data):
        email = next(entry.get('email') for entry in self.request("https://bitbucket.org/api/1.0/emails").json() if entry.get('primary'))
        return {"uid": data.get('user').get("username"),
                "email": email,
                "username": data.get('user').get("username"),
                "first_name": data.get('user').get("first_name"),
                "last_name": data.get('user').get("last_name"),
                "gender": None,
                "birthdate": None,
                "avatar_url": data.get('user').get("avatar"),
                "is_verified": False}
