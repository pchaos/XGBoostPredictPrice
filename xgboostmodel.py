# -*- coding: utf-8 -*-
"""
Created on Fri Apr 22 10:01:10 2022
Last Modified: Sat 18 Jun 2022 12:40:15 AM PST
@author: chenxiong888
"""

import xgboost as xgb

# from sklearn.model_selection import KFold, cross_val_score as CVS, train_test_split as TTS
# from sklearn.metrics import mean_squared_error as MSE
import pandas as pd
import datetime
import time
import re
#  import tushare as ts
import talib
import logging
from sometools import tools
import GetData

LOGGER = logging.getLogger(__name__)

class BuildFeature(object):
    def __init__(self, ):
        self.tool=tools()

    def splitbars(self,bars, y_days=5):
        ###
        # para1: stock code
        # para2: accumulate reward in days,which means feature y
        # return k_lines of before y_days and y for y_days's reward
        ###

        df1 = bars[1:-y_days-1]
        df2 = bars['close'][-y_days-2:-1].tolist()

        #  y = round(((df2[-1] - df2[-y_days-1]) / df2[-1]) * 100, 2)
        y = round(((df2[-1] - df2[-y_days-1]) / df2[-1]) * 100, 3)

        return df1,y

    def getfeatures(self,df,y):
        open_values=df['open'].values
        close_values=df['close'].values
        low_values=df['low'].values
        high_values=df['high'].values
        pct_chg=df['pct_chg'].values

        feature={}

        feature.update({"股票收益":y})
        feature.update({"股票名称":df.iloc[1]['ts_code']})

        #==============================================
        ma5=talib.SMA(close_values,timeperiod=5)
        deg=self.tool.data_to_deg(ma5[-11:-1])
        feature.update({"5日角度":deg})
        ma20=talib.SMA(close_values,timeperiod=20)
        deg=self.tool.data_to_deg(ma20[-11:-1])
        feature.update({"20日角度":deg})
        ma60=talib.SMA(close_values,timeperiod=60)
        deg=self.tool.data_to_deg(ma60[-11:-1])
        feature.update({"60日角度":deg})
        if ma5[-2]<ma20[-2] and ma5[-1]>=ma20[-1]:
            corss5x20=1
        elif ma5[-2]>ma20[-2] and ma5[-1]<=ma20[-1]:
            corss5x20=-1
        else :
            corss5x20=0
        feature.update({"5日20日均线":corss5x20})
        if ma20[-2]<ma60[-2] and ma20[-1]>=ma60[-1]:
            corss20x60=1
        elif ma20[-2]>ma60[-2] and ma20[-1]<=ma60[-1]:
            corss20x60=-1
        else :
            corss20x60=0
        feature.update({"20日60日均线":corss20x60})
        pos=round((close_values[-1]-min(close_values))/(max(close_values)-min(close_values))*100,2)
        feature.update({"价格分位数":pos})
        #==============================================
        feature.update({'两只乌鸦': talib.CDL2CROWS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({'三只乌鸦': talib.CDL3BLACKCROWS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '三内部上涨和下跌': talib.CDL3INSIDE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '三线打击': talib.CDL3LINESTRIKE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '三外部上涨和下跌': talib.CDL3OUTSIDE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '南方三星': talib.CDL3STARSINSOUTH(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '三个白兵': talib.CDL3WHITESOLDIERS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '弃婴': talib.CDLABANDONEDBABY(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '大敌当前': talib.CDLADVANCEBLOCK(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '捉腰带线': talib.CDLBELTHOLD(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '脱离': talib.CDLBREAKAWAY(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '收盘缺影线': talib.CDLCLOSINGMARUBOZU(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '藏婴吞没': talib.CDLCONCEALBABYSWALL(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '反击线': talib.CDLCOUNTERATTACK(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '乌云压顶': talib.CDLDARKCLOUDCOVER(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '十字': talib.CDLDOJI(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '十字星': talib.CDLDOJISTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '蜻蜓十字/T形十字': talib.CDLDRAGONFLYDOJI(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '吞噬模式': talib.CDLENGULFING(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '十字暮星': talib.CDLEVENINGDOJISTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '暮星': talib.CDLEVENINGSTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '向上/下跳空并列阳线': talib.CDLGAPSIDESIDEWHITE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '墓碑十字/倒T十字': talib.CDLGRAVESTONEDOJI(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '锤头': talib.CDLHAMMER(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '上吊线': talib.CDLHANGINGMAN(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '母子线': talib.CDLHARAMI(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '十字孕线': talib.CDLHARAMICROSS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '风高浪大线': talib.CDLHIGHWAVE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '陷阱': talib.CDLHIKKAKE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '修正陷阱': talib.CDLHIKKAKEMOD(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '家鸽': talib.CDLHOMINGPIGEON(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '三胞胎乌鸦': talib.CDLIDENTICAL3CROWS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '颈内线': talib.CDLINNECK(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '倒锤头': talib.CDLINVERTEDHAMMER(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '反冲形态': talib.CDLKICKING(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '由较长缺影线决定的反冲形态': talib.CDLKICKINGBYLENGTH(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '梯底': talib.CDLLADDERBOTTOM(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '长脚十字': talib.CDLLONGLEGGEDDOJI(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '长蜡烛': talib.CDLLONGLINE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '光头光脚/缺影线': talib.CDLMARUBOZU(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '相同低价': talib.CDLMATCHINGLOW(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '铺垫': talib.CDLMATHOLD(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '十字晨星': talib.CDLMORNINGDOJISTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '晨星': talib.CDLMORNINGSTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '颈上线': talib.CDLONNECK(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '刺透形态': talib.CDLPIERCING(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '黄包车夫': talib.CDLRICKSHAWMAN(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '上升/下降三法': talib.CDLRISEFALL3METHODS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '分离线': talib.CDLSEPARATINGLINES(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '射击之星': talib.CDLSHOOTINGSTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '短蜡烛': talib.CDLSHORTLINE(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '纺锤': talib.CDLSPINNINGTOP(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '停顿形态': talib.CDLSTALLEDPATTERN(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '条形三明治': talib.CDLSTICKSANDWICH(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '探水竿': talib.CDLTAKURI(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '跳空并列阴阳线': talib.CDLTASUKIGAP(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '插入': talib.CDLTHRUSTING(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '三星': talib.CDLTRISTAR(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '奇特三河床': talib.CDLUNIQUE3RIVER(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '向上跳空的两只乌鸦': talib.CDLUPSIDEGAP2CROWS(open_values, high_values, low_values, close_values)[-1]/100})
        feature.update({ '上升/下降跳空三法': talib.CDLXSIDEGAP3METHODS(open_values, high_values, low_values, close_values)[-1]/100})
        # if realtime==False:
        #     self.features=self.features.append(feature,ignore_index=True)
        # else:
        #     self.realtimefeatures=self.realtimefeatures.append(feature,ignore_index=True)
        # print(self.features)

        return feature

    def run(self,days=[3,5], testing=False) -> list:#注意：days列表里必须至少有一项，且不为0
        gd=GetData.GetData()
        feature0=pd.DataFrame()
        allstock=gd.GetAllStock()
        for k in days:#定义几个空的dataframe
            exec(f"feature{k}=pd.DataFrame()")
            #  print("feature%s=pd.DataFrame()"%k)

        j=0
        for code in allstock.ts_code:
            try:
                # time.sleep(0.15)
                bars=gd.GetAStockData(code)# 得到K线

                if len(bars)>100:
                    featureret=self.getfeatures(bars,y=0) #get today's feature
                    #  feature0=feature0.append(featureret,ignore_index=True)
                    #  feature0.append(featureret,ignore_index=True)
                    #  print(f"{type(featureret)=}")
                    #  print(f"{featureret=}")
                    #  print(f"{pd.DataFrame.from_dict(featureret, orient='index').T}")
                    #  feature0=pd.concat(feature0, pd.DataFrame(featureret), ignore_index=True)
                    #  feature01=pd.concat(feature01, pd.DataFrame(featureret), ignore_index=True)
                    feature0=pd.concat([feature0, pd.DataFrame.from_dict(featureret, orient='index').T])
                    feature0.reset_index(drop=True, inplace=True)
                    #  feature0=feature0.convert_dtypes()
                    self._adjust_columns_type(feature0)
                    if (j % 5 == 0):
                        print(f"|{j} {code}", end=" ", flush=True)
                    else:
                        print(f"|{j} {code}", end=" ")
                    for k in days:
                        df,y=self.splitbars(bars,y_days=k)
 
                        featureret=self.getfeatures(df,y) #get learning feature,which includes rewards
                        exec(f"feature{k}=pd.concat([feature{k}, pd.DataFrame.from_dict(featureret, orient='index').T]);feature{k}.reset_index(drop=True, inplace=True)")
                        exec(f"self._adjust_columns_type(feature{k})")
                        #  exec("feature%s=feature%s.append(featureret,ignore_index=True)"%(k,k))
                    j+=1
                    if testing and j>100 : 
                        # 当testing为真时，测试数据为100
                       break;   #这两行代码测试时使用
                else:
                    print(f"{code}", end=" - ")
            except OSError:
                pass
        result=[]
        result.append(feature0)
        for k in days:#定义几个空的dataframe
            exec ("result.append(feature%s)"%k)
        return result

    @classmethod
    def _adjust_columns_type(cls, a_df:pd.DataFrame) -> None:
        """调整pandas.DataFrame columns 数据类型
        """
        #不需要改变类型的列名
        exclude_columns=["股票名称"]
        for col in a_df.columns:
            if col in exclude_columns:
                continue
            a_df[col] = a_df[col].astype(float)

    @classmethod
    def check_stock_code(cls, code:str=""):
        """设定代码规则
        指定某些股票代码是否剔除
        return: 
        """
        # 返回股票代码以 0 3 6起始
        res = re.search("^[0,3,6]", code)
        if res is None:
            LOGGER.info(f"{code} not match")
        return res

if __name__ == "__main__":
    bf=BuildFeature()
    days=[1,3,5,10,20]
    ret=bf.run(days=days)  #得到特征矩阵，ret是一个list，每个元素是一个dataframe
    predict_data=ret[0]
    today = datetime.date.today()
    today = today.strftime('%Y%m%d')
    try:
        writer = pd.ExcelWriter(today+'result.xlsx')
        for i in range(len(days)):
            data=ret[i+1]

            y=data['股票收益']
            # x=data.iloc[:,3:]
            x=data.drop(['股票收益','股票名称'],axis=1)
            print(f"{x=}\n{y=}")

            #  Xtrain,Xtest,Ytrain,Ytest = TTS(x,y,test_size=0.3,random_state=420)
            dfull = xgb.DMatrix(x,y)
            param1 = {'silent':True
                      ,'obj':'reg:linear'
                      ,"subsample":1
                      ,"max_depth":5
                      ,"eta":0.1
                      ,"gamma":2
                      ,"lambda":0.2
                      ,"alpha":0
                      ,"colsample_bytree":1
                      ,"colsample_bylevel":1
                      ,"colsample_bynode":1
                      ,"nfold":5}
            num_round = 200
            print("......正在学习模型......")
            bst=xgb.train(param1,dfull,num_round)
            print("......正在预测......")

            xtest=predict_data.drop(['股票收益','股票名称'],axis=1)
            feature=xgb.DMatrix(xtest)
            pred=bst.predict(feature)
            predict_data['股票收益']=pred
            today = datetime.date.today()
            today = today.strftime('%Y%m%d')
            print("预测完成！")
            columns=['股票名称','股票收益']
            sorted=predict_data.sort_values(by="股票收益",ascending=False)[columns]
            sorted['股票收益']=sorted['股票收益'].round(2)
            print(f"{days[i]}日涨幅最大股票预测结果：")
            print(sorted.head(20) )
            top20=sorted.head(20)
            top20.to_excel(writer,sheet_name="%s日涨幅"%(days[i]))
    except Exception as e:
        print(e.args)
    finally:
        writer.save()
        writer.close()
