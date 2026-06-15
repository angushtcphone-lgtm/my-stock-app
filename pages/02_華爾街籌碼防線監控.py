import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import requests
import datetime
import io
import random

# 1. 網頁基礎設定
st.set_page_config(page_title="華爾街隱形力量 - 核心指標監控儀表板", layout="wide")
st.title("📊 核心指標與風險評估自動指引儀表板 (v3.0 - 跨國路由版)")
st.caption("即時時空背景：2026 年 6 月 FOMC 會議與美伊協議關鍵週")

# 【高級偽裝 Session】
@st.cache_resource
def get_stealth_session():
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8'
    })
    return session

# 2. 保持監控清單狀態
if 'tickers' not in st.session_state:
    st.session_state.tickers = ["2330.TW", "MU"]

# 3. 側邊欄：管理系統
st.sidebar.header("🛠️ 監控清單管理")
new_ticker = st.sidebar.text_input("輸入股票代碼 (例如: NVDA, AAPL):").upper().strip()

if st.sidebar.button("➕ 加入監控清單"):
    if new_ticker and new_ticker not in st.session_state.tickers:
        st.session_state.tickers.append(new_ticker)
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
        st.rerun()

# 4. 核心量化計算邏輯
def calculate_indicators(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.droplevel(1)
        
    # 標準化各個資料庫的欄位名稱 (大小寫相容處理)
    df.columns = [c.title() for c in df.columns]
    
    df['Ema_20'] = df['Close'].ewm(span=20, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['Rsi'] = 100 - (100 / (1 + rs))
    
    df['Vol_Ma20'] = df['Volume'].rolling(window=20).mean()
    df['Is_Distribution'] = (df['Close'] < df['Close'].shift(1)) & (df['Volume'] > df['Vol_MA20'])
    return df

# 5. 主畫面：數據巡航
if not st.session_state.tickers:
    st.info("目前監控清單為空，請在左側側邊欄加入股票代碼。")
else:
    session = get_stealth_session()
    
    for ticker_symbol in st.session_state.tickers:
        st.subheader(f"🔍 標的分析：{ticker_symbol}")
        
        data = pd.DataFrame()
        source_used = "Yahoo Finance"
        
        # --- 💥 跨國雙軌多源路由調度系統 ───
        # 路由 1：常態 Yahoo 管道嘗試
        try:
            data = yf.download(tickers=ticker_symbol, period="4m", session=session, progress=False, auto_adjust=True)
        except Exception:
            pass
            
        # 路由 2：若 Yahoo 全面陣亡 (empty)，無縫切換至歐洲 Stooq 頂級數據備援中心
        if data.empty or len(data) < 20:
            try:
                source_used = "歐洲 Stooq 備援中心"
                # 自動轉譯代碼格式
                if ".TW" in ticker_symbol:
                    stooq_ticker = ticker_symbol.lower()
                else:
                    stooq_ticker = f"{ticker_symbol.lower()}.us"
                    
                stooq_url = f"https://stooq.com/q/d/l/?s={stooq_ticker}&i=d"
                resp = session.get(stooq_url, timeout=15)
                
                if resp.status_code == 200 and "Date" in resp.text:
                    data = pd.read_csv(io.StringIO(resp.text), parse_dates=['Date'], index_col='Date')
                    data = data.sort_index().tail(90) # 擷取最近 90 個交易日數據
            except Exception as e:
                pass

        # --- 數據渲染與規則判定中心 ---
        if data.empty or len(data) < 20:
            st.error(f"❌ {ticker_symbol} 跨國所有數據庫（Yahoo & Stooq）皆遭阻斷。此為極端網路異常。")
            continue
            
        try:
            df = calculate_indicators(data)
            current_row = df.iloc[-1]
            prev_row = df.iloc[-2]
            
            curr_price = float(current_row['Close'])
            curr_ema20 = float(current_row['Ema_20'])
            curr_rsi = float(current_row['Rsi'])
            curr_vol = float(current_row['Volume'])
            ma20_vol = float(current_row['Vol_MA20'])
            dist_to_ema20 = ((curr_price - curr_ema20) / curr_ema20) * 100
            
            # 數據儀表板呈現
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("最新收盤價", f"{curr_price:.2f}")
            m2.metric("最新 EMA 20 防線", f"{curr_ema20:.2f}")
            m3.metric("RSI (14D)", f"{curr_rsi:.1f}", delta=f"{curr_rsi - float(prev_row['Rsi']):.1f}")
            m4.metric("距離 EMA 20 乖離率", f"{dist_to_ema20:.2f}%")
            
            st.caption(f"數據來源防護盾：此標的目前由【{source_used}】即時安全護航調度中")
            
            st.markdown("##### 🚦 系統硬性規則動態指引")
            
            if bool(current_row['Is_Distribution']):
                st.error(f"🚨 警告：今日符合【分佈日】特徵！大戶有高檔減碼嫌疑（今日量: {curr_vol:,.0f} / 均量: {ma20_vol:,.0f}）。")
            else:
                st.success("💡 籌碼流向：今日未出現主力異常放量倒貨特徵。")
                
            if curr_rsi > 75:
                st.warning("❌ 【系統指引：極度超買區】RSI 破 75，高槓桿散戶瘋狂追價中。依據帳本鐵律，此時嚴禁追高建倉，保留現金。")
            elif dist_to_ema20 < 1.0 and dist_to_ema20 > -1.0:
                if curr_vol < ma20_vol * 0.85:
                    st.success("🔥 【系統指引：符合安全建倉條件】股價首次拉回且極度貼近 EMA 20，同時成交量出現【量極縮】。允許分批建立多頭倉位。")
                else:
                    st.warning("⚠️ 【系統指引：觀望不接刀】股價貼近 EMA 20 但成交量未縮，代表多空震盪激烈，需等待收盤前確認是否收長下影線。")
            elif curr_price < curr_ema20 and curr_vol > ma20_vol:
                st.error("🚨 【系統指引：趨勢破壞！多單停損】股價放量跌破 EMA 20 防線。主力成本底牌遭擊穿，嚴禁接刀，多單應執行停損。")
            else:
                st.info("🔵 【系統指引：常態趨勢區】目前股價處於常態波動區間，未觸及極端買賣點。請耐心等待回測或突破訊號。")
                
            st.markdown("---")
            
        except Exception as e:
            st.error(f"處理解析 {ticker_symbol} 時發生錯誤: {e}")
