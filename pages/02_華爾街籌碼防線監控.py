import streamlit as st
import pandas as pd
import numpy as np
import requests
import datetime
import io

# 1. 網頁基礎設定
st.set_page_config(page_title="華爾街隱形力量 - 核心指標監控儀表板", layout="wide")
st.title("📊 核心指標與風險評估自動指引儀表板 (v7.0 - URL狀態鎖定版)")
st.caption("即時時空背景：2026 年 6 月 FOMC 會議與美伊協議關鍵週")

# 🔥 【永久記憶功能】從瀏覽器 URL 網址列讀取股票清單，徹底解決重新整理消失的問題
if "list" in st.query_params:
    try:
        url_tickers = st.query_params["list"].split(",")
        # 過濾空字串
        st.session_state.tickers = [t for t in url_tickers if t]
    except Exception:
        st.session_state.tickers = ["2330.TW", "MU"]
elif 'tickers' not in st.session_state:
    st.session_state.tickers = ["2330.TW", "MU"]

# 2. 側邊欄：管理系統
st.sidebar.header("🛠️ 監控清單管理")
new_ticker = st.sidebar.text_input("輸入股票代碼 (美股如 NVDA / 台股如 2344.TW):").upper().strip()

if st.sidebar.button("➕ 加入監控清單"):
    if new_ticker and new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)
        # 🔥 同步寫入 URL 網址列
        st.query_params["list"] = ",".join(st.session_state.tickers)
        st.rerun()
    elif new_ticker in st.session_state.tickers:
        st.sidebar.warning("該股票已在監控清單中！")

st.sidebar.write("---")
st.sidebar.subheader("📌 當前監控中股票")
for t in st.session_state.tickers:
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"**{t}**")
    if col2.button("🗑️", key=f"del_{t}"):
        st.session_state.tickers.remove(t)
        # 🔥 同步更新 URL 網址列
        st.query_params["list"] = ",".join(st.session_state.tickers)
        st.rerun()

# 3. 核心數據直連引擎 (拆除人工仿真數據，確保數據真實性)
def get_tw_stock_official(ticker_no):
    today = datetime.datetime.now()
    last_month = today - datetime.timedelta(days=32)
    dates_to_fetch = [last_month.strftime("%Y%m%d"), today.strftime("%Y%m%d")]
    all_rows = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    
    for dt in dates_to_fetch:
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&stockNo={ticker_no}&date={dt}"
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            if resp.status_code == 200:
                json_data = resp.json()
                if 'data' in json_data and isinstance(json_data['data'], list):
                    all_rows.extend(json_data['data'])
        except Exception:
            pass
            
    if not all_rows:
        return pd.DataFrame()
        
    raw_df = pd.DataFrame(all_rows)
    if raw_df.shape[1] == 9:
        raw_df.columns = ['Date', 'Volume', 'Amount', 'Open', 'High', 'Low', 'Close', 'Change', 'Tx']
        def parse_roc_date(date_str):
            try:
                parts = str(date_str).split('/')
                year = int(parts[0]) + 1911
                return pd.to_datetime(f"{year}-{parts[1]}-{parts[2]}")
            except Exception:
                return pd.NaT
        raw_df['ParsedDate'] = raw_df['Date'].apply(parse_roc_date)
        raw_df = raw_df.dropna(subset=['ParsedDate']).drop_duplicates(subset=['ParsedDate']).sort_values('ParsedDate')
        raw_df.set_index('ParsedDate', inplace=True)
        for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
            raw_df[col] = raw_df[col].astype(str).str.replace(',', '').replace('--', np.nan)
            raw_df[col] = pd.to_numeric(raw_df[col], errors='coerce')
        return raw_df.dropna(subset=['Close'])
    return pd.DataFrame()

def get_us_stock_backup(ticker_symbol):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'}
    url = f"https://stooq.com/q/d/l/?s={ticker_symbol.lower()}.us&i=d"
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200 and "Date" in resp.text:
            df = pd.read_csv(io.StringIO(resp.text), parse_dates=['Date'], index_col='Date')
            return df.sort_index().tail(60)
    except Exception:
        pass
    return pd.DataFrame()

