import pandas as pd
import datetime

from components.logger import Logger

class Signals:

    def __init__(self, loglevel=3):
   
        self.log                = Logger(name="signals", loglevel=loglevel)

        # Signals as Pandas dataframe
        self.signals_columns    = ["Name", "Type", "Action", "Description", "Weight", "Values"]
        self.signals            = pd.DataFrame(columns=self.signals_columns)

        self.market_is_bullish = False



    def check(self, chart):

        self.stochastic_rsi(chart)
        self.trading_volume(chart)
        self.moving_average(chart)
        self.macd(chart)

    def add_signal(self, signal):

        if signal[0] not in self.signals["Name"].values:

            self.signals_columns    = ["Name", "Action", "Type", "Description", "Weight", "Values"]
            signals                 = pd.DataFrame([signal], columns=self.signals_columns)

            self.signals = self.signals.append(signals, ignore_index=True)

            self.log.debug("Added signal {}".format(signal[0]))

    def drop_signal(self, signal_name):

        if signal_name in self.signals["Name"].values:
            signal_index = self.signals[self.signals["Name"] == signal_name].index
            self.signals.drop(signal_index, inplace=True)

            self.log.debug("Dropped signal {}".format(signal_name))


    def record_signal(self, signal_name, signal):
        d = datetime.datetime.now()
        
        entry = "{}: {} {}".format(d, signal_name, signal)
        with open("signal-history.log", "a+") as h:
            h.write(entry)

        self.signals_history[d] = {signal_name: signal}

#
# STOCHASTIC RSI
#

    def stochastic_rsi(self, chart):

        self.log.debug("Evaluating indicator: Stochastic RSI")

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
                self.add_signal([signal_name, "Buy", "Oscillator", "K and D lines are below lower threshold (20)", 1, k])
            else:
                self.drop_signal(signal_name)

            # Above threshold of 80, indicates RSI oversold
            signal_name = "stochastic_overbought"
            if k > 80 and d > 80:
                self.add_signal([signal_name, "Sell", "Oscillator", "K and D lines are above upper threshold (80)", 1, k])
            else:
                self.drop_signal(signal_name)


            # K line higher than D line indicates a bullish market
            signal_name = "stochastic_bullish_market"
            if k > d:
                self.add_signal([signal_name, "Neutral", "Oscillator", "K line is above D, indicating bullish market", 1, k])

                self.market_is_bullish = True
            else:
                self.drop_signal(signal_name)


            # Bearish market
            signal_name = "stochastic_bearish_market"
            if k < d:
                self.add_signal([signal_name, "Neutral", "Oscillator", "K line is below D, indicating bearish market", 1, k])                

                self.market_is_bullish = False
            else:
                self.drop_signal(signal_name)

            # Bullish crossover 
            signal_name = "stochastic_bullish_crossover"
            if k > d and previous_k < previous_d:
                self.add_signal([signal_name, "Buy", "Oscillator", "K crossed over D", 1, k])

            else:
                self.drop_signal(signal_name)

            # Bearish crossover 
            signal_name = "stochastic_bullish_crossover"
            if k < d and previous_k > previous_d:
                self.add_signal([signal_name, "Sell", "Oscillator", "D crossed over K", 1, k])

            else:
                self.drop_signal(signal_name)

        else:
            self.log.warning("Chart does not have Stocastic indicators.")


#
# Moving Average
#

    def moving_average(self, chart):

        self.log.debug("Evaluating indicator: Simple Moving Average")
        
        moving_averages = ["SMA-200-close", "SMA-100-close", "SMA-50-close", "SMA-20-close"]
        last_close = chart["close"].iat[-1]
        previous_close = chart["close"].iat[-2]

        for ma in moving_averages:
                
            if ma in chart:
                
                # Price above average
                signal_name = f"price_above_{ma}"

                if last_close > chart[ma].iat[-1]:
                    self.log.debug(f"Price is higher than {ma}")
                    
                    self.add_signal([signal_name, "Neutral", "Average", f"Closing higher than Moving Average ({ma})", 1, chart[ma].iat[-1]])

                else:
                    self.log.debug(f"Price is lower than {ma}")
                    self.drop_signal(signal_name)

                # Crossover
                signal_name = f"price_crossed_over_{ma}"
                if last_close > chart[ma].iat[-1] and previous_close < chart[ma].iat[-2]:
                    self.log.debug(f"Price crossed over {ma}")
                    self.add_signal([signal_name, "Neutral", "Average", f"Price crossed over {ma}", 1, chart[ma].iat[-1]])
                else:
                    self.log.debug(f"Price is lower than {ma}")
                    self.drop_signal(signal_name)


#
# RELATIVE STRENGTH INDEX
#


#
# VOLUME
#

    def trading_volume(self, chart, sma="SMA-20-volume"):

        self.log.debug("Evaluating indicator: Trading volume")

        signal_name = f"volume_above_{sma}"

        if sma in chart:
            self.log.debug("Volume: {} ({}: {})".format(chart["volume"].iat[-1], sma, chart["SMA-20-volume"].iat[-1]))
            if chart["volume"].iat[-1] > chart[sma].iat[-1]:
                self.add_signal([signal_name, "Neutral", "Average", f"Trading volume is higher than {sma}", 1, chart["volume"].iat[-1]])

        else:
            self.log.warning(f"{sma} has not yet been calculated.")


#
# MACD
#

# https://www.investopedia.com/terms/m/macd.asp

    def macd(self, chart):
        
        self.log.debug("Evaluating indicator: MACD")

        # Indicator exists in chart
        if "MACD" in chart and "MACD-S" in chart:
            
            # Get latest indicator values
            macd            = chart["MACD"].iat[-1]
            signal          = chart["MACD-S"].iat[-1]

            previous_macd   = chart["MACD"].iat[-2]
            previous_signal = chart["MACD-S"].iat[-2]


            # Bullish crossover 
            signal_name = "macd_bullish_crossover"
            if macd > signal and previous_macd < previous_signal:
                self.log.debug("MACD crossed over the signal line")
                self.add_signal([signal_name, "Buy", "Oscillator", "MACD crossed over the signal line", 1, macd]) 
            else:
                self.drop_signal(signal_name)

            # Bearish crossover 
            signal_name = "macd_bearish_crossover"
            if macd < signal and previous_macd > previous_signal:
                self.log.debug("Signal line crossed over MACD")
                self.add_signal([signal_name, "Sell", "Oscillator", "The signal line crossed over the MACD", 1, macd]) 
            else:
                self.drop_signal(signal_name)


#
# Bollinger Bands
#

