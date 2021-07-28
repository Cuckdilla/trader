

class Bookie:

    def __init__(self, signals):
        
        self.signals = signals

    
    def evaluate_trading_opportunity(self):
        pass


    def place_order(self, type):

        if type == "buy":
            print("Placing buy order")
        
        if type == "sell":
            print("Placing sell order")