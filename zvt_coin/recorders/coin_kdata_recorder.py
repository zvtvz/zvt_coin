# -*- coding: utf-8 -*-

import pandas as pd

from zvt.api import get_kdata_schema
from zvt.contract import IntervalLevel
from zvt.contract.api import df_to_db
from zvt.contract.recorder import FixedCycleDataRecorder
from zvt.utils import to_time_str, to_pd_timestamp
from zvt.utils.time_utils import TIME_FORMAT_DAY, TIME_FORMAT_ISO8601
from zvt_coin.api import get_coin_exchange, get_exchange_config
from zvt_coin.domain import Coin, CoinKdataCommon


class CoinKdataRecorder(FixedCycleDataRecorder):
    entity_provider = 'ccxt'
    entity_schema = Coin

    provider = 'ccxt'

    # register the recorder to data_schema
    data_schema = CoinKdataCommon

    def __init__(self, entity_type='coin', exchanges=None, entity_ids=None, codes=None, day_data=False, batch_size=10,
                 force_update=True, sleeping_time=1, default_size=2000, real_time=False, fix_duplicate_way='ignore',
                 start_timestamp=None, end_timestamp=None, close_hour=0, close_minute=0, level=IntervalLevel.LEVEL_1DAY,
                 kdata_use_begin_time=False, one_day_trading_minutes=24 * 60,
                 entity_filters=None) -> None:
        if entity_filters is None:
            entity_filters = [Coin.code.contains('/USDT')]
        level = IntervalLevel(level)

        self.data_schema = get_kdata_schema(entity_type=entity_type, level=level, adjust_type=None)
        self.ccxt_trading_level = level.value

        super().__init__(entity_type, exchanges, entity_ids, codes, day_data, batch_size, force_update, sleeping_time,
                         default_size, real_time, fix_duplicate_way, start_timestamp, end_timestamp, close_hour,
                         close_minute, level, kdata_use_begin_time, one_day_trading_minutes, entity_filters)

    def record(self, entity, start, end, size, timestamps):
        ccxt_exchange = get_coin_exchange(entity.exchange)

        if ccxt_exchange.has['fetchOHLCV']:
            config = get_exchange_config(entity.exchange)
            limit = config['kdata_limit']

            limit = min(size, limit)

            kdata_list = []

            if config['support_since'] and start:
                kdatas = ccxt_exchange.fetch_ohlcv(entity.code,
                                                   timeframe=self.ccxt_trading_level,
                                                   since=int(start.timestamp() * 1000))
            else:
                kdatas = ccxt_exchange.fetch_ohlcv(entity.code,
                                                   timeframe=self.ccxt_trading_level,
                                                   limit=limit)

            for kdata in kdatas:
                current_timestamp = kdata[0]
                if self.level == IntervalLevel.LEVEL_1DAY:
                    current_timestamp = to_time_str(current_timestamp)

                if self.level >= IntervalLevel.LEVEL_1DAY:
                    kdata_id = "{}_{}".format(entity.id, current_timestamp, fmt=TIME_FORMAT_DAY)
                else:
                    kdata_id = "{}_{}".format(entity.id, current_timestamp, fmt=TIME_FORMAT_ISO8601)

                kdata_json = {
                    'id': kdata_id,
                    'entity_id': entity.id,
                    'code': entity.code,
                    'name': entity.name,
                    'timestamp': to_pd_timestamp(current_timestamp),
                    'open': kdata[1],
                    'high': kdata[2],
                    'low': kdata[3],
                    'close': kdata[4],
                    'volume': kdata[5],
                    'provider': 'ccxt',
                    'level': self.level.value
                }
                kdata_list.append(kdata_json)

            if kdata_list:
                df = pd.DataFrame.from_records(kdata_list)
                df_to_db(data_schema=self.data_schema, df=df, provider=self.provider,
                         force_update=True)

        else:
            self.logger.warning("exchange:{} not support fetchOHLCV".format(entity.exchange))


if __name__ == '__main__':
    CoinKdataRecorder(exchanges=['huobipro'], level=IntervalLevel.LEVEL_1DAY, real_time=False).run()
