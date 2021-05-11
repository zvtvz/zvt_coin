# -*- coding: utf-8 -*-
from sqlalchemy import Column, Float

from zvt.domain import KdataCommon


# coin common kdata
class CoinKdataCommon(KdataCommon):
    pass
# the __all__ is generated
__all__ = ['CoinKdataCommon']

# __init__.py structure:
# common code of the package
# export interface in __all__ which contains __all__ of its sub modules

# import all from submodule coin_1d_kdata
from .coin_1d_kdata import *
from .coin_1d_kdata import __all__ as _coin_1d_kdata_all
__all__ += _coin_1d_kdata_all