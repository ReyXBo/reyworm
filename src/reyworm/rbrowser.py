# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-12-29 23:14:18
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Browser methods.
"""


from typing import Any, Literal
from selenium.webdriver import Edge, Chrome, EdgeOptions, ChromeOptions
from reykit.rcomm import join_url
from reykit.rtime import sleep
from reykit.rtype import RBase


__all__ = (
    'RBrowser',
    'get_page'
)


class RBrowser(RBase):
    """
    Rey's `browser` type.
    """


    def __init__(
        self,
        driver: Literal['edge', 'chrome'] = 'edge',
        headless: bool = False
    ) -> None:
        """
        Build `browser` instance attributes.

        Parameters
        ----------
        driver : Browser driver type.
            - `Literal['edge']`: Edge browser.
            - `Literal['chrome']`: Chrome browser.
        headless : Whether use headless mode.
        """

        # Get parameter.
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

        # Get parameter.
        if params is None:
            params = {}
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

        # Get parameter.
        page_source = self.driver.page_source

        return page_source


    __call__ = request


def get_page(
    url: str,
    params: dict[str, Any] | None = None
) -> str:
    """
    Get page elements document.

    Parameters
    ----------
    url : URL.
    params : URL parameters.

    Returns
    -------
    Page elements document.
    """

    # Get parameter.
    browser = RBrowser(headless=True)

    # Request.
    browser.request(url, params)

    # Page.
    page = browser.page

    return page
