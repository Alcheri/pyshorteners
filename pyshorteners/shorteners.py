# coding: utf-8
from __future__ import unicode_literals

import json

import requests

from .utils import is_valid_url
from .exceptions import (UnknownShortenerException, ShorteningErrorException,
                         ExpandingErrorException)

__all__ = ['Shortener', ]
module = __import__('pyshorteners.shorteners')


class Shortener(object):
    api_url = None

    def __init__(self, engine='GenericExpander', **kwargs):
        self.engine = engine
        self.kwargs = kwargs
        self.shorten = None
        self.expanded = None

        try:
            self._class = getattr(module.shorteners, self.engine)
        except AttributeError:
            raise UnknownShortenerException('Please enter a valid shortener.')

        for key, item in list(kwargs.items()):
            setattr(self, key, item)

    def short(self, url):
        if not is_valid_url(url):
            raise ValueError('Please enter a valid url')
        self.expanded = url

        self.shorten = self._class(**self.kwargs).short(url)
        return self.shorten

    def expand(self, url=None):
        if url and not is_valid_url(url):
            raise ValueError('Please enter a valid url')

        if url:
            self.expanded = self._class(**self.kwargs).expand(url)
        return self.expanded

    def qrcode(self, width=120, height=120):
        if not self.shorten:
            return None

        qrcode_url = ('http://chart.apis.google.com/chart?cht=qr&'
                      'chl={0}&chs={1}x{2}'.format(self.shorten, width,
                                                   height))
        return qrcode_url


class GoogleShortener(object):
    """
    Googl Shortener Implementation
    Needs a API_KEY
    """
    api_url = 'https://www.googleapis.com/urlshortener/v1/url'

    def __init__(self, **kwargs):
        if not kwargs.get('api_key', False):
            raise TypeError('api_key missing from kwargs')
        self.api_key = kwargs.get('api_key')

    def short(self, url):
        params = json.dumps({'longUrl': url})
        headers = {'content-type': 'application/json'}
        url = '{}?key={}'.format(self.api_url, self.api_key)
        response = requests.post(url, data=params,
                                 headers=headers)
        if response.ok:
            try:
                data = response.json()
            except ValueError as e:
                raise ShorteningErrorException('There was an error shortening'
                                               ' this url - {0}'.format(e))
            if 'id' in data:
                return data['id']
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        params = {'shortUrl': url}
        url = '{}?key={}'.format(self.api_url, self.api_key)
        response = requests.get(url, params=params)

        if response.ok:
            try:
                data = response.json()
            except ValueError:
                raise ExpandingErrorException('There was an error expanding'
                                              ' this url - {0}'.format(
                                                  response.content))
            if 'longUrl' in data:
                return data['longUrl']
        raise ExpandingErrorException('There was an error expanding '
                                      'this url - {0}'.format(
                                          response.content))


class BitlyShortener(object):
    """
    Bit.ly shortener Implementation
    needs on app.config:
    BITLY_LOGIN - Your bit.ly login user
    BITLY_API_KEY - Your bit.ly api key
    BITLY_TOKEN - Your bit.ly app access token
    """
    api_url = 'https://api-ssl.bit.ly/'

    def __init__(self, **kwargs):
        if not all([kwargs.get('bitly_login', False),
                    kwargs.get('bitly_token', False),
                    kwargs.get('bitly_api_key', False)]):
            raise TypeError('bitly_login, bitly_api_key and bitly_token '
                            'missing from kwargs')
        self.login = kwargs.get('bitly_login')
        self.api_key = kwargs.get('bitly_api_key')
        self.token = kwargs.get('bitly_token')

    def short(self, url):
        shorten_url = '{}{}'.format(self.api_url, 'v3/shorten')
        params = dict(
            uri=url,
            x_apiKey=self.api_key,
            x_login=self.login,
            access_token=self.token,
        )
        response = requests.post(shorten_url, data=params)
        if response.ok:
            data = response.json()
            if 'status_code' in data and data['status_code'] == 200:
                return data['data']['url']
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        expand_url = '{0}{1}'.format(self.api_url, 'v3/expand')
        params = dict(
            shortUrl=url,
            x_login=self.login,
            x_apiKey=self.api_key,
            access_token=self.token
        )
        response = requests.get(expand_url, params=params)
        if response.ok:
            data = response.json()
            if 'status_code' in data and data['status_code'] == 200:
                return data['data']['expand'][0]['long_url']
        raise ExpandingErrorException('There was an error expanding'
                                      ' this url - {0}'.format(
                                          response.content))


class TinyurlShortener(object):
    """
    TinyURL.com shortener implementation
    No config params needed
    """
    api_url = 'http://tinyurl.com/api-create.php'

    def short(self, url):
        response = requests.get(self.api_url, params=dict(url=url))
        if response.ok:
            return response.text
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        response = requests.get(url)
        if response.ok:
            return response.url
        raise ExpandingErrorException('There was an error expanding '
                                      'this url - {0}'.format(
                                          response.content))


