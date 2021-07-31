import sys, configparser, websocket, json, threading, argparse

import pandas as pd

from components.logger import Logger
from components.candles import Candles
from components.indicators import Indicators
from components.signals import Signals
from components.bookmaker import Bookie


#
# Command line options
#

parser = argparse.ArgumentParser(description='Trading bot')
parser.add_argument('-p','--pair', help='pair paid, i.e ETHUSDT', required=False)
parser.add_argument('-i','--interval', help='Candle frequency, i.e 1m, 5m, 24h', required=False)
parser.add_argument('-t','--timeframe', help='How far back the data goes. Binance specific string such as "24 hours ago UTC', required=False)
parser.add_argument('-x','--heikinashi', help='Create chart using Heikin Ashi', required=False)
parser.add_argument('-l','--loglevel', help='0 = INFO, 3 = DEBUG', required=False)
parser.add_argument('-b','--backtest', help='Simulate trades', required=False)
args = vars(parser.parse_args())


#
# Configuration
#

config = configparser.ConfigParser()
config.read("config/config.ini")

print("Loading configuration..")

try:

    # Prioritize command line arguments over configuration file.
    # Since we do not require any arguments, we rely on there being a config file.

    pair        = str(args["pair"]) if args["pair"] is not None else config["trading"]["pair"]
    interval    = str(args["interval"]) if args["interval"] is not None else config["trading"]["interval"]
    timeframe   = str(args["timeframe"]) if args["timeframe"] is not None else config["trading"]["timeframe"]
    heikinashi  = bool(args["heikinashi"]) if args["heikinashi"] is not None else config["trading"].getboolean("heikinashi")
    loglevel    = int(args["loglevel"]) if args["loglevel"] is not None else config["logging"].getint("loglevel")

    # Backtesting not yet implemented
    backtest    = bool(args["backtest"]) if args["backtest"] is not None else False

except Exception as e:
    print(e)
    sys.exit("Unable to load configuration")

try:
    candles     = Candles(pair, interval, timeframe, heikinashi, loglevel)
    indicators  = Indicators(loglevel=loglevel)
    signals     = Signals(loglevel=loglevel)
    bookie      = Bookie(signals)
    log         = Logger(name="app", loglevel=loglevel)
except:
    sys.exit("Could not instantiate all classes")


#
# Websocket
#

def open_socket():

    socket_url = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(pair.lower(), interval)
    
    ws = websocket.WebSocketApp(socket_url, on_open=websocket_opened, on_close=websocket_closed, on_message=websocket_message)
    ws.run_forever()

def websocket_opened(ws):
    log.info("Connected to Binance")

def websocket_closed(ws, close_status_code, close_message):
    log.info("Websocket connection closed!")
    log.debug('close_status_code: {} close_message: {}'.format(close_status_code, close_message))

def websocket_message(ws, message):

    data = json.loads(message)

    candle = data["k"]
    
    # When candle is closed
    if candle["x"]:

        # Create a new thread to handle the processing of the chart, indicators, and signaling
        t = threading.Thread(target=candle_closed, kwargs=candle)
        t.start()


def candle_closed(**candle):

    candle_opentime     = candle["t"]
    candle_open         = float(candle["o"])
    candle_close        = float(candle["c"])
    candle_high         = float(candle["h"])
    candle_low          = float(candle["l"])
    candle_volume       = float(candle["n"])
    candle_closetime    = candle["T"]

    last_candle = pd.DataFrame([[candle_opentime, candle_open, candle_high, candle_low, candle_close, candle_volume, candle_closetime]], columns=candles.chart_columns)
    last_candle["closetime"] = pd.to_datetime(last_candle["closetime"], unit='ms')
    last_candle["opentime"] = pd.to_datetime(last_candle["opentime"], unit='ms')

    if last_candle["opentime"].iat[-1] == candles.chart["opentime"].iat[-1]:
        log.warning("Opening time matches the last entry in the chart. This is expected for the first closing candle received via websocket.")
        log.warning("Dropping the last row of the chart.")

        candles.chart.drop(index=candles.chart.index[-1], axis=0, inplace=True)
        
    log.debug("Appending latest candle to the chart")
    

    candles.chart = candles.chart.append(last_candle, ignore_index=True)

    indicators.calculate(candles.chart)

    signals.check(candles.chart)
    print("\n")

    log.info("Candle closed at {}. O: {}, H: {}, L: {} V: {}".format(candle_close, candle_open, candle_high, candle_low, candle_volume))
    log.info("Market is bullish") if signals.market_is_bullish else log.info("Market is bearish")
    log.info("Total weight of signals: {}".format(signals.signals["Weight"].sum()))

    print("\n")
    
    if signals.signals.count != 0:
        for index, signal in signals.signals.iterrows():
            log.info("[{}] {} (weight: {})".format(signal["Action"], signal["Description"], signal["Weight"]))

    print("\n")

    print(candles.chart.tail(1))
    
if __name__ == "__main__":

    log.info(f"Token pair: {pair}, Interval: {interval}, Timeframe: {timeframe}, Heikin Ashi: {heikinashi}")
    open_socket()
