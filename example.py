import pandas as pd
import pandas_ta as ta  # module for ta indicators
import backtester


pair = 'LINKUSDT'
df = pd.read_csv(f'data/{pair}.csv')

# add indicators / manipulate data here
# all indicators / documentation: https://github.com/twopirllc/pandas-ta#indicators-by-category
df['ma_1'] = df.ta.sma(1000)
df['ma_2'] = df.ta.sma(2000)
bot = backtester.Env(df)  # define the bot / enviroment with the data

while not bot.done:
    row = bot.step()  # step 1 candle forwads

    """
    values you can use:
    row # current row of the dataframe so you can acces row.close row.indicatorvalue row.low or whatever 
    bot.unrealised_pnl  # unrealised pnl of current posistions
    bot.pos  # posistion of the bot ex: {'size': 1, 'side': 'long', 'entries': [420.69], 'sl': 420, 'tp': 440}
    bot.fee  # 0.1 by deafault but you can set it to whatever you want

    functions:
    bot.buy(amount, sl, tp)  # buy/long an amount with optional sl and tp
    bot.sell(amount, sl, tp)  # sell/short an amount with optional sl and tp
    bot.exit(amount)  # exit current trade with x amount

    bot.plot(plot_pnl=True, plot_close=True, plot_trades=True)  # plot pnl, close and trades with optional parameters
    bot.save_trades(filename)  # save trades to csv file
    bot.get_summary()  # print summary info
    """
    
    # trade logic goes here
    
    if abs(bot.pos['size']) < 1:  # if not in posistions more than 1 size
        if row.ma_1 < row.ma_2:
            bot.sell(1, sl=row.close*1.05) # short with 1 amount, 5% sl 1
        if row.ma_1 > row.ma_2:
            bot.buy(1, sl=row.close*0.95) # long with 1 amount, 5% sl
    else:
        if bot.pos['side'] == 'short' and row.ma_1 > row.ma_2:
            bot.exit()
        if bot.pos['side'] == 'long' and row.ma_1 < row.ma_2:
            bot.exit()


bot.get_summary()
bot.save_trades('trades.csv')
bot.plot(plot_trades=True)