# 4. 指標計算核心
def calculate_indicators(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
    df.columns = [c.title() for c in df.columns]
    
    df['EMA_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
    df['Is_Distribution'] = (df['Close'] < df['Close'].shift(1)) & (df['Volume'] > df['Vol_MA20'])
    return df

# 5. 主畫面巡航
for ticker_symbol in st.session_state.tickers:
    st.subheader(f"🔍 標的分析：{ticker_symbol}")
    
    data = pd.DataFrame()
    source_label = ""
    
    if ".TW" in ticker_symbol:
        ticker_no = ticker_symbol.split('.')[0]
        data = get_tw_stock_official(ticker_no)
        source_label = "TWSE 台灣證券交易所官方大數據源"
    else:
        data = get_us_stock_backup(ticker_symbol)
        source_label = "國際開放金融數據備援通道"
        
    # 台股失敗備援
    if data.empty and ".TW" in ticker_symbol:
        try:
            source_label = "跨國開放數據中心 (台股備援路由)"
            stooq_url = f"https://stooq.com/q/d/l/?s={ticker_symbol.lower()}&i=d"
            resp = requests.get(stooq_url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if resp.status_code == 200 and "Date" in resp.text:
                data = pd.read_csv(io.StringIO(resp.text), parse_dates=['Date'], index_col='Date').sort_index().tail(60)
        except Exception:
            pass
            
    # 🔥 誠實回報機制：如果雙軌路由都抓不到真實K線（例如 ONDS 這檔美國小盤股在公用庫未即時建檔），直接顯示明確提示，絕不拿 MU 數據呼弄您
    if data.empty or len(data) < 20:
        st.error(f"⚠️ 數據未達標：【{ticker_symbol}】暫時無法從官方交易所或歐洲備援庫取得足夠的歷史K線。")
        st.info("💡 操盤手提示：請確認代碼是否正確。若代碼正確，代表該特定標的超出了公用備援庫的涵蓋範圍，建議先將主力資金專注於帳本已鎖定的核心權值戰隊（如台積電、華邦電、南亞科、台達電、欣興）。")
        st.markdown("---")
        continue
        
    try:
        df = calculate_indicators(data)
        current_row = df.iloc[-1]
        prev_row = df.iloc[-2]
        
        curr_price = float(current_row['Close'])
        curr_ema20 = float(current_row['EMA_20'])
        curr_rsi = float(current_row['RSI'])
        curr_vol = float(current_row['Volume'])
        ma20_vol = float(current_row['Vol_MA20'])
        dist_to_ema20 = ((curr_price - curr_ema20) / curr_ema20) * 100
        
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("最新收盤價", f"{curr_price:.2f}")
        m2.metric("最新 EMA 20 防線", f"{curr_ema20:.2f}")
        m3.metric("RSI (14D)", f"{curr_rsi:.1f}", delta=f"{curr_rsi - float(prev_row['RSI']):.1f}")
        m4.metric("距離 EMA 20 乖離率", f"{dist_to_ema20:.2f}%")
        
        st.caption(f"🛡️ 安全防護盾：本標的數據已成功由【{source_label}】安全解鎖")
        st.markdown("##### 🚦 系統硬性規則動態指引")
        
        if bool(current_row['Is_Distribution']):
            st.error(f"🚨 警告：今日符合【分佈日】特徵！大戶有高檔減碼嫌疑。")
        else:
            st.success("💡 籌碼流向：今日未出現主力異常放量倒貨特徵。")
            
        if curr_rsi > 75:
            st.warning("❌ 【系統指引：極度超買區】RSI 破 75，高槓桿散戶瘋狂追價中。依據帳本鐵律，此時嚴禁追高建倉，保留現金。")
        elif dist_to_ema20 < 1.0 and dist_to_ema20 > -1.0:
            if curr_vol < ma20_vol * 0.85:
                st.success("🔥 【系統指引：符合安全建倉條件】股價首次拉回且極度貼近 EMA 20，同時成交量出現【量極縮】。允許分批建立多頭倉位。")
            else:
                st.warning("⚠️ 【系統指引：觀望不接刀】股價貼近 EMA 20 但成交量未縮，需等待收盤前確認是否收長下影線。")
        elif curr_price < curr_ema20 and curr_vol > ma20_vol:
            st.error("🚨 【系統指引：趨勢破壞！多單停損】股價放量跌破 EMA 20 防線。主力成本底牌遭擊穿，嚴禁接刀，多單應執行停損。")
        else:
            st.info("🔵 【系統指引：常態趨勢區】目前股價處於常態波動區間，未觸及極端買賣點。請耐心等待回測或突破訊號。")
            
        st.markdown("---")
    except Exception as e:
        st.error(f"指標解析異常: {e}")
