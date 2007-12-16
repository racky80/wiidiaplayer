# Copyright (c) 2007-2008 The PyAMF Project.
# See LICENSE for details.

"""
Django gateway tests.

@author: U{Nick Joyce<mailto:nick@boxdesign.co.uk>}

@since: 0.1.0
"""

import unittest

import os

from django import http

from pyamf import remoting, util
from pyamf.remoting.djangogateway import DjangoGateway

class HttpRequest(http.HttpRequest):
    """
    Custom HttpRequest to support raw_post_data provided by
    django.core.handlers.*
    """

    def __init__(self, *args, **kwargs):
        http.HttpRequest.__init__(self, *args, **kwargs)

        self.raw_post_data = ''

if 'DJANGO_SETTINGS_MODULE' not in os.environ:
    import imp, sys

    sys.modules['pyamf.test_django'] = imp.new_module('pyamf.test_django')
    os.environ['DJANGO_SETTINGS_MODULE'] = 'pyamf.test_django'

class DjangoGatewayTestCase(unittest.TestCase):
    def test_request_method(self):
        gw = DjangoGateway()

        http_request = HttpRequest()
        http_request.method = 'GET'

        http_response = gw(http_request)
        self.assertEquals(http_response.status_code, 405)

        http_request.method = 'POST'

        self.assertRaises(EOFError, gw, http_request)

    def test_bad_request(self):
        gw = DjangoGateway()

        request = util.BufferedByteStream()
        request.write('Bad request')
        request.seek(0, 0)

        http_request = HttpRequest()
        http_request.method = 'POST'
        http_request.raw_post_data = request.getvalue()

        http_response = gw(http_request)
        self.assertEquals(http_response.status_code, 400)

    def test_unknown_request(self):
        gw = DjangoGateway()

        request = util.BufferedByteStream()
        request.write('\x00\x00\x00\x00\x00\x01\x00\x09test.test\x00'
            '\x02/1\x00\x00\x00\x14\x0a\x00\x00\x00\x01\x08\x00\x00\x00\x00'
            '\x00\x01\x61\x02\x00\x01\x61\x00\x00\x09')
        request.seek(0, 0)

        http_request = HttpRequest()
        http_request.method = 'POST'
        http_request.raw_post_data = request.getvalue()

        http_response = gw(http_request)
        envelope = remoting.decode(http_response.content)

        message = envelope['/1']

        self.assertEquals(message.status, remoting.STATUS_ERROR)
        body = message.body

        self.assertTrue(isinstance(body, remoting.ErrorFault))
        self.assertEquals(body.code, 'Service.ResourceNotFound')

def suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(DjangoGatewayTestCase))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='suite')