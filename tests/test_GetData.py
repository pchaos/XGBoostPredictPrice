# -*- coding: utf-8 -*-
'''test GetData
Created on Tue 31 May 2022 12:47:01 PM PST
Last Modified: Tue 31 May 2022 05:17:39 PM PST
'''
from unittest import TestCase

import pandas as pd

import GetData


class TryTesting(TestCase):

    def setUp(self) -> None:
        self.gd = GetData.GetData()

    def tearDown(self):
        self.gd = None

    def test_GetAllStock(self):
        allStocks = self.gd.GetAllStock()
        print(type(allStocks))
        self.assertTrue(type(allStocks), pd)
        counts=4000
        self.assertTrue(len(allStocks) > counts, "股票列表返回结果应该大于{counts}")
