# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import six
import unittest

from uniauth import Google, Facebook, LinkedIn, GitHub, Bitbucket

from . import mocks


class GoogleTest(unittest.TestCase):

    def setUp(self):
        self.provider = Google(**mocks.OAUTH2_CREDENTIALS)

    def test_name(self):
        self.assertEqual('google', self.provider.name)
        self.assertEqual('Google', self.provider.verbose_name)
        self.assertEqual('Google', six.text_type(self.provider))

    # Add more


class FacebookTest(unittest.TestCase):

    def setUp(self):
        self.provider = Facebook(**mocks.OAUTH2_CREDENTIALS)

    def test_name(self):
        self.assertEqual('facebook', self.provider.name)
        self.assertEqual('Facebook', self.provider.verbose_name)
        self.assertEqual('Facebook', six.text_type(self.provider))

    # Add more


class LinkedInTest(unittest.TestCase):

    def setUp(self):
        self.provider = LinkedIn(**mocks.OAUTH2_CREDENTIALS)

    def test_name(self):
        self.assertEqual('linkedin', self.provider.name)
        self.assertEqual('LinkedIn', self.provider.verbose_name)
        self.assertEqual('LinkedIn', six.text_type(self.provider))

    # Add more


class GitHubTest(unittest.TestCase):

    def setUp(self):
        self.provider = GitHub(**mocks.OAUTH2_CREDENTIALS)

    def test_name(self):
        self.assertEqual('github', self.provider.name)
        self.assertEqual('GitHub', self.provider.verbose_name)
        self.assertEqual('GitHub', six.text_type(self.provider))

    # Add more


class BitbucketTest(unittest.TestCase):

    def setUp(self):
        self.provider = Bitbucket(**mocks.OAUTH1_CREDENTIALS)

    def test_name(self):
        self.assertEqual('bitbucket', self.provider.name)
        self.assertEqual('Bitbucket', self.provider.verbose_name)
        self.assertEqual('Bitbucket', six.text_type(self.provider))

    # Add more
