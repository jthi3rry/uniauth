=======
UniAuth
=======

.. image:: https://travis-ci.org/OohlaLabs/uniauth.svg?branch=master
    :target: https://travis-ci.org/OohlaLabs/uniauth

.. image:: https://coveralls.io/repos/OohlaLabs/uniauth/badge.png?branch=master
    :target: https://coveralls.io/r/OohlaLabs/uniauth

Minimalist and framework independent package that provides common OAuth (1 & 2) consumers (or the ability to easily add more).

* Unifies OAuth1 and OAuth2 flows into one easy and clear dance
* Normalises providers' profiles data
* Normalises OAuth1 & 2 tokens for storage/restoration
* Based on `oauthlib <https://github.com/idan/oauthlib>`_ and `requests <https://github.com/kennethreitz/requests>`_

Installation
============

::

    pip install uniauth

Usage
=====

Retrieve a token::

    from uniauth import Bitbucket, GitHub

    # Use an OAuth2 client
    client = GitHub(client_id="****************", client_secret="****************", scope=None)

    # Or an OAuth1 client
    client = Bitbucket(client_id="****************", client_secret="****************")

    # Provides a unified flow for both OAuth1 & OAuth2
    oauth_dance = client.dance(stash, "http://example.org/oauth/callback")

    # 'stash' allows to complete the oauth dance over multiple requests (by maintaining OAuth1's request token or OAuth2's state)
    # It can be anything as long as it implements __setattr__(key, value) and pop(key, default)
    # e.g.:
    #     stash = request.session
    # Or
    #     stash = {}

    # Redirect your user to:
    oauth_dance.get_authorization_url()

    # Get the access token using the absolute url the povider redirected your user to:
    normalised_token = oauth_dance.get_access_token(callback_url)
    # {"token": "**********", "extra": "**********", "expires_at": None, "scope": None}

    # The token is also stored in the client state
    client.get_profile()

Restore a token::

    # OAuth2 client
    client = GitHub(client_id="****************", client_secret="****************", scope=None, token=normalised_token)

    # or OAuth1 client
    client = Bitbucket(client_id="****************", client_secret="****************", token=normalised_token)

    client.get_profile()

Request any resource::

    # client.request has a similar signature to requests.request but with an optional method (it uses "GET" by default)
    response = client.request(url_to_resource)

    # response is an instance of requests.Response
    response.raise_for_status()

    data = response.json()


That's it.

Available Consumers
===================

Bitbucket
---------

Use ``uniauth.Bitbucket``

Facebook
--------

Use ``uniauth.Facebook``

GitHub
------

Use ``uniauth.GitHub``

Google
------

Use ``uniauth.Google``

LinkedIn
--------

Use ``uniauth.LinkedIn``

Contribute More
---------------

It's easy to add more consumers::

    from uniauth.base import ProfileMixin
    from uniauth.oauth2 import OAuth2Consumer

    class MyProviderName(ProfileMixin, OAuth2Consumer):
        authorization_url = "https://example.org/oauth2/authorization"
        access_token_url = "https://example.org/oauth2/access_token"
        profile_url = "https://example.org/user/"

        def normalize_profile_data(self, data):
            # transform provider's format into normalised format
            return {"uid": data.get("id"),
                    "email": data.get("email_address"),
                    "username": data.get("login"),
                    "first_name": data.get("given_name"),
                    "last_name": data.get("family_name"),
                    "gender": data.get("sex"),
                    "birthdate": data.get("dob"),
                    "avatar_url": data.get("picture"),
                    "is_verified": data.get("verified")}


Running Tests
=============

Get a copy of the repository::

    git clone git@github.com:OohlaLabs/uniauth.git .

Install `tox <https://pypi.python.org/pypi/tox>`_::

    pip install tox

Run the tests::

    tox

Contributions
=============

All contributions and comments are welcome.

Change Log
==========

v0.0.2
------
* Cast default provider name to unicode
* Fix resource request extra params not used

v0.0.1
------
* Initial
