#!/usr/bin/env python
# encoding: utf-8
import urllib
import json

from pyshorteners.shorteners import Shortener
from pyshorteners.exceptions import ShorteningErrorException

import responses
import pytest

s = Shortener('OwlyShortener', api_key='TEST_KEY')
shorten = 'http://ow.ly/test'
expanded = 'http://www.test.com'


@responses.activate
def test_owly_short_method():
    # mock responses
    params = urllib.urlencode({
        'apiKey': 'TEST_KEY',
        'longUrl': expanded,
    })
    body = json.dumps({
        'results': {'shortUrl': shorten}
    })
    mock_url = '{}shorten?{}'.format(s.api_url, params)
    responses.add(responses.GET, mock_url, body=body,
                  match_querystring=True)

    shorten_result = s.short(expanded)

    assert shorten_result == shorten
    assert s.shorten == shorten_result
    assert s.expanded == expanded


@responses.activate
def test_owly_short_method_bad_response():
    # mock responses
    params = urllib.urlencode({
        'apiKey': 'TEST_KEY',
        'longUrl': expanded,
    })
    body = {
        'results': {'shortUrl': shorten}
    }
    mock_url = '{}shorten?{}'.format(s.api_url, params)
    responses.add(responses.GET, mock_url, body=body,
                  match_querystring=True)

    with pytest.raises(ShorteningErrorException):
        s.short(expanded)


@responses.activate
def test_owly_expand_method():
    # mock responses
    params = urllib.urlencode({
        'apiKey': 'TEST_KEY',
        'shortUrl': shorten,
    })
    body = json.dumps({
        'results': {'longUrl': expanded}
    })
    mock_url = '{}expand?{}'.format(s.api_url, params)
    responses.add(responses.GET, mock_url, body=body,
                  match_querystring=True)

    expanded_result = s.expand(shorten)

    assert expanded_result == expanded
    assert s.expanded == expanded


def test_owly_bad_key():
    b = Shortener('OwlyShortener')
    with pytest.raises(TypeError):
        b.short('http://www.test.com')


def test_owly_exception():
    b = Shortener('OwlyShortener', api_key='TK')
    with pytest.raises(ShorteningErrorException):
        b.short('http://www.test.com')
