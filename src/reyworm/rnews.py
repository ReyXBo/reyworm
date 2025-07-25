# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-22 14:06:05
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : News methods.
"""


from typing import Any, Literal
from fake_useragent import UserAgent
from reykit.rnet import request, join_url


__all__ = (
    'get_weibo_hot_search',
    'get_toutiao_hot_search'
)


def get_weibo_hot_search() -> list[dict[Literal['rank', 'time', 'title', 'type', 'hot', 'url'], Any]]:
    """
    Get hot search table from `weibo` website.

    Returns
    -------
    Hot search table.
        - `Key 'rank'`: Hot search rank.
        - `Key 'time'`: Hot search time.
        - `Key 'title'`: Hot search title.
        - `Key 'type'`: Hot search type.
        - `Key 'hot'`: Hot search hot value.
        - `Key 'url'`: Hot search URL.
    """

    # Request.
    url = 'https://weibo.com/ajax/side/hotSearch'
    ua = UserAgent()
    headers = {'user-agent': ua.edge}
    response = request(url, headers=headers, check=True)

    # Extract.
    response_json = response.json()
    table: list[dict] = response_json['data']['realtime']

    # Convert.
    table = [
        {
            'title': info['word'],
            'hot': info['num'],
            'url': join_url(
                'https://s.weibo.com/weibo',
                {'q': '#%s#' % info['word']}
            )
        }
        for info in table
        if 'flag' in info
    ]
    func_sort = lambda row: (
        0
        if row['hot'] is None
        else row['hot']
    )
    table.sort(key=func_sort, reverse=True)
    table = [
        {
            'rank': index,
            **row
        }
        for index, row in enumerate(table)
    ]

    return table


def get_toutiao_hot_search() -> list[dict[Literal['title', 'type', 'label', 'hot', 'url', 'image'], Any]]:
    """
    Get hot search table from `toutiao` website.

    Returns
    -------
    Hot search table.
        - `Key 'title'`: Hot search title.
        - `Key 'type'`: Hot search type list.
        - `Key 'label'`: Hot search label.
        - `Key 'hot'`: Hot search hot value.
        - `Key 'url'`: Hot search URL.
        - `Key 'image'`: Hot search image URL.
    """

    # Request.
    url = 'https://www.toutiao.com/hot-event/hot-board/'
    params = {'origin': 'toutiao_pc'}
    response = request(
        url,
        params,
        check=True
    )

    # Extract.
    response_json = response.json()
    table: list[dict] = response_json['data']

    # Convert.
    table = [
        {
            'title': info['Title'],
            'type': info.get('InterestCategory'),
            'label': info.get('LabelDesc'),
            'hot': int(info['HotValue']),
            'url': info['Url'],
            'image': info['Image']['url'],
        }
        for info in table
    ]
    func_sort = lambda row: row['hot']
    table.sort(key=func_sort, reverse=True)
    table = [
        {
            'rank': index,
            **row
        }
        for index, row in enumerate(table)
    ]

    return table
