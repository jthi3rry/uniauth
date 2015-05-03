# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, print_function

import os
import re
import sys
import uuid
import codecs
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from pip.req import parse_requirements


class Tox(TestCommand):

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the eggs aren't loaded
        import tox
        errno = tox.cmdline(self.test_args)
        sys.exit(errno)


def read(*parts):
    filename = os.path.join(os.path.dirname(__file__), *parts)
    with codecs.open(filename, encoding='utf-8') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

pypi_readme_note = """\
.. note::

   For the latest source, discussions, etc., please visit the
   `GitHub repository <https://github.com/OohlaLabs/uniauth>`_
"""

setup(
    name='uniauth',
    version=find_version('uniauth', '__init__.py'),
    author='OohlaLabs Limited',
    author_email='packages@oohlalabs.com',
    maintainer='Thierry Jossermoz',
    maintainer_email='thierry.jossermoz@oohlalabs.com',
    url="https://github.com/OohlaLabs/uniauth",
    description="Minimalist and framework independent OAuth(1 & 2) consumers",
    long_description="\n\n".join([pypi_readme_note, read('README.rst')]),
    install_requires=[str(ir.req) for ir in parse_requirements('requirements.txt', session=uuid.uuid1())],
    packages=find_packages(),
    tests_require=["tox"],
    cmdclass={"test": Tox},
    license='MIT',
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
    ]
)
