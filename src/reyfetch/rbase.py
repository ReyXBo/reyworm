# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-12-29 23:14:18
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Base methods.
"""


from typing import Any, Literal
from types import MethodType
from threading import get_ident as threading_get_ident
from selenium.webdriver import Edge, Chrome, EdgeOptions, ChromeOptions
from reydb.rdb import Database
from reykit.rbase import Base
from reykit.rnet import join_url


__all__ = (
    'FetchBase',
    'FetchRequest',
    'FetchCrawl',
    'FetchBrowser',
    'crawl_page',
    'FetchRequestWithDatabase',
    'FetchRequestDatabaseRecord'
)


class FetchBase(Base):
    """
    Fetch base type.
    """


class FetchRequest(FetchBase):
    """
    Request API fetch type.
    """


class FetchCrawl(FetchBase):
    """
    Crawl Web fetch type.
    """


class FetchBrowser(FetchBase):
    """
    Control browser fetch type.
    """


    def __init__(
        self,
        driver: Literal['edge', 'chrome'] = 'edge',
        headless: bool = False
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        driver : Browser driver type.
            - `Literal['edge']`: Edge browser.
            - `Literal['chrome']`: Chrome browser.
        headless : Whether use headless mode.
        """

        # Parameter.
        match driver:
            case 'edge':
                driver_type = Edge
                driver_option_type = EdgeOptions
            case 'chrome':
                driver_type = Chrome
                driver_option_type = ChromeOptions

        # Option.
        options = driver_option_type()

        ## Headless.
        if headless:
            options.add_argument('--headless')

        # Driver.
        self.driver = driver_type(options)


    def request(
        self,
        url: str,
        params: dict[str, Any] | None = None
    ) -> None:
        """
        Request URL.

        Parameters
        ----------
        url : URL.
        params : URL parameters.
        """

        # Parameter.
        params = params or {}
        url = join_url(url, params)

        # Request.
        self.driver.get(url)


    @property
    def page(self) -> str:
        """
        Return page elements document.

        Returns
        -------
        Page elements document.
        """

        # Parameter.
        page_source = self.driver.page_source

        return page_source


    __call__ = request


def crawl_page(
    url: str,
    params: dict[str, Any] | None = None
) -> str:
    """
    Crawl page elements document.

    Parameters
    ----------
    url : URL.
    params : URL parameters.

    Returns
    -------
    Page elements document.
    """

    # Parameter.
    browser = FetchBrowser(headless=True)

    # Request.
    browser.request(url, params)

    # Page.
    page = browser.page

    return page


class FetchRequestWithDatabase(FetchRequest):
    """
    With database method reuqest API fetch type.
    Can create database used `self.build_db` method.
    """

    db: Database | None
    db_names: dict[str, str]
    build_db: MethodType


class FetchRequestDatabaseRecord(FetchRequest):
    """
    Request API fetch type of record into the database, can multi threaded.
    """


    def __init__(
        self,
        api: FetchRequestWithDatabase | None = None,
        database: str | None = None,
        table: str | None = None
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        api : `API` instance.
            - `None`: Not record.
        database : Index `API.db_names` database name.
        table : Index `API.db_names` table name.
        """

        # Build.
        self.api = api
        self.database = database
        self.table = table
        self.data: dict[int, dict[str, Any]] = {}


    def __setitem__(self, key: str, value: Any) -> None:
        """
        Update record data parameter.

        Parameters
        ----------
        key : Parameter key.
        value : Parameter value.
        """

        # Check.
        if self.api.db is None:
            return

        # Parameter.
        thread_id = threading_get_ident()
        record = self.data.setdefault(thread_id, {})

        # Update.
        record[key] = value


    def record(self) -> None:
        """
        Insert record to table of database.
        """

        # Check.
        if self.api.db is None:
            return

        # Parameter.
        thread_id = threading_get_ident()
        record = self.data.setdefault(thread_id, {})
        table = self.api.db_names[self.table]

        # Insert.
        self.api.db.execute.insert(table, record)

        # Delete.
        del self.data[thread_id]
