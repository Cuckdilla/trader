import sys, configparser, websocket, json
import pandas as pd

from components.logger import Logger
from components.candles import Candles
from components.strategies import Strategies
from components.signals import Signals
from components.bookmaker import Bookie

log = Logger(loglevel=3, persist=True, rotation_interval=1)
log.info("Application starting")

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
except Exception as e:
    log.error("Unable to get all required parameters from configuration file")
    print(e)
    sys.exit(1)

#
# Main
#
signals = ["BB", "STOCH"]
last_candle = []


#
# Websocket
#

def open_socket():

    socket_url = "wss://stream.binance.com:9443/ws/{}@kline_{}".format(token.lower(), interval)
    log.info("Connection to websocket ({})".format(socket_url))
    
    ws = websocket.WebSocketApp(socket_url, on_open=websocket_opened, on_close=websocket_closed, on_message=websocket_message)
    ws.run_forever()

def websocket_opened(ws):
    log.info("Connected!")

def websocket_closed(ws, close_status_code, close_message):
    log.info("Connection to websocket closed!")
    log.debug('close_status_code: {} close_message: {}'.format(close_status_code, close_message))

def websocket_message(ws, message):

    data = json.loads(message)

    candle = data["k"]

    candle_opentime     = candle["t"]
    candle_open         = float(candle["o"])
    candle_close        = float(candle["c"])
    candle_high         = float(candle["h"])
    candle_low          = float(candle["l"])
    candle_volume       = float(candle["n"])
    candle_closetime    = candle["T"]
    
    if candle["x"]:

        # Candle has closed

        last_candle = pd.DataFrame([[candle_opentime, candle_open, candle_high, candle_low, candle_close, candle_volume, candle_closetime]], columns=candles.chart_columns)
        last_candle["closetime"] = pd.to_datetime(last_candle["closetime"], unit='ms')
        last_candle["opentime"] = pd.to_datetime(last_candle["opentime"], unit='ms')

        if last_candle["opentime"].iat[-1] == candles.chart["opentime"].iat[-1]:
            log.warning("The last candle has the same opening time as the last entry in the chart. This is expected for the first closing candle received via websocket.")
            log.warning("Dropping the last row of the chart")

            candles.chart.drop(index=candles.chart.index[-1], axis=0, inplace=True)
            
        log.debug("Appending latest candle to the chart")

        candles.chart = candles.chart.append(last_candle, ignore_index=True)

        log.debug("Candle closed at {}. Open: {}, High: {}, Low: {}".format(candle_close, candle_open, candle_high, candle_low))

        # Indicators
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
        


        if len(signals.conditions) != 0:

            signals_score = 0
            print("\n")

            for k,v in signals.conditions.items():
                print("Signal: {}".format(k))
                print("Action: {}".format(v["action"]))
                print("Score: {}".format(v["score"]))
                print("Reason: {}".format(v["reason"]))
                print("Values: {}".format(v["data"]))

                signals_score += v["score"]
                print("\n")

            print("Total score: {}".format(signals_score))
            print("Market: Bullish") if signals.market_is_bullish else print("Market: Bearish")

        else:
                
            print("\nNo signals\n")
        

        print(candles.chart)

if __name__ == "__main__":    
    candles     = Candles(token=token, interval=interval, timeframe=timeframe, heikinashi=heikinashi, logger=log)
    strategies  = Strategies(log)
    signals     = Signals(log)
    bookie      = Bookie(signals)

    # Start websocket
    open_socket()

