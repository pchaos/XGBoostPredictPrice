# -*- coding: utf-8 -*-
'''test sometools
Created on Mon 07 Jun 2022 05:56:35 PM PST
Last Modified: Thu 16 Jun 2022 01:19:21 AM PST
'''
import datetime
import logging
import os
import unittest
from unittest import TestCase

import pandas as pd
import xgboost as xgb

import GetData
from xgboostmodel import BuildFeature

LOGGER = logging.getLogger(__name__)


def get_class_name(aclass):
    return str(type(aclass)).split("'")[1]


class BuildFeature_old(BuildFeature):

    def run(self, days=[3, 5]) -> list:  #注意：days列表里必须至少有一项，且不为0
        gd = GetData.GetData()
        feature0 = pd.DataFrame()
        allstock = gd.GetAllStock()
        for k in days:  #定义几个空的dataframe
            exec("feature%s=pd.DataFrame()" % k)

        j = 0
        for i in allstock.ts_code:
            try:
                # time.sleep(0.15)
                bars = gd.GetAStockData(i)  # 得到K线
                if len(bars) > 100:
                    featureret = self.getfeatures(bars,
                                                  y=0)  #get today's feature
                    feature0 = feature0.append(featureret, ignore_index=True)
                    print(i, end=", ")
                    for k in days:
                        df, y = self.splitbars(bars, y_days=k)
                        featureret = self.getfeatures(
                            df,
                            y)  #get learning feature,which includes rewards
                        exec(
                            "feature%s=feature%s.append(featureret,ignore_index=True)"
                            % (k, k))
                    j = j + 1
                    if j > 100:
                        break  #这两行代码测试时使用
            except OSError:
                pass
            continue
        result = []
        result.append(feature0)
        for k in days:  #定义几个空的dataframe
            exec("result.append(feature%s)" % k)
        return result


class XGboostTesting(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.bf = None
        cls.bf_old = None

    def setUp(self) -> None:
        self.bf = BuildFeature()
        self.bf_old = BuildFeature_old()

    def tearDown(self):
        self.bf = None
        self.bf_old = None

    def test_BuildFeature_old_run(self):
        bf = self.bf_old
        LOGGER.info(f"self BuildFeature:{bf}")
        self.BuildFeature_run(bf)

    def test_BuildFeature_run(self):
        bf = self.bf
        LOGGER.info(f"self BuildFeature:{bf}")
        self.BuildFeature_run(bf)

    def BuildFeature_run(self, bf):
        ret, days = self.bf_run(bf)
        predict_data = ret[0]
        today = datetime.date.today()
        today = today.strftime('%Y%m%d')
        class_name = str(type(bf)).split("'")[1]
        writer = pd.ExcelWriter(
            os.path.join("/tmp", f'{(class_name)}{today}result.xlsx'))
        try:
            for i in range(len(days)):
                data = ret[i + 1]

                y = data['股票收益']
                # x=data.iloc[:,3:]
                x = data.drop(['股票收益', '股票名称'], axis=1)
                print(f"{x=}\n{y=}")

                #  Xtrain,Xtest,Ytrain,Ytest = TTS(x,y,test_size=0.3,random_state=420)
                dfull = xgb.DMatrix(x, y)
                param1 = {
                    'silent': True,
                    'obj': 'reg:linear',
                    "subsample": 1,
                    "max_depth": 5,
                    "eta": 0.1,
                    "gamma": 2,
                    "lambda": 0.2,
                    "alpha": 0,
                    "colsample_bytree": 1,
                    "colsample_bylevel": 1,
                    "colsample_bynode": 1,
                    "nfold": 5
                }
                num_round = 200
                print("正在学习模型......")
                bst = xgb.train(param1, dfull, num_round)
                print("正在预测......")

                xtest = predict_data.drop(['股票收益', '股票名称'], axis=1)
                feature = xgb.DMatrix(xtest)
                pred = bst.predict(feature)
                predict_data['股票收益'] = pred
                today = datetime.date.today()
                today = today.strftime('%Y%m%d')
                print("预测完成！")
                columns = ['股票名称', '股票收益']
                sorted = predict_data.sort_values(by="股票收益",
                                                  ascending=False)[columns]
                print("%s日涨幅最大股票预测结果：" % (days[i]))
                print(sorted.head(20))
                top20 = sorted.head(20)
                top20.to_excel(writer, sheet_name="%s日涨幅" % (days[i]))
        except Exception as e:
            print(e.args)
        finally:
            writer.save()
            writer.close()

    def bf_run(self, bf):
        days = [1, 3, 5, 10, 20]
        ret = bf.run(days=days)  #得到特征矩阵，ret是一个list，每个元素是一个dataframe
        #  LOGGER.info(f"{get_class_name(bf)}\n{ret}")
        return ret, days

    def test_bf_run(self):
        """BuildFeature run test
        """
        bf_old = self.bf_old
        ret, days = self.bf_run(bf_old)

        bf = self.bf
        ret2, days2 = self.bf_run(bf)
        self.assertEqual(days, days2, f"days not match:{days},{days2}")
        self.assertTrue(
            len(ret) == len(ret2),
            f"return value length not equals:\n{ret}\n{ret2}")
        self.assertTrue((ret[0].columns == ret2[0].columns).any(),
                        f"{ret[0].columns}, {ret2[0].columns}")
        #  LOGGER.info(f"return value equals:{ret[0].equals(ret2[0])}")
        #  LOGGER.info(f"{type(ret[0])}=")
        #  LOGGER.info(f"{ret[0].astype=}")
        #  LOGGER.info(f"{ret[0].columns=}")
        LOGGER.info(f"before:{ret[0].columns=}")
        LOGGER.info(f"before:{ret2[0].columns=}")
        LOGGER.info(f"{ret[0].describe().loc[['min','max','mean'],:]=}")
        LOGGER.info(f"{ret2[0].describe()=}")
        #  ret[1].to_csv("/tmp/ret.csv")
        #  ret2[1].to_csv("/tmp/ret2.csv")
        for i in range(len(ret)):
            #  self.assertEqual(ret[i], ret2[i], f"result not equals:\n{ret[i]=}, {ret2[i]=}")
            df_ret = ret[i].drop(columns='股票名称')
            df_ret2 = ret2[i].drop(columns='股票名称')
            # 5日20日均线        int64   why???
            LOGGER.info(f"{df_ret.dtypes=}")
            LOGGER.info(f"{df_ret2.dtypes=}")
            for j in df_ret.columns:
                # 转换成相同数据类型，否则会测试不通过
                df_ret[j] = df_ret[j].astype(float)
                #  df_ret2[j] = df_ret2[j].astype(float)
            LOGGER.info(f"after modified type:{df_ret.dtypes=}")
            LOGGER.info(f"after modified type: {df_ret2.dtypes=}")
            self.assertTrue(df_ret.equals(df_ret2),
                            f"{i=} not equals:\n{df_ret=},\n{df_ret2=}")
        LOGGER.info(f"{df_ret2.describe().loc[['min','max','mean'],:]=}")
        LOGGER.info(f"after modified type: {ret2[0].convert_dtypes().dtypes=}")
        LOGGER.info(f"after modified type: {ret2[0].dtypes=}")


if __name__ == "__main__":
    #  XGboostTesting().test_bf_run()
    unittest.main()
