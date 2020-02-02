
import time
import datetime as dt
import pandas as pd
import shutil
import fxcmpy
from playsound import  playsound
from socketIO_client import SocketIO

def connect():

    token ='786733bea669469874c5b4f45be1e1766ac9066b' # 'b7ff7cbe3d6735a548ba8f33a37c78d465f847b2'  # demo
    con = fxcmpy.fxcmpy(access_token=token, log_level="error",server='real')
    print(con.get_accounts())
    return con,token


def Run(con,token):
    symbol = 'GBP/USD'
    do=True
    data_m1=None
    info = con.get_open_positions(kind=list)
    for x in range(0, len(info)):
        if info.iloc[x]['currency'] == symbol:
            do = False
            break
        else:
            do = True
    data = pd.DataFrame(columns = ['time','bid','tick'])
    N=0
    bid=0
    h=0
    candle_1_open=0
    candle_1_close=0
    candle_2_open=0
    candle_2_close=0
    candle_3_open=0
    candle_3_close=0

    while True:
        time1 = dt.datetime.now()
        if time1.second!=h:
            h = time1.second
            shutil.copy2('C:/Users\master\Desktop\\fix_example_x64 (1)\\fix_example\\fix_example\Logs\\' + 'FIX.4.4-MD_701299628_client1-FXCM.messages.current.log',\
                         'C:/Users\master\Desktop\\fix_example_x64 (1)\\fix_example\\fix_example\Logs\\' + 'new.log')
            f = open('C:/Users\master\Desktop\\fix_example_x64 (1)\\fix_example\\fix_example\Logs\\' + 'new.log','r')
            lines = f.readlines()
            f.close()

            num=len(lines)
            raw=lines[-1].split('270=')

            N1 = num - N
            N = num
            if N1!=0 and N1<150 and len(raw)>4:
                for x in range(N1):
                    timenow = dt.datetime.now()
                    raw = lines[-x]
                    bid_list=raw[1].split('')
                    bid=float(bid_list[0])
                    dic={'time':timenow,'bid':bid,'tick':1}
                    data=data.append(dic,ignore_index=True,sort=False)
                    print(data.tail(1))
            if N1==0 or len(raw)<=4:
                timenow = dt.datetime.now()
                dic = {'time': timenow, 'bid': bid, 'tick': 0}
                data = data.append(dic, ignore_index=True, sort=False)
                print(data.tail(1))


            if len(data)>185:
                two_minute = data.iloc[-120:-10]
                two_minute=two_minute.reset_index(drop=True)
                tick_sum = 0
                for x in range(len(two_minute)):
                    tick_sum += two_minute['tick'][x]
                maximum = two_minute['bid'].max()
                minimum = two_minute['bid'].min()
                average_tick_for_one_second = tick_sum / 120
                average_ticks_for_ten_seconds = average_tick_for_one_second * 10
                actual_ten_seconds_sum = 0
                for x in range((len(data)-10),len(data)):
                    actual_ten_seconds_sum += data['tick'][x]
                print('actual     '+str(actual_ten_seconds_sum))
                print('average    '+str(average_ticks_for_ten_seconds))
                print('--')
                print(((maximum-minimum)*10000)/2)
                print(((data['bid'][len(data)-1] - maximum)*10000)/2)
                print(((minimum - data['bid'][len(data)-1])*10000)/2)
                print('----------------------------')

                if (actual_ten_seconds_sum - average_ticks_for_ten_seconds) > average_ticks_for_ten_seconds*0.8 and do:
                    #print('downtrend    '+str(downtrend))
                    #print('uptrend    ' + str(uptrend))

                    if candle_1_open<candle_1_close and candle_2_open<candle_2_close and candle_3_open<candle_3_close :

                        if (data['bid'][len(data)-1] - maximum) >= (maximum - minimum)*0.8 :
                            print((maximum - minimum) * 10000)
                            opentrade = con.open_trade(symbol=symbol, is_buy=True, amount=1,
                                                       time_in_force='GTC',
                                                       order_type='AtMarket', is_in_pips=True, limit=5,
                                                       stop=-5)
                            do=False
                            playsound('warp.mp3')

                    if candle_1_open > candle_1_close and candle_2_open > candle_2_close and candle_3_open > candle_3_close:

                        if (minimum - data['bid'][len(data)-1]) >= (maximum - minimum)*0.8 :
                            print((maximum - minimum) * 10000)
                            opentrade = con.open_trade(symbol=symbol, is_buy=False, amount=1,
                                                       time_in_force='GTC',
                                                       order_type='AtMarket', is_in_pips=True, limit=5,
                                                       stop=-5)
                            do=False
                            playsound('warp.mp3')

            if time1.second==1 and len(data)>185:
                connected=con.is_connected()
                print(connected)
                candle_1_close = data['bid'][len(data)-2]
                candle_1_open = data['bid'][len(data)-62]
                candle_2_close = data['bid'][len(data)-62]
                candle_2_open = data['bid'][len(data)-122]
                candle_3_close = data['bid'][len(data)-122]
                candle_3_open = data['bid'][len(data)-182]
                print(data['time'][len(data)-2])
                print(data['time'][len(data)-62])
                print(data['time'][len(data)-62])
                print(data['time'][len(data)-122])
                print(data['time'][len(data)-122])
                print(data['time'][len(data)-182])

                if candle_1_open<candle_1_close:
                    print('candle 1   +')
                else:
                    print('candle 1   -')
                if candle_2_open<candle_2_close:
                    print('candle 2   +')
                else:
                    print('candle 2   -')
                if candle_3_open<candle_3_close:
                    print('candle 3   +')
                else:
                    print('candle 3   -')

                if connected==False:
                    con = fxcmpy.fxcmpy(access_token=token, log_level="error")
                print('DO :'+str(do))
                if do==False:
                    info = con.get_open_positions(kind=list)
                    if len(info)==0:
                        do=True
                    for x in range(0,len(info)):
                        if info.iloc[x]['currency']==symbol:
                            do=False
                            break
                        else:
                            do=True
            time2 = dt.datetime.now()
            print(((time2 - time1).microseconds)/1000000)

        time.sleep(0.1)

print(fxcmpy.__version__)
con,token=connect()
Run(con,token)
while True:
    try:
        con,token=connect()
        Run(con,token)
    except Exception as e:
        print(e)
        time.sleep(120)
