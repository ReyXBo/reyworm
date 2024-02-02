# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-22 14:06:05
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Security methods.
"""


from typing import Any, List, Tuple, Dict, Literal, Union
from reytool.rcomm import request
from reytool.rregex import search, findall, sub
from reytool.rsystem import throw
from reytool.rtime import now


__all__ = (
    "search_sina_market",
    "get_sina_stock_info"
)


def search_sina_market(keyword: str) -> List[Dict[Literal["code", "name", "type", "url"], str]]:
    """
    Search products from market from `sina` website.

    Parameters
    ----------
    keyword : Search keyword.

    Returns
    -------
    Search result table.
    """

    # Get parameter.
    url = "https://biz.finance.sina.com.cn/suggest/lookup_n.php"
    params = {
        "country": "",
        "q": keyword
    }

    # Request.
    response = request(
        url,
        params,
        check=True
    )

    # Unique result.
    if response.request.url.startswith("https://finance.sina.com.cn"):
        pattern = "var papercode = '(.+?)'"
        stock_code = search(pattern, response.text)
        pattern = "var stockname = '(.+?)'"
        stock_name = search(pattern, response.text)
        row = {
            "code": stock_code,
            "name": stock_name,
            "type": "沪深股市(个股)",
            "url": response.request.url
        }
        table = [row]
        return table

    # Extract.
    pattern = "<div class=\"(market|list)\"(.+?)</div>"
    labels_result: Tuple[str, str] = findall(pattern, response.text)
    table = []
    for index, (label_class, div_text) in enumerate(labels_result):
        if label_class != "list":
            continue
        stock_type_div_text = labels_result[index - 1][1]
        stock_type = stock_type_div_text.rsplit("<div>", 1)[1]
        pattern = "<label><a href=\"([^\"]+)\" target=\"_blank\">(.+?)</label>"
        stocks_result = findall(pattern, div_text)
        for stock_url, stock_text in stocks_result:
            pattern = "<.+?>"
            stock_info = sub(pattern, stock_text)
            stock_code, stock_name = stock_info.split(maxsplit=1)
            if stock_name.startswith("("):
                stock_name = stock_name[1:-1]
            row = {
                "code": stock_code,
                "name": stock_name,
                "type": stock_type,
                "url": stock_url
            }
            table.append(row)

    return table


def get_sina_stock_info(code: Union[str, List[str]]) -> List[
    Dict[
        Literal[
            "code",
            "name",
            "price",
            "open",
            "pre_close",
            "high",
            "low",
            "volume",
            "amount",
            "time",
            "change",
            "change_rate",
            "swing"
        ],
        Any
    ]
]:
    """
    Get stock information table from `sina` website.

    Parameters
    ----------
    code : Stock code.

    Returns
    -------
    Stock information table.
    """

    # Get parameter.
    if code.__class__ == str:
        code = code.split(",")
    code = [
        (
            i
            if i[-1] in "0123456789"
            else "gb_" + i.replace(".", "$")
        )
        for i in code
    ]
    code = ",".join(code)
    code = code.lower()
    url = "https://hq.sinajs.cn/rn=%s&list=%s" % (
        now("timestamp"),
        code
    )
    headers = {"Referer": "https://finance.sina.com.cn"}

    # Request.
    response = request(
        url,
        headers=headers,
        check=True
    )

    # Extract.
    pattern = "([^_]+?)=\"([^\"]*)\""
    result: List[Tuple[str, str]] = findall(pattern, response.text)
    table = []
    for code, info in result:
        info_list = info.split(",")
        info_list_len = len(info_list)

        ## A.
        if info_list_len == 34:
            (
                stock_name,
                stock_open,
                stock_pre_close,
                stock_price,
                stock_high,
                stock_low,
                _,
                _,
                stock_volume,
                stock_amount,
                *_,
                stock_date,
                stock_time,
                _,
                _
            ) = info_list
            row = {
                "code": code,
                "name": stock_name,
                "price": float(stock_price),
                "open": float(stock_open),
                "pre_close": float(stock_pre_close),
                "high": float(stock_high),
                "low": float(stock_low),
                "volume": int(float(stock_volume)),
                "amount": int(float(stock_amount)),
                "time": "%s %s" % (stock_date, stock_time),
                "url": "https://finance.sina.com.cn/realstock/company/%s/nc.shtml" % code
            }

        # US.
        elif info_list_len in (36, 30):
            (
                stock_name,
                stock_price,
                _,
                stock_date_time,
                _,
                stock_open,
                stock_high,
                stock_low,
                _, _,
                stock_amount,
                _, _, _, _, _, _, _, _, _, _, _, _, _, _, _,
                stock_pre_close,
                *_
            ) = info_list
            row = {
                "code": code,
                "name": stock_name,
                "price": float(stock_price),
                "open": float(stock_open),
                "pre_close": float(stock_pre_close),
                "high": float(stock_high),
                "low": float(stock_low),
                "amount": int(float(stock_amount)),
                "time": stock_date_time,
                "url": "https://stock.finance.sina.com.cn/usstock/quotes/%s.html" % code.replace("$", ".")
            }

        ## Raise.
        else:
            throw(value=info)

        row["change"] = round(row["price"] - row["pre_close"], 4)
        row["change_rate"] = round(row["change"] / row["pre_close"] * 100, 4)
        row["swing"] = round((row["high"] - row["low"]) / row["high"] * 100, 4)
        table.append(row)

    return table