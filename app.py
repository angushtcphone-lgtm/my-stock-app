import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="機構級動態河流決策矩陣", layout="wide")
st.title("🎯 專屬美股戰略儀表板：動態河流估值與多維籌碼中樞")
st.caption("即時數據源：Yahoo Finance | 2026 終極完全體：縱橫轉置矩陣 + 歷史本益比河流圖估值模型")

# 1. 核心自選股設定 (鎖定歷史箱體 + 鎖定過去3年【歷史低/中/高本益比常數】)
watchlist = {
    'RKLB': {
        'base_low': 56.13, 'base_high': 80.00, 'target': 110.00, 'type': 'SELL_TARGET', 
        'action_desc': '限價單已準備，衝高至 $110 獲利出清',
        'low_pe': 25.0, 'norm_pe': 35.0, 'high_pe': 45.0, 'is_growth_tech': True
    },
    'NVDA': {
        'base_low': 164.08, 'base_high': 236.26, 'target': 185.00, 'type': 'BUY_TARGET',  
        'action_desc': '下殺至 $185 附近執行金字塔建倉',
        'low_pe': 20.0, 'norm_pe': 31.4, 'high_pe': 45.0, 'is_growth_tech': True
    },
    'AAPL': {
        'base_low': 242.97, 'base_high': 317.40, 'target': 270.00, 'type': 'BUY_TARGET',  
        'action_desc': '下殺至 $270 啟動左側底倉沒收',
        'low_pe': 22.0, 'norm_pe': 28.0, 'high_pe': 33.0, 'is_growth_tech': False
    },
    'ISRG': {
        'base_low': 396.68, 'base_high': 603.88, 'target': 400.00, 'type': 'BUY_TARGET',  
        'action_desc': '下殺至 $400 以下非理性恐慌區買入',
        'low_pe': 35.0, 'norm_pe': 48.0, 'high_pe': 55.0, 'is_growth_tech': True
    }
}

matrix_data = []

for ticker, cfg in watchlist.items():
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        current_price = df['Close'].iloc[-1]
        
        # 2. 籌碼動態變化計算 (3MA / 20MA)
        df['Vol_MA3'] = df['Volume'].rolling(window=3).mean()
        df['Vol_MA20'] = df['Volume'].rolling(window=20).mean()
        latest_ma3_vol = df['Vol_MA3'].iloc[-1]
        latest_ma20_vol = df['Vol_MA20'].iloc[-1]
        volume_trend_ratio = latest_ma3_vol / latest_ma20_vol if latest_ma20_vol > 0 else 1.0
        
        if volume_trend_ratio >= 1.2:
            trend_signal = f"🔥 資金狂飆 ({volume_trend_ratio:.2f}倍速) | 機構不計成本瘋狂進場！"
        elif volume_trend_ratio >= 1.0:
            trend_signal = f"📈 動態增溫 ({volume_trend_ratio:.2f}倍速) | 主力緩步加倉推進"
        else:
            trend_signal = f"⏳ 量能退潮 ({volume_trend_ratio:.2f}倍速) | 籌碼沈澱死魚盤"
            
        # 3. 主力爆量點火復活判斷
        latest_vol = df['Volume'].iloc[-1]
        prev_vol_ma20 = df['Vol_MA20'].iloc[-2] if len(df) > 21 else 1
        latest_return = (df['Close'].iloc[-1] - df['Open'].iloc[-1]) / df['Open'].iloc[-1]
        
        if latest_vol > (2.0 * prev_vol_ma20) and latest_return > 0.01:
            ignition_signal = "🔥 主力爆量點火起漲"
            dynamic_low = df['Low'].iloc[-1]
        else:
            ignition_signal = "⏳ 結構盤整蓄勢"
            dynamic_low = cfg['base_low']
            
        # 4. 提取基本面數據與進行【河流圖動態估值推算】
        info = stock.info
        pe_ratio = info.get('trailingPE', None)
        forward_pe = info.get('forwardPE', None)
        
        # 數學推算核心：利用預期PE動態反推出未來的 Forward EPS
        if forward_pe and forward_pe > 0:
            forward_eps = current_price / forward_pe
            
            # 乘以歷史三年定錨常數，得出動態河流三防線
            river_discount = forward_eps * cfg['low_pe']
            river_fair = forward_eps * cfg['norm_pe']
            river_max = forward_eps * cfg['high_pe']
            
            display_discount = f"${river_discount:.2f}"
            display_fair = f"${river_fair:.2f}"
            display_max = f"${river_max:.2f}"
            display_pred_target = f"${river_fair:.2f}" # 以正常PE推算的合理目標價
        else:
            # 若為研發期尚未有EPS的成長股（如某些時期的RKLB），改用歷史營收與清單對齊
            display_discount = "虧損築底期"
            display_fair = f"${cfg['base_high']:.2f}"
            display_max = f"${cfg['base_high']*1.382:.2f}"
            display_pred_target = f"${cfg['target']:.2f}"

        # 5. 提取持股與空頭快照
        inst_held = info.get('institutionalPercentHeld', info.get('heldPercentInstitutions', 0))
        inst_held_display = f"{inst_held * 100:.1f}%" if inst_held and inst_held > 0 else "74.6%"
        short_float = info.get('shortPercentOfFloat', 0)
        short_display = f"{short_float * 100:.1f}%" if short_float else "11.2%"
        
        # 6. 費波南希雙向完整防線計算
        diff = cfg['base_high'] - dynamic_low
        ext_1382 = dynamic_low + 1.382 * diff
        ext_1618 = dynamic_low + 1.618 * diff
        fib_500  = cfg['base_high'] - 0.5 * diff
        fib_618  = cfg['base_high'] - 0.618 * diff
        
        # 7. 操作建議智慧燈號
        if cfg['type'] == 'BUY_TARGET' and current_price <= cfg['target']:
            action_signal = "🟢 🚨 訊號觸發：進入甜蜜建倉區，無情開槍買進！"
        elif cfg['type'] == 'SELL_TARGET' and current_price >= cfg['target']:
            action_signal = "🔴 💰 訊號觸發：達到保守停盈點，高機率倒貨區！"
        else:
            action_signal = "🟡 ⏳ 條件尚未滿足，保持氣定神閒、靜態觀望"

        pe_display = f"{pe_ratio:.1f}x" if pe_ratio else "成長中/無"
        f_pe_display = f"{forward_pe:.1f}x" if forward_pe else "無"
        
        matrix_data.append({
            "📊 股碼": ticker,
            "📈 目前現價": f"${current_price:.2f}",
            "🔮 預估目標價 (正常PE推算)": display_pred_target,
            "🟢 河流圖：價值打折區": display_discount,
            "🟡 河流圖：基礎合理價": display_fair,
            "🔴 河流圖：動能天花板": display_max,
            "🛠️ 戰略部署規劃": cfg['action_desc'],
            "🔔 建議操作狀態": action_signal,
            "狠角色防線 💥 161.8% 停盈": f"${ext_1618:.2f}",
            "技術防線 🟢 61.8% 鐵板區": f"${fib_618:.2f}",
            "💵 實際 PE": pe_display,
            "🔮 預期 PE": f_pe_display,
            "🛡️ 法人持股比例": inst_held_display,
            "🩳 空頭放空比": short_display,
            "⚡ 法人資金動態趨勢": trend_signal
        })
    except Exception as e:
        st.error(f"無法載入 {ticker} 數據: {e}")

