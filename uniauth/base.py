# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import re
import six


def python_2_unicode_compatible(klass):
    """
    From Django

    A decorator that defines __unicode__ and __str__ methods under Python 2.
    Under Python 3 it does nothing.

    To support Python 2 and 3 with a single code base, define a __str__ method
    returning text and apply this decorator to the class.
    """
    if six.PY2:  # pragma: no cover
        if '__str__' not in klass.__dict__:
            raise ValueError("@python_2_unicode_compatible cannot be applied "
                             "to %s because it doesn't define __str__()." %
                             klass.__name__)
        klass.__unicode__ = klass.__str__
        klass.__str__ = lambda self: self.__unicode__().encode('utf-8')
    return klass


class MetaAuthConsumer(type):

    def __new__(cls, name, bases, attrs):
        if 'name' not in attrs:
            attrs['name'] = six.text_type(name.lower())
        if 'verbose_name' not in attrs:
            attrs['verbose_name'] = six.text_type(re.sub('(.)([A-Z][a-z]+)', r'\1 \2', name))
        return super(MetaAuthConsumer, cls).__new__(cls, name, bases, attrs)


@python_2_unicode_compatible
class BaseAuthConsumer(six.with_metaclass(MetaAuthConsumer)):

    def dance(self, stash, redirect_uri):  # pragma: no cover
        """
        Return OAuth flow instance

        """
        raise NotImplementedError()

    def get_token(self):  # pragma: no cover
        """
        Token dictionary denormalised to contain: token, extra, scope and expires_at
        """
        raise NotImplementedError()

    def request(self, uri, method=None, headers=None, **params):  # pragma: no cover
        raise NotImplementedError()

    def __str__(self):
        return self.verbose_name


class BaseAuthDance(object):

    def __init__(self, client, stash, redirect_uri):
        self.client = client
        self.stash = stash
        self.redirect_uri = redirect_uri

    def get_authorization_url(self, **params):  # pragma: no cover
        raise NotImplementedError()

    def get_access_token(self, callback_uri):  # pragma: no cover
        raise NotImplementedError()


class ProfileMixin(object):

    @property
    def profile_url(self):  # pragma: no cover
        """
        Profile url for provider

        """
        raise NotImplementedError()

    def normalize_profile_data(self, data):  # pragma: no cover
        """
        Return normalized data

        E.g.::
            return {"uid": data.get("id"),
                    "email": None,
                    "username": None,
                    "first_name": None,
                    "last_name": None,
                    "gender": None,
                    "birthdate": None,
                    "avatar_url": None,
                    "is_verified": False,}

        """
        raise NotImplementedError()

    def normalize_profile_response(self, response):
        return response.json()

    def get_profile(self):
        return self.normalize_profile_data(self.normalize_profile_response(self.request(self.profile_url)))
