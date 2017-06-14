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


# Pylint doesn't fully understand what bottle does and doesn't know
# about all the members in all the objects. Disable related warnigs for
# this module.
#
# pylint: disable=no-member
# pylint: disable=not-an-iterable


import time

import bottle

import qvarn


class LoggingPlugin(object):

    '''A Bottle plugin to log HTTP requests.'''

    def __init__(self):
        # Create a counter shared between threads so that HTTP
        # requests can be numbered linearly between threads.
        self._counter = qvarn.Counter()

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            # Do the thing and catch any exceptions.
            try:
                self._start_context()
                self._log_request()
                data = callback(*args, **kwargs)
                self._add_response_headers()
                self._log_response(data)
                self._end_context()
                return data
            except SystemExit:
                self._end_context()
                raise
            except BaseException as e:
                # Log an error, not critical, since we're not
                # necessarily exiting due to the exception. In fact,
                # we hopefully aren't.
                qvarn.log.log('error', msg_text=str(e), exc_info=True)
                self._end_context()
                raise bottle.HTTPError(status=500, body=str(e))

        return wrapper

    def _start_context(self):
        n = self._counter.increment()
        context = 'HTTP request {}'.format(n)
        qvarn.log.set_context(context)

    def _end_context(self):
        qvarn.log.reset_context()

    def _log_request(self):
        '''Log an HTTP request, with arguments and body.'''
        r = bottle.request

        # Do not log the values of these headers.
        hidden_headers = [
            'Authorization',
        ]

        qvarn.log.log(
            'http-request',
            method=r.method,
            path=r.path,
            url_args=r.url_args,
            headers={
                key: (
                    'HIDDEN'
                    if key in hidden_headers
                    else bottle.request.headers.get(key)
                )
                for key in bottle.request.headers
            }
        )

    def _add_response_headers(self):
        bottle.response.set_header('Date', self._rfc822_now())

    def _rfc822_now(self):
        return time.strftime('%a, %d %b %Y %H:%M:%S %z')

    def _log_response(self, data):
        r = bottle.response
        qvarn.log.log(
            'http-response',
            status=r.status_code,
            headers=dict(r.headers))
