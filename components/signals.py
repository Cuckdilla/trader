import pandas as pd
import datetime

class Signals:

    def __init__(self, logger=None):

        if logger is None:
            raise Exception("An instance of the logger class is required.")
   
        self.log                = logger
        self.conditions         = {}
        self.signals_history    = {}

        # List required conditions to flag a buy or sell.
        # All conditions must be met.
        self.required_conditions = {}

        self.market_is_bullish = False

    def add_condition(self, signal_name, signal):
        self.log.debug(f"Checking if {signal_name} already exists")
        
        if signal_name in self.conditions:
            self.log.debug(f"{signal_name} already in conditions")
        
        else:
            self.log.debug("Adding signal")
            self.conditions[signal_name] = signal
            self.record_signal(signal_name, signal)


    def del_condition(self, signal_name):
        
        if signal_name in self.conditions:

            self.log.debug(f"Removing aged signal {signal_name}")
            del self.conditions[signal_name]

    def record_signal(self, signal_name, signal):
        d = datetime.datetime.now()
        
        with open("signal-history.log", "a+") as h:
            h.write(f'{d}: {signal_name} ({signal})')

        self.signals_history[d: {signal_name: signal}]

#
# STOCHASTIC RSI
#

    def stochastic_buy_signal(self, chart):

        self.log.info("Evaluating: Stochastic RSI indicator")

        # Indicator exists in chart
        if "stoch_k" in chart and "stoch_d" in chart:
            
            # Get latest indicator values
            k           = chart["stoch_k"].iat[-1]
            d           = chart["stoch_d"].iat[-1]

            previous_k  = chart["stoch_d"].iat[-2]
            previous_d  = chart["stoch_d"].iat[-2]


            # Below threshold of 20, indicates RSI oversold
            signal_name = "stochastic_oversold"
            if k < 20 and d < 20:
                self.add_condition(signal_name, { "action": "buy", "reason": "Both K and D line are below 20", "stoch_k": k, "stoch_d": d, "score": 3 })
            else:
                self.del_condition(signal_name)


            # K line higher than D line indicates a bullish market
            signal_name = "stochastic_bullish_market"
            if k > d:
                self.add_condition(signal_name, { "action": "none", "reason": "K line is above the D line",  "stoch_k": k, "stoch_d": d, "score": 1 })
                self.market_is_bullish = True
            else:
                self.del_condition(signal_name)


            # Bearish market
            signal_name = "stochastic_bearish_market"
            if k < d:
                self.add_condition(signal_name, { "action": "none", "reason": "K line is below the D line",   "stoch_k": k, "stoch_d": d, "score": 1 })
                self.market_is_bullish = False
            else:
                self.del_condition(signal_name)

            # Bullish crossover 
            signal_name = "stochastic_bullish_crossover"
            if k > d and previous_k < previous_d:
                self.add_condition(signal_name, { "action": "buy", "reason": "K crossed over D",   "stoch_k": k, "stoch_d": d, "score": 6 })                
            else:
                self.del_condition(signal_name)

            # Bearish crossover 
            signal_name = "stochastic_bullish_crossover"
            if k < d and previous_k > previous_d:
                self.add_condition(signal_name, { "action": "sell", "reason": "D crossed over K",   "stoch_k": k, "stoch_d": d, "score": 6 })            
            else:
                self.del_condition(signal_name)

        else:
            self.log.warning("Chart does not have Stocastic indicators.")


#
# RELATIVE STRENGTH INDEX
#


#
# VOLUME
#


    def trading_volume_moving_average(self, chart):

        self.log.info("Evaluating: Trading volume")

        signal_name = "volume_above_200_ma"

        if "SMA-200-volume" in chart:
            
            if chart["volume"].iat[-1] > chart["SMA-200-volume"].iat[-1]:
                self.add_condition(signal_name, { "action": "buy", "reason": "Trading volume is above SMA-200", "volume": chart["volume"].iat[-1], "SMA-200-volume": chart["SMA-200-volume"].iat[-1], "score": 2 })
  
        else:
            self.log.warning("SMA-200-volume has not yet been calculated.")


#
# MACD
#

# https://www.investopedia.com/terms/m/macd.asp



#
# Bollinger Bands
#

