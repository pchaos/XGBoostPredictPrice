# -*- coding: utf-8 -*-
"""
Created on Fri Apr 2 10:01:10 2022
Last Modified: Tue 21 Jun 2022 12:50:36 AM PST
@author: chenxiong888
"""

import pandas as pd
import numpy as np
import tushare as ts
import datetime
import talib
import matplotlib.pyplot as plt
from functools import lru_cache
from sometools import tools, getTushareToken


class GetData(object):

    def __init__(self):
        token = getTushareToken()
        ts.set_token(token)
        #  print(f"token:{token}")
        self.pro = ts.pro_api()

    def GetAllStock(self) -> pd.DataFrame:

        allstock = self.pro.query(
            'stock_basic',
            exchange='',
            list_status='L',
            fields='ts_code,symbol,name,area,industry,list_date')
        allstock = allstock[~allstock.name.str.contains('ST')]
        #重新索引
        allstock = allstock.reset_index(drop=True)
        return allstock

    @lru_cache(maxsize=8192)
    def GetAStockData(self, tscode='000001.SZ', period=250):
        """获取股票数据
tushare返回pd.DataFrame, 字段类型：
ts_code trade_date close open high low pre_close change pct_chg vol amount

        """
        today = datetime.date.today()
        today = today.strftime('%Y%m%d')
        startday = datetime.date.today() - datetime.timedelta(days=period)
        startday = startday.strftime('%Y%m%d')
        #daily返回的是未复权数据
        #data= self.pro.daily(ts_code=tscode, start_date=startday, end_date=today)
        #probar返回的是复权数据
        #print(tscode)
        data = ts.pro_bar(ts_code=tscode,
                          adj='qfq',
                          start_date=startday,
                          end_date=today)
        if data is None:
            data = pd.DataFrame(columns=['trade_date', 'B', 'C', 'D'])
        if not data.empty:
            data = data.sort_index(ascending=False)
        sorteddata = data.sort_values(by="trade_date", ascending=True)
        sorteddata = sorteddata.reset_index(drop=True)
        return sorteddata

    def GetAStockDataByDate(self,
                            tscode='000001.SZ',
                            startday='20220101',
                            today='20220331'):

        data = ts.pro_bar(ts_code=tscode,
                          adj='qfq',
                          start_date=startday,
                          end_date=today)
        if data is None:
            data = pd.DataFrame(columns=['trade_date', 'B', 'C', 'D'])
        if not data.empty:
            data = data.sort_index(ascending=False)
        sorteddata = data.sort_values(by="trade_date", ascending=True)
        sorteddata = sorteddata.reset_index(drop=True)
        return sorteddata

    def GetIndex(self, mkt="SSE", period=365):
        today = datetime.date.today()
        today = today.strftime('%Y%m%d')
        startday = datetime.date.today() - datetime.timedelta(days=period)
        startday = startday.strftime('%Y%m%d')
        #df = self.pro.index_basic(market=mkt)
        df = self.pro.index_daily(ts_code='000001.SH ',
                                  start_date=startday,
                                  end_date=today)
        df1 = df.sort_values(by="trade_date", ascending=True)
        df1 = df1.reset_index(drop=True)

        return df1

    def GetHourBar(self, tscode='000001.SZ', day='20200610'):
        today = datetime.date.today()
        today = today.strftime('%Y%m%d')

        #data=ts.pro_bar(ts_code=tscode, adj='qfq', freq='60min',start_date=day, end_date=day)
        data = ts.get_hist_data('600848',
                                start='2020-06-10',
                                end='2020-06-10',
                                ktype='5')
        if data is None:
            data = pd.DataFrame(columns=['A', 'B', 'C', 'D'])
        if not data.empty:
            data = data.sort_index(ascending=False)
        #print (data)
        return data

    def GetAllFuturesName(self):
        #交易所代码 CFFEX-中金所 DCE-大商所 CZCE-郑商所 SHFE-上期所 INE-上海国际能源交易中心
        df = self.pro.fut_daily(ts_code='CU指数.SHF',
                                start_date='20210301',
                                end_date='20210315')
        #df=self.pro.trade_cal(exchange='SHFE', start_date='20210315', end_date='20210315')
        # df = self.pro.fut_basic(exchange='DCE', fut_type='1', fields='ts_code,symbol,name,list_date,delist_date')
        # df = self.pro.fut_basic(exchange='SHFE',fut_type='1', fields='ts_code,symbol,name,list_date,delist_date')
        return df

    #同花顺板块指数相关函数===============================================================================================
    def GetIndustryList(self):
        #得到同花顺板块的名称列表
        df = self.pro.ths_index()
        return df

    def GetAIndustryData(self, tscode='865001.TI', period=250):
        #得到一个同花顺板块的k线数据
        today = datetime.date.today()
        today = today.strftime('%Y%m%d')
        startday = datetime.date.today() - datetime.timedelta(days=period)
        startday = startday.strftime('%Y%m%d')
        df = self.pro.ths_daily(
            ts_code=tscode,
            start_date=startday,
            end_date=today,
            fields='ts_code,trade_date,open,close,high,low,vol,pct_change')
        if not df.empty:
            df = df.sort_index(ascending=False)
        return df

    def GetAIndustryMember(self, tscode='865001.TI'):
        df = self.pro.ths_member(ts_code=tscode)
        return df

    def GetIndicator(self, tscode='600000.SH'):
        df = self.pro.query('fina_indicator',
                            ts_code=tscode,
                            start_date='20200101',
                            end_date='20210701')
        return df

    # ===============================================================================================


if __name__ == "__main__":
    gd = GetData()
    df = pd.DataFrame()
    # df=gd.GetAllFuturesName()

    # df.drop_duplicates(subset=None, keep='first', inplace=False)
    print()
