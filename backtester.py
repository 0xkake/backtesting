import matplotlib.pyplot as plt
import pandas as pd


class Env:
    def __init__(self, df):
        self.default_pos = {'size': 0, 'side': None, 'entries': [], 'sl': None, 'tp': None}
        self.pos = self.default_pos
        self.df = df.itertuples()
        self.row = next(self.df)
        self.done = False

        self.pnl = 0
        self.time = -1
        self.unrealised_pnl = 0
        self.pnl_list = []
        self.price_list = []
        self.trades = []

        self.fee = 0.1

    def _get_mean_entry(self):
        return sum(self.pos['entries']) / len(self.pos['entries']) 

    def buy(self, amount=1, sl=None, tp=None):
        self.pos = {'size': self.pos['size']+amount, 'entry_time': self.time,
                    'side': 'long', 'entries': self.pos['entries']+[self.row.close],
                    'sl': sl, 'tp': tp}

    def sell(self, amount=1, sl=None, tp=None):
        self.pos = {'size': self.pos['size']-amount, 'entry_time': self.time,
                    'side': 'short', 'entries': self.pos['entries']+[self.row.close],
                    'sl': sl, 'tp': tp}

    def exit(self, amount=1, _exit=None):
        if self.pos['side'] == 'long': amount = min(amount, self.pos['size'])
        else: amount = max(-amount, self.pos['size'])
        if not _exit: exit = self.row.close
        else: exit = _exit
        entry = self._get_mean_entry()

        pnl = (((exit - entry) / entry) * 100 - self.fee) * self.pos['size'] 
        self.pnl += pnl
        self.trades.append({'entry_time': self.pos['entry_time'], 'exit_time': self.time, 'side': self.pos['side'], 'entry': entry, 'exit': exit, 'amount': amount, 'pnl': pnl})
        self.pos['size'] -= amount
        if abs(self.pos['size']) < 0.01:
            self.pos = self.default_pos
            self.unrealised_pnl = 0

    def step(self):
        try: self.row = next(self.df)
        except StopIteration:
            self.done = True

        if self.pos['side'] == 'long':
            self.unrealised_pnl = ((self.row.close - self._get_mean_entry()) / self._get_mean_entry()) * 100
            if self.pos['sl'] and self.pos['sl'] > self.row.low: self.exit(100, _exit=self.pos['sl'])
            if self.pos['tp'] and self.pos['tp'] < self.row.high: self.exit(100, _exit=self.pos['tp'])
            
        elif self.pos['side'] == 'short':
            self.unrealised_pnl = ((self._get_mean_entry() - self.row.close) / self.row.close) * 100
            if self.pos['sl'] and self.pos['sl'] < self.row.high: self.exit(100, _exit=self.pos['sl'])
            if self.pos['tp'] and self.pos['tp'] > self.row.low: self.exit(100, _exit=self.pos['tp'])
            
        self.time += 1
        self.pnl_list.append(self.pnl)
        self.price_list.append(self.row.close)

        return self.row

    def plot(self, plot_pnl=True, plot_close=True, plot_trades=True):
        price_pct = [(c/self.price_list[0])*100-100 for c in self.price_list]
        if plot_pnl:
            plt.plot(self.pnl_list, label='PnL')
        if plot_close:
            plt.plot(price_pct, label='close')
        if plot_trades:
            if len(self.trades) > 1000:
                print('Warning: number of trades is greater than 1000, only plotting last 1000')
            for trade in self.trades[-1000:]:
                # print(trade)
                plt.scatter(trade['entry_time'], (trade['entry']/self.price_list[0])*100-100, marker='^', c=trade['side'].replace('long', '#00FF00').replace('short', '#FF0000'))
                plt.scatter(trade['exit_time'], (trade['exit']/self.price_list[0])*100-100, marker='v', c=trade['side'].replace('long', '#FF0000').replace('short', '#00FF00'))
        plt.legend()
        plt.show()

    def save_trades(self, filename='trades.csv'):
        df = pd.DataFrame(self.trades)
        df.to_csv(filename)

    def get_summary(self):
        print(f"""
        ################################################################################
        Total PnL: {round(self.pnl_list[-1], 3)}%       Total trades: {len(self.trades)}
        Positive trades: {len([i for i in self.trades if i['pnl'] > 0])} Negative trades: {len([i for i in self.trades if i['pnl'] < 0])}
        Average profit on trade: {round(self.pnl_list[-1]/len(self.trades), 3)}% 
        Most profitable trade: {round(max([i['pnl'] for i in self.trades]), 2)}% Least profitable trade: {round(min([i['pnl'] for i in self.trades]), 2)}%
        ################################################################################""")
