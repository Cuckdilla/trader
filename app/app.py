import sys, configparser, websocket, json, threading
import pandas as pd

from components.logger import Logger
from components.candles import Candles
from components.strategies import Strategies
from components.signals import Signals
from components.bookmaker import Bookie


#
# Configuration
#

config = configparser.ConfigParser()
config.read("config/config.ini")

try:
    token       = config["trading"]["token"]
    interval    = config["trading"]["interval"]
    timeframe   = config["trading"]["timeframe"]
    heikinashi  = config["trading"].getboolean("heikinashi")

    loglevel    = config["logging"].getint("loglevel")

except Exception as e:
    print(e)
    sys.exit("Unable to get all required parameters from configuration file")

try:
    candles     = Candles(token, interval, timeframe, heikinashi, loglevel)
    strategies  = Strategies(loglevel=loglevel)
    signals     = Signals(loglevel=loglevel)
    bookie      = Bookie(signals)
    log         = Logger(name="app", loglevel=loglevel)
except:
    sys.exit("Could not instantiate all classes")


#
# Websocket
#

def open_socket():

    log.info("Connecting to Binance..")
    socket_url = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(token.lower(), interval)
    
    ws = websocket.WebSocketApp(socket_url, on_open=websocket_opened, on_close=websocket_closed, on_message=websocket_message)
    ws.run_forever()

def websocket_opened(ws):
    log.info("Connected!")

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

    # Indicators -- 
    strategies.calculate_bollinger_bands(candles.chart)
    strategies.calculate_stochastic_rsi(candles.chart)
    strategies.calculate_simple_moving_average(candles.chart, 200, "close")
    strategies.calculate_simple_moving_average(candles.chart, 100, "close")
    strategies.calculate_simple_moving_average(candles.chart, 50, "close")
    strategies.calculate_simple_moving_average(candles.chart, 20, "close")
    strategies.calculate_simple_moving_average(candles.chart, 20, "volume")
    strategies.calculate_macd(candles.chart)

    signals.stochastic_rsi(candles.chart)
    signals.trading_volume(candles.chart)
    signals.moving_average(candles.chart)
    signals.macd(candles.chart)


    if signals.signals.count != 0:
        for index, signal in signals.signals.iterrows():
            log.info("{} (weight: {})".format(signal["Description"], signal["Weight"]))

    log.info("Candle closed at {}. O: {}, H: {}, L: {}".format(candle_close, candle_open, candle_high, candle_low))

    log.info("Market is bullish") if signals.market_is_bullish else log.info("Market is bearish")
    log.info("Total weight of signals: {}".format(signals.signals["Weight"].sum()))

if __name__ == "__main__":

    open_socket()