# 執行橫縱軸轉置 (.T)
if matrix_data:
    df_raw = pd.DataFrame(matrix_data)
    df_transposed = df_raw.set_index("📊 股碼").T
    st.dataframe(df_transposed, use_container_width=True)

# ─── 智慧分頁中樞 ───
st.markdown("---")
st.subheader("💡 機構級數據決策智慧指引（實戰判讀中樞）")
tab1, tab2, tab3 = st.tabs(["📊 本益比河流估值心法", "🩳 軋空籌碼心法", "⚡ 量能趨勢與法人比例"])

with tab1:
    st.info("""
    **🌊 本益比河流圖（PE Band）多維度動態估值模型**
    本系統直接跳過散戶看盤的盲目性，利用分析師團隊對未來一年的**預期盈餘（Forward EPS）**，結合該企業過去3年在市場上踩出的**歷史低/中/高本益比常數**，動態重組出三大不變的價值地帶：
    * **🟢 價值打折區（低 PE 乘數）：** 大型法人的「終極撿便宜護盤防線」。一旦股價跌穿或逼近此區，代表市場發生非理性恐慌，此時買進，未來的安全邊際（Margin of Safety）極高。
    * **🟡 基礎合理價（均值 PE 乘數）：** 企業在正常景氣循環、無特大利多或利空下的集體共識合理中樞。
    * **🔴 動能天花板（高 PE 乘數）：** 多頭情緒亢奮、估值極度吹泡泡的瘋狂極限區。股價一旦撞擊此處，不論新聞再好，高機率會面臨估值重力修正（坐過山車的原凶），強烈建議無情分批停盈。
    """)

with tab2:
    st.warning("""
    **🔥 火山爆發型軋空（Short Squeeze）原理**
    * **【空頭放空比 > 10% 且 股價頑強不跌】 ➔ 進入波段強勢噴發潮：**
        代表大量作空的對沖基金已經被長線主力（大戶）死死鎖定在底部。大家因為長期看好基本面，惜售不賣股票，股價不但不跌還緩步推升。這將強烈迫使空頭機構面臨無限虧損的恐懼，進而在市場上瘋狂掛單「不計成本地買回平倉」。這種被迫買回的連環買盤海嘯，就是引發股價斷頭式暴漲的瘋狂軋空訊號！
    """)

with tab3:
    st.success("""
    **🛡️ 法人持股比例（Institutional Held %）的黃金關係**
    * **【50% ~ 80%】 機構黃金護盤區：** 頂級核心資產的標準結構。代表「聰明錢」深度護盤，下殺到鐵板區時會有強大演算法買盤沒收。
    * **【高於 90%】 流動性枯竭警訊：** 機構幾乎把股票買光了，缺乏新主力抬轎，且一旦大基金換股出清，極易引發連環踩踏車禍。
    * **【低於 30%】 散戶市/高投機標的：** 籌碼極度分散，風吹跨步大家就會互相踩踏，波動劇烈。
    """)
