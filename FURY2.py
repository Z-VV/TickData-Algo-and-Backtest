import time
import datetime as dt
import pandas as pd
import shutil
import fxcmpy
from playsound import  playsound
from talib import EMA

def connect():
    #Connects
    
    token = 'insert token here'  
    con = fxcmpy.fxcmpy(access_token=token, log_level="error")
    print(con.get_accounts())
    return con,token

# Originaly  FIX (Financial Information Exchange) API is designed to work with C++ mostly,beacause of the speed of data streaming
# and orders(see high frequency trading).
# C++ code is working simultaneously with this code.To take up yo 200 price changes a second,our code must first copy the C log.file 
# in order to not interrupt the writing and then read the new file.

def Run(con,token):
    symbol = 'GBP/USD'
    do=True
    info = con.get_open_positions(kind=list)
    for x in range(0, len(info)):
        if info.iloc[x]['currency'] == symbol:
            do = False
            break
        else:
            do = True
    data = pd.DataFrame(columns = ['time','bid','tick'])
    N=0

    while True:
            time1 = dt.datetime.now()
            shutil.copy2('C:/Users\master\Desktop\\fix_example_x64 (1)\\fix_example\\fix_example\Logs\\' + 'FIX.4.4-MD_701299628_client1-FXCM.messages.current.log',\
                         'C:/Users\master\Desktop\\fix_example_x64 (1)\\fix_example\\fix_example\Logs\\' + 'new.log')
            f = open('C:/Users\master\Desktop\\fix_example_x64 (1)\\fix_example\\fix_example\Logs\\' + 'new.log','r')
            lines = f.readlines()
            f.close()

            num=len(lines)
            raw=lines[-1].split('270=')
            
            # Creating dataframe from the tick data avaliable from the log.file 
            if len(raw)>4:
                N1 = num - N
                N = num
                if N1!=0 and N1<150:
                    timenow = dt.datetime.now()
                    bid_list=raw[1].split('')
                    bid=float(bid_list[0])
                    dic={'time':timenow,'bid':bid,'tick':N1}
                    data=data.append(dic,ignore_index=True,sort=False)
                    print(data.tail(1))
                    
            # Going throw the dataframe every second and checking for signals as at FuryBacktest.py . 
            if len(data)>121:
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
                    if (data['bid'][len(data)-1] - maximum) >= (maximum - minimum)*0.8 :
                        print((maximum - minimum) * 10000)
                        opentrade = con.open_trade(symbol=symbol, is_buy=True, amount=5,
                                                   time_in_force='GTC',
                                                   order_type='AtMarket', is_in_pips=True, limit=3,
                                                   stop=-2)
                        do=False
                        playsound('warp.mp3')

                    if (minimum - data['bid'][len(data)-1]) >= (maximum - minimum)*0.8 :
                        print((maximum - minimum) * 10000)
                        opentrade = con.open_trade(symbol=symbol, is_buy=False, amount=5,
                                                   time_in_force='GTC',
                                                   order_type='AtMarket', is_in_pips=True, limit=3,
                                                   stop=-2)
                        do=False
                        playsound('warp.mp3')

            if time1.second==10:
                connected=con.is_connected()
                print(connected)

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
            print(time2 - time1)
            time.sleep(1)


con,token=connect()
Run(con,token)
