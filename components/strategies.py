
class Strategies:

    def __init__(self, chart=None, logger=None):

        if chart is None:
            raise Exception("No valid chart was passed to the Strategies class")

        if logger is None:
            raise Exception("An instance of the logger class is required.")

        self.chart  = chart
        self.log    = logger        


        self.sources = ["open", "high", "low", "close"]

        #self.calculate_bollinger_bands()
        #self.calculate_stochastic_rsi()
        

#
# Helper functions
#

    def is_valid_source(self, source):
        return source in self.sources

#
# SMA
#

    def calculate_simple_moving_average(self, period, source):

        self.log.debug("Calculating SMA")

        if self.is_valid_source(source):
            column_name = "SMA-{}-{}".format(period, source)
            self.chart[column_name] = self.chart[source].rolling(period).mean()

#
# EMA
#

    def calculate_exponential_moving_average(self, period, source):
        
        self.log.debug("Calculating EMA")

        if self.is_valid_source(source):
            column_name = "EMA-{}-{}".format(period, source)                
            self.chart[column_name] = self.chart[source].ewm(span=period, adjust=False).mean()

#
# RSI
#
    def calculate_relative_strength_index(self, period):
        if self.chart is None:
            return None

#
# Bollinger Bands
#

    def calculate_bollinger_bands(self):

        self.log.debug("Calculating Bollinger Bands")
        
        # Check if the desired SMA is already calculated
        if "SMA-20-close" not in self.chart:
            self.calculate_simple_moving_average(20, "close")

        std                 = self.chart["close"].rolling(20).std(ddof=0)
        self.chart["BBU"]   = self.chart["SMA-20-close"] + 2*std
        self.chart["BBL"]   = self.chart["SMA-20-close"] - 2*std


    
#
# Stochastic RSI
#

    def calculate_stochastic_rsi(self):

        self.log.debug("Calculating Stochastic RSI")

        high14 = self.chart["high"].rolling(14).max()
        low14  = self.chart["low"].rolling(14).min()
        
        self.chart["stoch_k"] = k_line = (self.chart["close"] - low14)*100 / (high14 - low14)
        self.chart["stoch_d"] = d_line = k_line.rolling(3).mean()

#
# MACD
#

    def calculate_macd(self):
        
        self.log.debug("Calculating MACD")
        
        ema12 = self.chart["close"].ewm(span=12, adjust=False).mean()
        ema26 = self.chart["close"].ewm(span=26, adjust=False).mean()
        
        self.chart["MACD"] = ema12 - ema26
        self.chart["MACD-S"] = self.chart["MACD"].ewm(span=9, adjust=False).mean()

