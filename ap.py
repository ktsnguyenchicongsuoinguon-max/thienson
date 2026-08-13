import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ================= 1. THIẾT LẬP GIAO DIỆN & CSS TÙY CHỈNH =================
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", page_icon="logothienson.png", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    header[data-testid="stHeader"] { background: transparent !important; }
    .stAppDeployButton { display: none !important; }
    .block-container { padding-top: 3rem !important; padding-bottom: 2rem !important; }
    
    /* TÙY CHỈNH KHỐI KPI */
    .kpi-card {
        width: 100%; padding: 20px 15px; 
        border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        border: 1px solid var(--border-color); 
        border-left: 6px solid #C62828; 
        display: flex; align-items: center; margin-bottom: 15px; min-height: 115px; 
        background-color: var(--secondary-background-color); 
    }
    .kpi-icon {
        font-size: 2.2rem; margin-right: 15px; 
        background-color: rgba(198, 40, 40, 0.15); 
        padding: 10px; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; min-width: 60px; height: 60px;
    }
    .kpi-details { flex-grow: 1; overflow: hidden; }
    .kpi-title {
        font-size: 0.85rem; font-weight: 800; opacity: 0.7;
        text-transform: uppercase; margin-bottom: 5px; white-space: nowrap;
        overflow: hidden; text-overflow: ellipsis;
        color: var(--text-color);
    }
    .kpi-value { font-size: 1.8rem; font-weight: 900; color: var(--text-color); }
</style>
""", unsafe_allow_html=True)


# ================= 2. ĐỌC DỮ LIỆU =================
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    
    # Chuẩn hóa tên cột
    if 'Đầu Việc' in df.columns: df.rename(columns={'Đầu Việc': 'Hạng Mục'}, inplace=True)
    if 'Đầu Việc Shopdrawing' in df.columns: df.rename(columns={'Đầu Việc Shopdrawing': 'Hạng Mục'}, inplace=True)
    if 'Ghi chú' in df.columns: df.rename(columns={'Ghi chú': 'Vướng Mắc'}, inplace=True)
        
    cols_to_fill = ['Mã Dự Án', 'Dự Án', 'Hợp Đồng - PLHĐ', 'Hạng Mục']
    for col in cols_to_fill:
        if col in df.columns: df[col] = df[col].replace('', pd.NA).ffill()
            
    df = df.fillna('') 
    
    # Xử lý ngày tháng
    if 'Ngày Bắt Đầu' in df.columns:
        df['Ngày_Bat_Dau_Obj'] = pd.to_datetime(df['Ngày Bắt Đầu'].astype(str).str.strip(), format='%d/%m/%Y', errors='coerce')
    col_ht = 'Ngày hoàn thành' if 'Ngày hoàn thành' in df.columns else ('Ngày Hoàn Thành' if 'Ngày Hoàn Thành' in df.columns else None)
    if col_ht:
        df['Ngày_Hoan_Thanh_Obj'] = pd.to_datetime(df[col_ht].astype(str).str.strip(), format='%d/%m/%Y', errors='coerce')
        
    return df

df = load_data()


# ================= 3. SIDEBAR =================
with st.sidebar:
    st.image("logothienson.png", use_container_width=True) 
    st.markdown("### BỘ LỌC DỮ LIỆU")
    
    selected_projects = st.multiselect("🏢 DỰ ÁN", options=df.get('Dự Án', pd.Series()).unique())
    selected_hd = st.multiselect("📑 SỐ HỢP ĐỒNG", options=df.get('Hợp Đồng - PLHĐ', pd.Series()).unique())
    selected_hm = st.multiselect("📁 HẠNG MỤC", options=df.get('Hạng Mục', pd.Series()).unique())
    
    time_filter = st.selectbox("📅 KHOẢNG THỜI GIAN", ["Tất cả", "Hôm nay", "Tuần này", "Tháng này", "Năm nay"])
    
    # (Logic lọc thời gian giữ nguyên như cũ)
    today = datetime.today().date()
    start_date, end_date = None, None
    if time_filter == "Hôm nay": start_date = end_date = today
    elif time_filter == "Tuần này": start_date = today - timedelta(days=today.weekday()); end_date = start_date + timedelta(days=6)
    # ... các logic khác ...

# ================= 4. HIỂN THỊ KPI & BẢNG =================
df_display = df.copy() # (Thêm các bước lọc tại đây)

st.markdown("<h2 style='text-align: center; color: #198754; font-weight: 900;'>BÁO CÁO KẾ HOẠCH TIẾN ĐỘ</h2>", unsafe_allow_html=True)

# ... (Khối KPI như cũ) ...

# === CÁCH 1 & 2 KẾT HỢP: DẢI MÀU + DATA EDITOR ===
st.markdown("<h4 style='text-align: center; color: #198754; margin-top: 35px;'>BẢNG TỔNG HỢP CHI TIẾT CÔNG VIỆC</h4>", unsafe_allow_html=True)

# Dải màu phân cách (Điểm nhấn cho tiêu đề)
st.markdown("""
<div style="height: 5px; background: linear-gradient(to right, #C62828, #198754); border-radius: 5px; margin-bottom: 2px;"></div>
""", unsafe_allow_html=True)

# Data Editor để tiêu đề bảng rõ nét
def color_rows(row):
    status = row.get('Trạng Thái', '')
    if status == 'Đã hoàn thành': return ['background-color: #4CAF50; color: #ffffff; font-weight: bold;'] * len(row)
    if status == 'Tạm dừng': return ['background-color: #E53935; color: #ffffff; font-weight: bold;'] * len(row)
    return [''] * len(row)

styled_df = df_display.style.apply(color_rows, axis=1)

# Sử dụng data_editor thay cho dataframe để tiêu đề sắc nét hơn
st.data_editor(styled_df, use_container_width=True, hide_index=True, height=550, disabled=True)
