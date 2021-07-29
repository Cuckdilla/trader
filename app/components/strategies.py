
import configparser
from components.logger import Logger

class Strategies:

    def __init__(self, configfile="strategies.ini", loglevel=3):

        self.log        = Logger(name="strategies", loglevel=loglevel)

        self.sources    = ["open", "high", "low", "close", "volume"]
        self.config     = configparser.ConfigParser()
        self.configfile = configfile
        
    def get_config(self):
        self.config.read(f"config/{self.configfile}")
        

#
# Helper functions
#

    def is_valid_source(self, source):
        return source in self.sources

#
# SMA
#

    def calculate_simple_moving_average(self, chart, period, source):

        self.log.debug("Calculating SMA")

        if self.is_valid_source(source):
            column_name = "SMA-{}-{}".format(period, source)
            chart[column_name] = chart[source].rolling(period).mean()

#
# EMA
#

    def calculate_exponential_moving_average(self, chart, period, source):
        
        self.log.debug("Calculating EMA")

        if self.is_valid_source(source):
            column_name = "EMA-{}-{}".format(period, source)                
            chart[column_name] = chart[source].ewm(span=period, adjust=False).mean()


#
# Bollinger Bands
#

    def calculate_bollinger_bands(self, chart):

        self.log.debug("Calculating Bollinger Bands")
        
        # Check if the desired SMA is already calculated
        self.calculate_simple_moving_average(chart, 20, "close")

        std            = chart["close"].rolling(20).std(ddof=0)
        chart["BBU"]   = chart["SMA-20-close"] + 2*std
        chart["BBL"]   = chart["SMA-20-close"] - 2*std

 
#
# Stochastic RSI
#

    def calculate_stochastic_rsi(self, chart, window=14):

        self.log.debug("Calculating Stochastic RSI")

        high = chart["high"].rolling(window).max()
        low  = chart["low"].rolling(window).min()
        
        chart["stoch_k"] = k_line = (chart["close"] - low)*100 / (high - low)
        chart["stoch_d"] = d_line = k_line.rolling(3).mean()

#
# MACD
#

    def calculate_macd(self, chart):
        
        self.log.debug("Calculating MACD")
        
        ema12 = chart["close"].ewm(span=12, adjust=False).mean()
        ema26 = chart["close"].ewm(span=26, adjust=False).mean()
        
        chart["MACD"]   = ema12 - ema26
        chart["MACD-S"] = chart["MACD"].ewm(span=9, adjust=False).mean()

