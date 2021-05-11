# -*- coding: utf-8 -*-
import functools

from zvt import init_config

zvt_coin_config = {}

int_zvt_coin_config = functools.partial(init_config, pkg_name='zvt_coin', current_config=zvt_coin_config)

int_zvt_coin_config()

__all__ = ['int_zvt_coin_config']
