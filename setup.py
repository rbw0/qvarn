#!/usr/bin/python
#
# setup.py - standard Python build-and-package program
#
# Copyright 2015, 2016 Suomen Tilaajavastuu Oy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import ast
from distutils.core import setup


for line in open('qvarn/version.py'):
    if line.startswith('__version__'):
        __version__ = ast.literal_eval(line.split('=')[1].strip())


setup(
    name='qvarn',
    version=__version__,
    description='backend service for JSON and binary data storage',
    author='Suomen Tilaajavastuu Oy',
    author_email='tilaajavastuu.hifi@tilaajavastuu.fi',
    packages=['qvarn'],
    scripts=['slog-pretty', 'slog-errors', 'qvarn-backend'],
    install_requires=[
        'bottle',
        'psycopg2',
        'PyJWT',
        'uwsgidecorators',
        'pyyaml',
        'cryptography',
    ],
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
