import pandas as pd

from zvt.contract.api import df_to_db
from zvt.contract.recorder import Recorder
from zvt_coin.api import get_coin_exchange, COIN_EXCHANGES
from zvt_coin.domain import Coin


class CoinMetaRecorder(Recorder):
    provider = 'ccxt'
    data_schema = Coin

    def __init__(self, batch_size=10, force_update=False, sleeping_time=1, exchanges=COIN_EXCHANGES) -> None:
        super().__init__(force_update, sleeping_time)
        self.exchanges = exchanges

    def run(self):
        for exchange_str in self.exchanges:
            exchange = get_coin_exchange(exchange_str)
            try:
                markets = exchange.fetchMarkets()
                df = pd.DataFrame()

                # markets有些为key=symbol的dict,有些为list
                markets_type = type(markets)
                if markets_type != dict and markets_type != list:
                    self.logger.exception("unknown return markets type {}".format(markets_type))
                    return

                aa = []
                for market in markets:
                    if not market['active']:
                        continue
                    if markets_type == dict:
                        name = market
                        code = market

                    if markets_type == list:
                        code = market['symbol']
                        name = market['symbol']

                    aa.append(market)

                    security_item = {
                        'id': '{}_{}_{}'.format('coin', exchange_str, code),
                        'entity_id': '{}_{}_{}'.format('coin', exchange_str, code),
                        'exchange': exchange_str,
                        'entity_type': 'coin',
                        'code': code,
                        'name': name
                    }

                    df = df.append(security_item, ignore_index=True)

                # 存储该交易所的数字货币列表
                if not df.empty:
                    df_to_db(df=df, data_schema=self.data_schema, provider=self.provider, force_update=True)
                self.logger.info(f"init_markets for {exchange_str} success")
            except Exception:
                self.logger.exception(f"init_markets for {exchange_str} failed")


__all__ = ["CoinMetaRecorder"]

if __name__ == '__main__':
    CoinMetaRecorder(exchanges=['huobipro']).run()
