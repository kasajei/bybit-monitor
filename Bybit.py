from pybit.unified_trading import HTTP
import pandas as pd

class Wallet:
    def __init__(self, equity, wallet_balance, available_to_withdraw, cum_realised_pnl, unrealised_pnl):
        self.equity = equity
        self.wallet_balance = wallet_balance
        self.available_to_withdraw = available_to_withdraw
        self.cum_realised_pnl = cum_realised_pnl
        self.unrealised_pnl = unrealised_pnl
        self.time = None

    def update(self, equity, wallet_balance, available_to_withdraw, cum_realised_pnl, unrealised_pnl, time):
        self.equity = equity
        self.wallet_balance = wallet_balance
        self.available_to_withdraw = available_to_withdraw
        self.cum_realised_pnl = cum_realised_pnl
        self.unrealised_pnl = unrealised_pnl
        self.time = time
        


class Bybit:
    def __init__(self, api_key, api_secret, account_type, coin, category, testnet=False):
        self.api_key = api_key
        self.api_secret = api_secret
        self.account_type = account_type
        self.coin = coin
        self.category = category
        self.session = HTTP(
            testnet=testnet,
            api_key=api_key,
            api_secret=api_secret,
        )
        self.wallet = Wallet(0, 0, 0, 0, 0)
        self.closed_pnl = None

    def get_balance(self):
        balance = self.session.get_wallet_balance(accountType=self.account_type, coin=self.coin)
        if self.account_type == "UNIFIED":
            total = balance["result"]["list"][0]
            coin = balance["result"]["list"][0]["coin"][0]
            self.wallet.update(
                total['totalEquity'],
                total['totalWalletBalance'],
                total['totalAvailableBalance'],
                coin['cumRealisedPnl'],
                total['totalPerpUPL'],
                balance["time"]
            )
        else:
            coin = balance["result"]["list"][0]["coin"][0]
            self.wallet.update(
                coin['equity'],
                coin['walletBalance'],
                coin['availableToWithdraw'],
                coin['cumRealisedPnl'],
                coin['unrealisedPnl'],
                balance["time"]
            )

    
    def get_closed_pnl(self, start_time=None):
        results_list = []
        cursor = None
        while True:
            results = self.session.get_closed_pnl(category=self.category, limit=100, cursor=cursor, startTime=start_time)
            results_list += results["result"]["list"]
            cursor = results["result"]["nextPageCursor"]
            if cursor == "" or cursor == None or start_time == None:
                break
        df = pd.DataFrame(results_list, columns=['createdTime', 'closedPnl', "fillCount"])
        df['createdTime'] = pd.to_datetime(df['createdTime'] , unit='ms')
        df["closedPnl"] = pd.to_numeric(df["closedPnl"])
        df["fillCount"] = pd.to_numeric(df["fillCount"])
        df = df.rename(columns={'createdTime': 'timestamp'})
        df.set_index("timestamp", inplace=True)
        df = df.resample('D').sum()
        df["cumClosedPnl"] = df["closedPnl"].cumsum()
        df.sort_index(inplace=True, ascending=False)
        self.closed_pnl = df
