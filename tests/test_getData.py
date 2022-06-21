# -*- coding: utf-8 -*-
'''test getData
Created on Tue 31 May 2022 12:47:01 PM PST
Last Modified: Tue 21 Jun 2022 12:27:47 AM PST
'''
from unittest import TestCase

import pandas as pd
import logging
import getData

LOGGER = logging.getLogger(__name__)

class GetDataTesting(TestCase):

    def setUp(self) -> None:
        self.gd = getData.GetData()

    def tearDown(self):
        self.gd = None

    def test_GetAllStock(self):
        allStocks = self.gd.GetAllStock()
        print(type(allStocks))
        self.assertTrue(type(allStocks), pd)
        counts = 4000
        self.assertTrue(len(allStocks) > counts, "股票列表返回结果应该大于{counts}")

    def test_GetAllStock_fields(self):
        allStocks = self.gd.GetAllStock()
        stockClumns = 'ts_code,symbol,name,area,industry,list_date'
        for item in stockClumns.split(","):
            # 校验返回股票列表标题
            self.assertTrue(item in allStocks.columns,
                            f"{item} not in {allStocks.columns}")

        # 改变股票列表标题
        newStockClumns = stockClumns.replace("ts_code", "code").split(",")
        allStocks.columns = newStockClumns
        self.assertTrue(allStocks.columns[0] == "code", f"{allStocks.columns[0]} != \"code\"")

    def test_GetAStockData(self):
        # 测试获取股票数据
        allStocks = self.gd.GetAllStock()
        LOGGER.info(allStocks.columns[0])
        i=1
        for code in allStocks[allStocks.columns[0]]:
            LOGGER.info(f"{i}, {code}")
            i+=1
        counts = 4000
        self.assertTrue(len(allStocks[allStocks.columns[0]]) > 4000, f"codes counts < {counts}" )
        LOGGER.info(f"{type(allStocks)=}")

