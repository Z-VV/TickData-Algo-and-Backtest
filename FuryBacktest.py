import pandas as pd
import fxcmpy
import sys
from datetime import timedelta
import datetime as dt
from pandas.plotting import register_matplotlib_converters
import time
import warnings
warnings.filterwarnings('ignore')
register_matplotlib_converters()
pd.set_option('max_rows',None)


def data_down(symbol):
    
    #This function dowloads the tick data from fxcm.
    
    start = dt.datetime(2019, 8, 5)
    stop = dt.datetime(2019, 8, 9)
    td = fxcmpy.fxcmpy_tick_data_reader(symbol, start, stop)
    raw_data = td.get_raw_data()
    raw_data.info()
    td.get_data().info()
    frame = td.get_data()
    frame.to_pickle('GBPUSD.pkl')
    print(frame.tail(100))
    print('ok')

    return frame

def data_fill_sec(new):
    
    #Counting the number of ticks for one second and adding it to the 'tick' column. 
    
    new['tick']=0
    new['buy']=0
    new['sell']=0
    slice=new
    print(slice.head(3))
    tick = 1
    for x in range(len(slice)):
        timestamp=slice.index[x]
        timestamp1 = slice.index[x-1]
        sec=timestamp.second
        sec1 = timestamp1.second
        if sec==sec1:
            tick+=1
        else:
            a=slice.index[x-1]
            slice.at[a, 'tick'] = tick
            tick=1

    df = slice[(slice[['tick']] != 0).all(axis=1)]
    df=df.reset_index(drop=False)
    print('into')
    total=len(df)
    
    #Inserting rows for each second missing in the data,because of no  changes in the price.
    
    x=0
    while x<=total-1:
        diff=df.iloc[x, 0].second - df.iloc[x - 1, 0].second
        if diff>1:
            bid=df.iloc[x-1,1]
            ask=df.iloc[x-1,2]
            df1 = df[0:x]
            df2 = df[x::]
            for z in range(diff-1):
                new = df.iloc[x-1, 0] + timedelta(seconds=z+1)
                new_row = [new, bid, ask, 0, 0, 0]
                df1.loc[x+z] = new_row
            total+=(diff-1)
            df= pd.concat([df1, df2])
        x+=1

    df=df.reset_index(drop=True)
    print(df.head(10))
    df.set_index("index", inplace=True)
    print(df.head(10))
    #df.to_pickle('gbp01.pkl')
    return df

def algo(df):
    
    #Checking the clean and ready data  for BUY and SELL signals via trading algorithm.
    #Marks the point of entry at the BUY and SELL columns with 1.
    
    print('checking....')
    for x in range(60,len(df)):
        two_minute=df.iloc[x-120:x-10]
        tick_sum=0
        for tick in range(len(two_minute)):
            tick_sum+=two_minute['tick'][tick]
        maximum=two_minute['Bid'].max()
        minimum=two_minute['Bid'].min()
        average_tick_for_one_second=tick_sum/120
        average_ticks_for_ten_seconds=average_tick_for_one_second*10
        actual_ten_seconds_sum=0
        for next in range(10):
            actual_ten_seconds_sum+=df['tick'][x-next]
        if (actual_ten_seconds_sum - average_ticks_for_ten_seconds)>average_ticks_for_ten_seconds*2.5:
            if  (df['Bid'][x]-maximum)>=(maximum-minimum)*0.75:
                print((maximum - minimum) * 10000)
                a=df.index[x]
                df.at[a,'buy']=1
                print('{}   --BUY--'.format(str(df.index[x])))
                print('------')
            if (minimum-df['Bid'][x])>=(maximum-minimum)*0.75:
                print((maximum - minimum) * 10000)
                a=df.index[x]
                df.at[a,'sell']=1
                print(str(df.index[x])+'   --SELL--')
                print('------')

    return df

def clean_signal(data):
    
    #Going throw the data again,taking the first signal only and deleting the next 100 second if the sagnal appears again.
    
    x = 1
    while x <= len(data) - 1:
        if data['buy'][x] == 1:
            try:
                for z in range(x + 1, x + 100):
                    if data['buy'][z] == 1:
                        data.at[data.index[z], 'buy'] = 0
            except Exception as e:
                print(e)
                break
            x = z
        x += 1

    x = 1
    while x <= len(data) - 1:
        if data['sell'][x] == 1:
            try:
                for z in range(x + 1, x + 100):
                    if data['sell'][z] == 1:
                        data.at[data.index[z], 'sell'] = 0
            except Exception as e:
                print(e)
                break
            x = z
        x += 1

    return data

def backtest(data):
    
    #Counting the number of wins and loses and cheking if the algorithm is profitable.
    
    print(data.tail(20))
    print('ok')
    dictionary = {}
    tp_list = [5,6,7]
    sl_list = [-3,-4]

    for take in tp_list:
        for stop in sl_list:
            tp = take
            sl = stop
            x = 1
            wins_buy = []
            loses_buy = []
            wins_sell = []
            loses_sell = []
            while x < len(data):
                if data['buy'][x] == 1:
                    #print('NEW BUY SIGNAL    '+str(data.index[x]))
                    pips = 0
                    for z in range(x, len(data)):
                        pips += (data['Bid'][z] - data['Bid'][z - 1]) * 10000
                        #print(str("%.1f" % pips)+'    '+str(data.index[z]))
                        #time.sleep(0.1)
                        if pips >= tp:
                            print('                                                                      win')
                            wins_buy.append(1)
                            x = z
                            break
                        if pips <= sl:
                            print('                                                                      lost')
                            loses_buy.append(1)
                            x = z
                            break
                if data['sell'][x] == 1:
                    #print('NEW SELL SIGNAL    '+str(data.index[x]))
                    pips = 0
                    for z in range(x, len(data)):
                        pips += (data['Bid'][z - 1] - data['Bid'][z]) * 10000
                        #print(str("%.1f" % pips)+'    '+str(data.index[z]))
                        #time.sleep(0.1)
                        if pips >= tp:
                            print('                                                                      win')
                            wins_sell.append(1)
                            x = z
                            break
                        if pips <= sl:
                            print('                                                                      lost')
                            loses_sell.append(1)
                            x = z
                            break
                x += 1
            dictionary[(tp * (len(wins_buy)+len(wins_sell)) - ((-sl) * (len(loses_buy)+len(loses_sell))))] = [tp, sl]
            print('wins buy   ' + str(len(wins_buy)))
            print('loses buy  ' + str(len(loses_buy)))
            print('wins sell   ' + str(len(wins_sell)))
            print('loses sell  ' + str(len(loses_sell)))
            print('result  :  ' + str(tp * (len(wins_buy)+len(wins_sell)) - (-sl) * (len(loses_buy)+len(loses_sell))))
            print(sl, tp)
            print('---------------------------------------------')

    print(dictionary)
    best = max(dictionary, key=int)
    print(best, dictionary[best])

def full_test():
    time1=dt.datetime.now()
    data=data_down('GBPUSD')
    print('step 1')
    data1=data_fill_sec(data)
    print('step 2')
    data2=algo(data1)
    print('step 3')
    data3=clean_signal(data2)
    print('step 4')
    backtest(data=data3)
    time2=dt.datetime.now()
    print(time2-time1)
    time.sleep(5)


full_test()

