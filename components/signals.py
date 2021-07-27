import pandas as pd

class Signals:

    def __init__(self, candles, strategies, signals, logger=None):

        if logger is None:
            raise Exception("An instance of the logger class is required.")

        
        self.candles    = candles
        self.strategies = strategies
        self.signals    = signals
        self.log        = logger

        self.conditions = []


        self.check_signals()




    def check_signals(self):

        chart = self.candles 








    def add_condition(self, condition):
        pass


    def check_heikinashi_wicks(self):
        """
        If a candle has no upper wick, this could mean it is time to sell
        If it has no lower wick, it could mean time to buy.
        """
        if self.candles.heikinashi:
            for index, row in self.candles.chart.iterrows():
                if row["upperwick"] == 0:
                    print("NO UPPER WICK!")
                elif row["lowerwick"] == 0:
                    print("NO LOWER WICK!")
        
    def crypto_buy_in(self):
        """
        EMA-8-close
        EMA-13-close
        EMA-21-close
        EMA-55-close

        When EMA-21 crosses over EMA-55
        AND
        EMA-8 is above EMA-13

        BUY

        """

        buy = pd.DataFrame()

        self.strategies.calculate_exponential_moving_average(8, "close")
        self.strategies.calculate_exponential_moving_average(13, "close")
        self.strategies.calculate_exponential_moving_average(21, "close")
        self.strategies.calculate_exponential_moving_average(55, "close")

        ema8    = "EMA-8-close"
        ema13   = "EMA-13-close"
        ema21   = "EMA-21-close"
        ema55   = "EMA-55-close"
        
        if ema8 in self.candles.chart and ema13 in self.candles.chart and ema21 in self.candles.chart and ema55 in self.candles.chart:

            for index, row in self.candles.chart.iterrows():
                if row[ema21] > row[ema55] and row[ema8] > row[ema13]:
                    buy = buy.append(row)
        
        print(buy)