class AdflyShortener(object):
    """
    Adf.ly shortener implementation
    Needs api key and uid
    """
    api_url = 'http://api.adf.ly/api.php'

    def __init__(self, **kwargs):
        if not all([kwargs.get('key', False), kwargs.get('uid', False)]):
            raise TypeError('Please input the key and uid value')
        self.key = kwargs.get('key')
        self.uid = kwargs.get('uid')
        self.type = kwargs.get('type', 'int')

    def short(self, url):
        data = {
            'domain': 'adf.ly',
            'advert_type': self.type,  # int or banner
            'key': self.key,
            'uid': self.uid,
            'url': url,
        }
        response = requests.get(self.api_url, params=data)
        if response.ok:
            return response.text
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        """
        No expand for now
        TODO!
        """
        return url


class IsgdShortener(object):
    """
    Is.gd shortener implementation
    No config params needed
    """
    api_url = 'http://is.gd/create.php'

    def short(self, url):
        params = {
            'format': 'simple',
            'url': url,
        }
        response = requests.get(self.api_url, params=params)
        if response.ok:
            return response.text.strip()
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        response = requests.get(url)
        if response.ok:
            return response.url
        raise ExpandingErrorException('There was an error expanding'
                                      ' this url - {0}'.format(
                                          response.content))


class SentalaShortener(object):
    """
    Senta.la shortener implementation
    No config params needed
    """
    api_url = 'http://senta.la/api.php'

    def short(self, url):
        params = {
            'dever': 'encurtar',
            'format': 'simple',
            'url': url,
        }
        response = requests.get(self.api_url, params=params)
        if response.ok:
            return response.text.strip()
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        response = requests.get(url)
        if response.ok:
            return response.url
        raise ExpandingErrorException('There was an error expanding '
                                      'this url - {0}'.format(
                                          response.content))


class QrCxShortener(object):
    """
    Qr.cx shortener implementation
    No config params needed
    """
    api_url = 'http://qr.cx/api/'

    def short(self, url):
        params = {
            'longurl': url,
        }
        response = requests.get(self.api_url, params=params)
        if response.ok:
            return response.text.strip()
        raise ShorteningErrorException('There was an error shortening this '
                                       'url')

    def expand(self, url):
        response = requests.get(url)
        if response.ok:
            return response.url
        raise ExpandingErrorException('There was an error expanding this url')


class OwlyShortener(object):
    """
    Ow.ly url shortner api implementation
    Located at: http://ow.ly/api-docs
    Doesnt' need anything from the app
    """
    api_url = 'http://ow.ly/api/1.1/url/'

    def __init__(self, **kwargs):
        if not kwargs.get('api_key', False):
            raise TypeError('api_key is missing from kwargs')
        self.api_key = kwargs.get('api_key')

    def short(self, url):
        shorten_url = self.api_url + 'shorten'
        data = {'apiKey': self.api_key, 'longUrl': url}
        response = requests.get(shorten_url, params=data)
        if response.ok:
            try:
                data = response.json()
            except ValueError:
                raise ShorteningErrorException('There was an error shortening'
                                               ' this url')
            return data['results']['shortUrl']
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        expand_url = self.api_url + 'expand'
        data = {'apiKey': self.api_key, 'shortUrl': url}
        response = requests.get(expand_url, params=data)
        if response.ok:
            try:
                data = response.json()
            except ValueError:
                raise ShorteningErrorException('There was an error shortening'
                                               ' this url')
            return data['results']['longUrl']
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))


class ReadabilityShortener(object):
    """
    Readbility url shortner api implementation
    Located at: https://readability.com/developers/api/shortener
    Doesnt' need anything from the app
    """
    api_url = 'http://www.readability.com/api/shortener/v1/urls/'

    def short(self, url):
        params = {'url': url}
        response = requests.post(self.api_url, data=params)
        if response.ok:
            try:
                data = response.json()
            except ValueError:
                raise ShorteningErrorException('There was an error shortening'
                                               ' this url - {0}'.format(
                                                   response.content))
            return data['meta']['rdd_url']
        raise ShorteningErrorException('There was an error shortening this '
                                       'url - {0}'.format(response.content))

    def expand(self, url):
        url_id = url.split('/')[-1:][0]
        api_url = self.api_url + url_id
        response = requests.get(api_url)
        if response.ok:
            try:
                data = response.json()
            except ValueError:
                raise ExpandingErrorException('There was an error expanding'
                                              ' this url - {0}'.format(
                                                  response.content))
            return data['meta']['full_url']
        raise ExpandingErrorException('There was an error expanding this url')


# pylint: disable=R0921
class GenericExpander(object):
    """
    Adding this generic expander, it doesn't shorten url's, just tries to
    retrieve URL's using a get http method
    """

    def short(self, url):
        raise NotImplementedError('This class doesn\'t support shortening')

    def expand(self, url):
        response = requests.get(url)
        if response.ok:
            return response.url
        raise ExpandingErrorException('There was an error expanding this url')
