from binance import Client
import multiprocessing
import time


def getpair(pair, client, fetch_time):
    print(pair)
    klines = client.futures_historical_klines(pair, Client.KLINE_INTERVAL_5MINUTE, fetch_time)
    klines = [','.join([str(k) for k in i[:6]]) for i in klines]
    s = 'timestamp,open,high,low,close,volume\n'
    for candle in klines:
        s += candle + '\n'

    with open(f'data/{pair}.csv', 'w+') as f:
        f.write(s)


if __name__ == '__main__':
    client = Client()
    fetch_time = "365 days ago"

    allpairs = [i['symbol'] for i in client.futures_exchange_info()['symbols'] if i['symbol'].endswith('USDT')]
    print(allpairs)
    # allpairs = ['BTCUSDT', 'ETHUSDT', 'ALGOUSDT']

    pool = multiprocessing.Pool(processes=5)
    for pair in allpairs:
        pool.apply_async(getpair, args=(pair, client, fetch_time))

    pool.close()
    pool.join()

