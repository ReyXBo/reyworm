# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2024-01-10 21:57:08
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Calendar methods.
"""


from typing import List, Dict, Optional
from json import loads as json_loads
from reytool.rcomm import request
from reytool.rregex import search
from reytool.rtime import now


__all__ = (
    "get_calendar",
    "get_lunar_calendar"
)


def get_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None
) -> List[Dict]:
    """
    Get calendar table for three months from `baidu` website.

    Parameters
    ----------
    year : Given year.
        - `None` : Now year.

    month : Given month.
        - `None` : Now month.

    Returns
    -------
    Calendar table.
    """

    # Get parameter.
    now_date = now("date")
    if year is None:
        year = now_date.year
    if month is None:
        month = now_date.month
    if month == 12:
        month = 1
    else:
        month += 1
    url = "https://opendata.baidu.com/data/inner"
    query = "%s年%s月" % (year, month)
    params = {
        "tn": "reserved_all_res_tn",
        "type": "json",
        "resource_id": "52109",
        "query": query,
        "apiType": "yearMonthData",
        "cb": "jsonp_1706670926975_94318"
    }

    # Request.
    response = request(url, params)

    # Extract.
    pattern = "{.+}"
    text = search(pattern, response.text)
    data: Dict = json_loads(text)
    table: List[Dict] = data["Result"][0]["DisplayData"]["resultData"]["tplData"]["data"]["almanac"]

    # Convert.
    week_dict = {
        "一": 0,
        "二": 1,
        "三": 2,
        "四": 3,
        "五": 4,
        "六": 5,
        "日": 6
    }
    table = [
        {
            "year": int(row["year"]),
            "month": int(row["month"]),
            "day": int(row["day"]),
            "week": week_dict[row["cnDay"]],
            "work": row.get("status"),
            "festival": [
                {
                    "name": info["name"],
                    "url": info.get("baikeUrl")
                }
                for info in row.get("festivalInfoList", [])
            ],
            "animal": row["animal"],
            "lunar_year": int(row["lunarYear"]),
            "lunar_month": int(row["lunarMonth"]),
            "lunar_day": int(row["lunarDate"]),
            "gz_year": row["gzYear"],
            "gz_month": row["gzMonth"],
            "gz_day": row["gzDate"],
            "suit": row["suit"].split("."),
            "avoid": row["avoid"].split("."),
            "url": row["yjJumpUrl"]
        }
        for row in table
    ]
    for row in table:
        week = row["week"]
        work = row["work"]
        if work is None:
            is_work_day = week not in (5, 6)
        elif work == "1":
            is_work_day = False
        elif work == "2":
            is_work_day = True
        row["work"] = is_work_day

    return table


def get_lunar_calendar(
    year: Optional[int] = None,
    month: Optional[int] = None
) -> List[Dict]:
    """
    Get lunar calendar table for one month from `rili` website.

    Parameters
    ----------
    year : Given year.
        - `None` : Now year.

    month : Given month.
        - `None` : Now month.

    Returns
    -------
    Lunar calendar table.
    """

    # Get parameter.
    now_date = now("date")
    if year is None:
        year = now_date.year
    if month is None:
        month = now_date.month
    url = "https://www.rili.com.cn/rili/json/pc_wnl/%s/%02d.js" % (year, month)
    params = {"_": now("timestamp")}

    # Request.
    response = request(url, params)

    # Extract.
    pattern = "{.+}"
    text = search(pattern, response.text)
    data = json_loads(text)
    table = data["data"]

    return table