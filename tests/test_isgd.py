#!/usr/bin/env python
# encoding: utf-8
import urllib

from pyshorteners.shorteners import Shortener

import responses

s = Shortener('IsgdShortener')
shorten = 'http://is.gd/test'
expanded = 'http://www.test.com'


@responses.activate
def test_isgd_short_method():
    # mock responses
    params = urllib.urlencode({
        'format': 'simple',
        'url': expanded,
    })
    mock_url = '{}?{}'.format(s.api_url, params)
    responses.add(responses.GET, mock_url, body=shorten,
                  match_querystring=True)

    shorten_result = s.short(expanded)

    assert shorten_result == shorten
    assert s.shorten == shorten_result
    assert s.expanded == expanded
