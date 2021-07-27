import websocket, datetime, json

from binance.client import Client
from matplotlib.pyplot import savefig

import pandas as pd
import numpy as np
import mplfinance as mpf

class Candles:

    def __init__(self, token: str, interval: int, timeframe=None, heikinashi=False, logger=None):    

        if logger is None:
            raise Exception("An instance of the logger class is required.")

        self.token              = token
        self.interval           = interval
        self.timeframe          = timeframe
        self.heikinashi         = heikinashi

        self.log                = logger        
        self.client             = Client()
        self.ws                 = None
        self.last_candle        = pd.Series()

        self.chart_columns      = ["opentime", "open", "high", "low", "close", "volume", "closetime"]
        self.create_chart()


    # Returns market data from Binance, using the instanitated token, interval and timeframe
    def get_historical_klines(self):
        return self.client.get_historical_klines(self.token, self.interval, self.timeframe)

    # Creates a pandas dataframe, representing the chart, or table of "candles".
    def create_chart(self):
        
        self.log.info("Creating initial chart")

        klines = self.get_historical_klines()
        chart = []

        if self.heikinashi:
            
            """

            Heikin Ashi Formula:

            High = Maximum of High, Open, or Close (whichever is highest)
            Low = Minimum of Low, Open, or Close (whichever is lowest)

            Open = [Open (previous bar) + Close (previous bar)] /2
            Close = (Open + High + Low + Close) / 4

            """

            self.log.info("Heikin Ashi is enabled. Creating Heikin Ashi chart")

            for i, data in enumerate(klines):

                opentime    = data[0]
                openprice   = float(data[1])
                highprice   = float(data[2])
                lowprice    = float(data[3])
                closeprice  = float(data[4])
                volume      = float(data[5])
                closetime   = data[6]

                if i == 0:

                    openprice   = (openprice + closeprice) / 2
                    closeprice  = (openprice + highprice + lowprice + closeprice) / 4
                
                else:
                    
                    openprice   = (float(klines[i-1][1]) + float(klines[i-1][4])) / 2
                    highprice   = max([float(data[1]), float(data[2]), float(data[4])])
                    lowprice    = min([float(data[1]), float(data[3]), float(data[4])])
                    closeprice  = (float(data[1]) + float(data[2]) + float(data[3]) + float(data[4])) / 4
                

                upperwick    = highprice - closeprice
                lowerwick    = openprice - lowprice
                bodysize     = closeprice - openprice

                chart.append([opentime, openprice, highprice, lowprice, closeprice, volume, closetime, bodysize, upperwick, lowerwick])


            self.chart = pd.DataFrame(chart, columns=self.chart_columns+["bodysize", "upperwick", "lowerwick"])
            
        else:

            self.log.info("Creating chart")

            for data in klines:
                chart.append([
                    data[0],
                    float(data[1]),
                    float(data[2]),
                    float(data[3]),
                    float(data[4]),
                    float(data[5]),
                    data[6]
                ])

            self.chart = pd.DataFrame(chart, columns=self.chart_columns)


        # Finalize chart by converting epochs to datetime objects.
        # Set the dataframe index to be "opentime", and drop that from the columns
        self.chart["closetime"] = pd.to_datetime(self.chart["closetime"], unit='ms')
        self.chart["opentime"] = pd.to_datetime(self.chart["opentime"], unit='ms')

    # Exports a plotted pandas dataframe to png format. 
    def draw_chart(self, chart, type="candle", volume=False, style="binance", filename=None):

        chart = chart.set_index(pd.DatetimeIndex(self.chart["opentime"]))
        chart = chart.drop(["opentime"], axis=1)

        if filename is None:
            filename = "exports/" + str(datetime.datetime.now()) + ".png"
        
        self.log.debug("Exporting chart: {}".format(filename))

        return mpf.plot(chart, type=type, volume=volume, style=style, savefig=filename)



