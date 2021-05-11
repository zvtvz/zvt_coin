# -*- coding: utf-8 -*-
import pandas as pd
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declarative_base

from zvt.contract import EntityMixin
from zvt.contract.register import register_schema, register_entity

CoinMetaBase = declarative_base()


@register_entity(entity_type='coin')
class Coin(EntityMixin, CoinMetaBase):
    __tablename__ = 'coin'
    # 上市日
    list_date = Column(DateTime)
    # 退市日
    end_date = Column(DateTime)

    @classmethod
    def get_trading_dates(cls, start_date=None, end_date=None):
        return pd.date_range(start_date, end_date, freq='D')

    @classmethod
    def could_short(cls):
        return True

    @classmethod
    def get_trading_t(cls):
        return 0

    @classmethod
    def get_trading_intervals(cls):
        return [('00:00,23:59')]


register_schema(providers=['ccxt'], db_name='coin_meta', schema_base=CoinMetaBase)
# the __all__ is generated
__all__ = ['Coin']