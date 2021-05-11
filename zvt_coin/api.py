# -*- coding: utf-8 -*-

import ccxt

from zvt_coin import zvt_coin_config

exchange_cache = {}

exchange_config = {}


def get_coin_exchange(exchange_str, refresh=False) -> ccxt.Exchange:
    if not refresh and exchange_cache.get(exchange_str):
        return exchange_cache[exchange_str]

    exchange = eval("ccxt.{}()".format(exchange_str))
    if exchange_str in zvt_coin_config:
        #     'huobipro': {
        #         'proxy': '',
        #         'apiKey': '',
        #         'secret': '',
        #         'password': '',
        #         'uid': ''
        #     }
        config = zvt_coin_config[exchange_str]
        exchange.apiKey = config.get('apiKey')
        exchange.secret = config.get('secret')
        exchange.proxies = config.get('proxies')
        exchange.uid = config.get('uid')

    exchange_cache[exchange_str] = exchange
    return exchange


def get_exchange_config(exchange_str):
    return zvt_coin_config.get(exchange_str)
