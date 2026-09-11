import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import plotly.express as px

# --- 1. 頁面初始設定與動態狀態 ---
st.set_page_config(page_title="學員能力評估系統", page_icon="▪", layout="centered")

if "searched" not in st.session_state:
    st.session_state.searched = False

# --- 2. 載入 Google Fonts 與極簡風格 CSS 樣式 ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important;
    }

    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    .stApp {
        background-color: #F9F9F8;
        color: #222222;
    }

    .custom-title {
        font-family: 'Noto Serif TC', serif !important;
        font-size: 60px !important;
        font-weight: 700 !important;
        color: #222222 !important;
        text-align: center;
        letter-spacing: 0.05em;
        margin-bottom: 10px;
    }

    .custom-subtitle {
        font-family: 'Noto Serif TC', serif !important;
        font-size: 42px !important;
        font-weight: 400 !important;
        color: #8C8C88 !important;
        text-align: center;
        margin-bottom: 40px;
    }

    .stTextInput>div>div>input {
        background-color: #FFFFFF !important;
        border: 1px solid #E2E2DF !important;
        border-radius: 3px !important;
        color: #222222 !important;
        font-size: 20px !important;
        padding: 12px 16px !important;
        font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #1A1A1A !important;
        box-shadow: none !important;
    }

    .stButton>button {
        background-color: #222222 !important; 
        color: #FFFFFF !important;
        border-radius: 3px !important;
        border: 1px solid #222222 !important;
        padding: 12px 24px !important;
        font-weight: 600;
        font-size: 20px !important;
        letter-spacing: 0.1em;
        font-family: "Microsoft JhengHei", "微軟正黑體", sans-serif !important;
        transition: all 0.2s ease;
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #1A1A1A !important;
        border-color: #1A1A1A !important;
    }

    hr {
        border-color: #EEEEEB !important;
        margin: 30px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. Google 試算表連線設定 (支援本機與雲端自動切換) ---
scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

if "gcp_service_account" in st.secrets:
    # 將 Secrets 轉為標準字典格式
    creds_dict = dict(st.secrets["gcp_service_account"])
    # 💡 終極修復：強制將文字的 \n 替換為真實的換行符號
    creds_dict["private_key"] = creds_dict["private_key"].replace('\\n', '\n')
    creds = Credentials.from_service_account_info(creds_dict, scopes=scopes)
else:
    # 本地環境：讀取資料夾內的 credentials.json 檔案
    creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)

client = gspread.authorize(creds)

SHEET_URL = "https://docs.google.com/spreadsheets/d/1uU5QiSpML3-vroTFrMVrzMu0rj8gMLYIsyekyYxSVME/edit?gid=1075932015#gid=1075932015" 
spreadsheet = client.open_by_url(SHEET_URL)

# --- 4. Plotly Express 雷達圖繪製函式 ---
def create_radar_chart(core, suspension, mobility):
    df = pd.DataFrame(dict(
        r=[core, suspension, mobility],
        theta=['核心', '懸吊', '活動度']
    ))
    
    fig = px.line_polar(
        df, 
        r='r', 
        theta='theta', 
        line_close=True,
        template="plotly_white"
    )
    
    fig.update_traces(
        fill='toself',
        fillcolor='rgba(34, 34, 34, 0.12)',
        line=dict(color='#222222', width=2),
        marker=dict(size=6, color='#222222')
    )
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True, 
                range=[0, 5], 
                tickfont=dict(size=11, color='#8C8C88', family='Microsoft JhengHei'),
                gridcolor='#E2E2DF',
                linecolor='#E2E2DF'
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='#222222', family='Noto Serif TC'),
                linecolor='#E2E2DF'
            ),
            bgcolor='#F9F9F8'
        ),
        showlegend=False,
        paper_bgcolor='#F9F9F8',
        plot_bgcolor='#F9F9F8',
        margin=dict(l=40, r=40, t=30, b=30)
    )
    return fig

# --- 5. 版面配置：將核心互動區限縮在中央 80% 寬度 ---
_, col2, _ = st.columns([1, 8, 1])

with col2:
    if not st.session_state.searched:
        st.markdown("<div style='height: 10vh;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="custom-title">SKILL ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown('<div class="custom-subtitle">學員能力評估系統</div>', unsafe_allow_html=True)
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    else:
        st.markdown('<div style="font-family: \'Noto Serif TC\', serif; font-size: 36px; font-weight: 700; color: #222222; margin-bottom: 2px;">SKILL ANALYSIS</div>', unsafe_allow_html=True)
        st.markdown('<div style="font-size: 16px; color: #8C8C88; margin-bottom: 20px;">學員能力評估系統</div>', unsafe_allow_html=True)

    sub_col1, sub_col2 = st.columns([3, 1])
    with sub_col1:
        user_name = st.text_input("學員姓名", placeholder="請輸入姓名...", label_visibility="collapsed")
    with sub_col2:
        search_button = st.button("查 詢")

    # --- 6. 查詢邏輯與結果渲染 ---
    if search_button:
        if user_name:
            st.session_state.searched = True
            found = False
            
            for worksheet in spreadsheet.worksheets():
                all_values = worksheet.get_all_values()
                
                for i in range(len(all_values)):
                    row = all_values[i]
                    
                    if row and row[0].strip() == "測量者":
                        for j in range(1, len(row)):
                            if row[j].strip() == user_name.strip():
                                try:
                                    level = all_values[i+4][j]
                                    
                                    try:
                                        core = float(all_values[i+1][j])
                                    except ValueError:
                                        core = 0.0
                                        
                                    try:
                                        suspension = float(all_values[i+2][j])
                                    except ValueError:
                                        suspension = 0.0
                                        
                                    try:
                                        mobility = float(all_values[i+3][j])
                                    except ValueError:
                                        mobility = 0.0

                                    st.markdown("---")
                                    st.markdown(f"""
                                        <div style='font-family: "Noto Serif TC", serif; font-size: 22px; font-weight: 600; color: #222222; margin-bottom: 10px;'>
                                            {user_name} <span style='font-size: 15px; color: #8C8C88; font-weight: 400;'>— 等級：{level}</span>
                                        </div>
                                    """, unsafe_allow_html=True)
                                    
                                    fig = create_radar_chart(core, suspension, mobility)
                                    st.plotly_chart(fig, use_container_width=True)
                                    
                                    found = True
                                    break 
                                    
                                except IndexError:
                                    st.error("表格讀取錯誤，請確認格子配置。")
                                    break
                                    
                    if found:
                        break 
                        
                if found:
                    break 
                    
            if not found:
                st.warning("找不到此姓名的資料，請確認輸入是否正確。")
        else:
            st.warning("請先輸入姓名再點擊查詢。")