import streamlit as st
import pandas as pd
import numpy as np
import os
from Bybit import Bybit, Wallet
from datetime import datetime, date
import matplotlib.pyplot as plt
import hmac

import json
DEBUG = bool(os.getenv("DEBUG", "False") == "True")
config = json.load(open('config.json' if not DEBUG else 'config.test.json')) 

def check_password():
    def password_entered():
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the password.
        else:
            st.session_state["password_correct"] = False
    if st.session_state.get("password_correct", False):
        return True
    st.text_input(
        "Password", type="password", on_change=password_entered, key="password"
    )
    if "password_correct" in st.session_state:
        st.error("😕 Password incorrect")
    return False


if not check_password() and not DEBUG:
    st.stop()  # Do not continue if check_password is not True.


@st.cache_data
def fetch_wallet(account_name, account, datetime):
    bybit = Bybit(
        api_key=account['API_KEY'],
        api_secret=account['API_SECRET'],
        account_type=account['ACCOUNT_TYPE'],
        coin=account['COIN'],
        category=account['CATEGORY'],
        testnet=account['TESTNET'],
    )
    bybit.get_balance()
    return {
        'account_name': account_name,
        'wallet_balance': bybit.wallet.wallet_balance,
        'cum_realised_pnl': bybit.wallet.cum_realised_pnl,
        'unrealised_pnl': bybit.wallet.unrealised_pnl,
        'unrealised_%': round(bybit.wallet.unrealised_pnl/ bybit.wallet.wallet_balance * 100, 2),
        'time': bybit.wallet.time,
    }

@st.cache_data
def fetch_closed_pnl(account_name, account, start_date, datetime):
    bybit = Bybit(
        api_key=account['API_KEY'],
        api_secret=account['API_SECRET'],
        account_type=account['ACCOUNT_TYPE'],
        coin=account['COIN'],
        category=account['CATEGORY'],
        testnet=account['TESTNET'],
    )
    bybit.get_closed_pnl(start_time=start_date)
    return bybit
    

# bybit
st.markdown("# Bybit Account")
bybit_acccounts = config['bybit']

df = pd.DataFrame(
    columns=['account_name', 'wallet_balance', 'cum_realised_pnl', 'unrealised_pnl', 'time'],
)
select_choices = ("--- Please select Account ---",)
bar = st.progress(0)
bar_i = 0
for account_name in bybit_acccounts:
    result = fetch_wallet(account_name, bybit_acccounts[account_name], datetime.now().strftime('%Y-%m-%d %H:%M'))
    df = pd.concat([df, pd.DataFrame([result])])
    select_choices  = select_choices + (account_name,)
    bar_i += 1
    bar.progress(bar_i * 1 / len(bybit_acccounts))

df['time'] = pd.to_datetime(df['time'] , unit='ms')
df.set_index("account_name", inplace=True)
df

st.markdown("## Closed Pnl")

account_select = st.selectbox(
    'Select Account',
    select_choices
)

start_date = st.date_input("Start Date", value=datetime.now()-pd.Timedelta(days=6))
start_date = datetime.combine(start_date, datetime.min.time())

if account_select in bybit_acccounts:
    st.markdown("### " + account_select)
    account = bybit_acccounts[account_select]
    bybit = fetch_closed_pnl(account_select, bybit_acccounts[account_select], start_date.timestamp()*1000, datetime.now().strftime('%Y-%m-%d %H:%M'))
    st.line_chart(bybit.closed_pnl["cumClosedPnl"])
    bybit.closed_pnl
