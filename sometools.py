import numpy as np
import pandas
import statsmodels.api as sm
import matplotlib.pyplot as plt
import talib
import datetime

def getTushareToken():
    """从文件".env"获取tushare token
    """
    import os
    from dotenv import load_dotenv
    if os.path.exists(".env"):
        # 存在文件".env"
        config = load_dotenv()

    else:
        print("You must set tushare token  in file:'.env' first!!!\n see example.env ")
        exit(1)


class tools(object):
    """一些用于分析的tool函数"""

    def __init__(self):
        # pro=ts.pro_api(token='d37e1279d92ac6d0470c5a14eb4dd227e4dfbaa8261e66ce2af19684')
        pass
    # ===================================================================================================================

    def GetHoldRatio(self, df):  # 通过大盘强弱得到持仓比例
        orghold = 0.1
        closed = df['close'].values
        price = df['close'].tolist()[-1]
        ma20 = talib.SMA(closed, timeperiod=20)
        ma60 = talib.SMA(closed, timeperiod=60)
        angel20 = self.data_to_deg(ma20[-6:-1])
        angel60 = self.data_to_deg(ma60[-6:-1])
        if price > ma60[-1] and price > ma20[-1]:
            orghold = 1
        elif price > ma60[-1] and price < ma20[-1]:
            orghold = 0.5
        elif price < ma60[-1] and price > ma20[-1]:
            orghold = 0.3
        elif price < ma60[-1] and price < ma20[-1]:
            orghold = 0.1
        return orghold
    # ===================================================================================================================
    # 将输入的数据序列拟合成直线，输出斜率，格式为度

    def data_to_deg(self, data):
        deg_data = 0

        try:
            y_arr = data/np.mean(data)
            x_arr = np.arange(0, len(y_arr))
            x_b_arr = sm.add_constant(x_arr)  # 添加常数列1
            model = sm.OLS(y_arr, x_b_arr).fit()  # 使用OLS做拟合
            rad = model.params[1]  # y = kx + b :params[1] = k
            deg_data = np.rad2deg(rad)  # 弧度转换为角度
        except:
            pass
        return round(deg_data, 2)

    def GoldenCross(self, fast, slow):
        # if  not fast or not slow :
        #    return False
        if fast[-1] > slow[-1] and fast[-2] < slow[-2]:
            return True
        else:
            return False

    def DeathCross(self, fast, slow):
        # if  not fast or not slow :
        #    return False
        if fast[-1] < slow[-1] and fast[-2] > slow[-2]:
            return True
        else:
            return False

    def LLV(self, data, period):
        return data[-1-period:-1].min()

    def HHV(self, data, period):
        return np.max(data[-1-period:-1])

    def EMA(self, c, N):
        Y = 0
        n = 1
        for ci in c[-N:]:
            Y = (2 * ci + (n - 1) * Y) / (n + 1)
            n += 1
        return Y

    def EMA2(self, c, N, denominator=1):
        if N >= 1:
            if denominator == 1:
                denominator = sum(range(N + 1))
            return N / denominator * c[-1] + EMA2(c[len(c) - N:len(c) - 1], N - 1, denominator)
        else:
            return 0

    def SMA(self, c, N):
        pass

    def zig(self, df, x=0.10):

        ZIG_STATE_START = 0
        ZIG_STATE_RISE = 1
        ZIG_STATE_FALL = 2
        peer_i = 0
        candidate_i = None
        scan_i = 0
        peers = [0]
        closed = df['close'].values
        #
        k = talib.SMA(closed, timeperiod=5)
        k = k[5:-1]
        # 22年3月修改了代码，由原来的收盘价改为了5日均线价
        # 原代码 k=df['close'].values

        # k=df['close'].values
        d = df["trade_date"]
        #d = df['date']
        z = np.zeros(len(k))
        state = ZIG_STATE_START
        while True:
            # print(peers)
            scan_i += 1
            if scan_i == len(k) - 1:
                # 扫描到尾部
                if candidate_i is None:
                    peer_i = scan_i
                    peers.append(peer_i)
                else:
                    if state == ZIG_STATE_RISE:
                        if k[scan_i] >= k[candidate_i]:
                            peer_i = scan_i
                            peers.append(peer_i)
                        else:
                            peer_i = candidate_i
                            peers.append(peer_i)
                            peer_i = scan_i
                            peers.append(peer_i)
                    elif state == ZIG_STATE_FALL:
                        if k[scan_i] <= k[candidate_i]:
                            peer_i = scan_i
                            peers.append(peer_i)
                        else:
                            peer_i = candidate_i
                            peers.append(peer_i)
                            peer_i = scan_i
                            peers.append(peer_i)
                break

            if state == ZIG_STATE_START:
                if k[scan_i] >= k[peer_i] * (1 + x):
                    candidate_i = scan_i
                    state = ZIG_STATE_RISE
                elif k[scan_i] <= k[peer_i] * (1 - x):
                    candidate_i = scan_i
                    state = ZIG_STATE_FALL
            elif state == ZIG_STATE_RISE:
                if k[scan_i] >= k[candidate_i]:
                    candidate_i = scan_i
                elif k[scan_i] <= k[candidate_i]*(1-x):
                    peer_i = candidate_i
                    peers.append(peer_i)
                    state = ZIG_STATE_FALL
                    candidate_i = scan_i
            elif state == ZIG_STATE_FALL:
                if k[scan_i] <= k[candidate_i]:
                    candidate_i = scan_i
                elif k[scan_i] >= k[candidate_i]*(1+x):
                    peer_i = candidate_i
                    peers.append(peer_i)
                    state = ZIG_STATE_RISE
                    candidate_i = scan_i

        # 线性插值， 计算出zig的值
        for i in range(len(peers) - 1):
            peer_start_i = peers[i]
            peer_end_i = peers[i+1]
            start_value = k[peer_start_i]
            end_value = k[peer_end_i]
            a = (end_value - start_value)/(peer_end_i - peer_start_i)  # 斜率
            for j in range(peer_end_i - peer_start_i + 1):
                z[j + peer_start_i] = start_value + a*j

        # plt.plot(z)
        return z


if __name__ == "__main__":
    a = tools()
