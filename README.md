# 使用XGBoost预测n日后的股价

#### 介绍
使用XGBoost预测n日后的股价（使用tushare数据源）

#### 软件架构
软件架构说明


#### 安装教程

1.  此代码在linux下无法运行，因为linux下dataframe返回的数据被自动按title排序了
2.  由于要计算全部股票，tushare读取全部股票数据需要近1小时
3.  计算结束后，在代码目录下生成XXXXXXresult.xls的文件
4.  tushare目前开始提供因子数据，等tushare因子数据提供的足够多后可以，可以直接使用tushare的因子数据做特征工程
5.  tushare的免费token可以使用。
6.  注册免费tushare token https://tushare.pro/register?reg=286095
7.  运行前将你的token更新到 GetData.py中ts.set_token('your token here')
8.  XGBoost的调参一直做的不好，目前参数有些过拟合。后来明白了，是数据本身的问题。


#### 使用说明

1.  python xgboostmodel.py
