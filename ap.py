import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ================= 1. THIẾT LẬP GIAO DIỆN & CSS =================
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", page_icon="logothienson.png", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* Ẩn nút Deploy rườm rà */
    .stAppDeployButton { display: none !important; }
    
    /* Thiết lập khối KPI */
    .kpi-card {
        width: 100%; padding: 20px 15px; border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1); border-left: 6px solid #C62828; 
        display: flex; align-items: center; margin-bottom: 15px; min-height: 110px; 
        background-color: var(--secondary-background-color);
    }
    .kpi-icon {
        font-size: 2rem; margin-right: 15px; background-color: rgba(198, 40, 40, 0.1); 
        padding: 10px; border-radius: 50%; display: flex; align-items: center;
        justify-content: center; min-width: 55px; height: 55px;
    }
    .kpi-title { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; margin-bottom: 5px; opacity: 0.8; }
    .kpi-value { font-size: 1.6rem; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# ================= 2. ĐỌC DỮ LIỆU =================
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    df.columns = df.columns.str.strip()
    
    if 'Đầu Việc' in df.columns: df.rename(columns={'Đầu Việc': 'Hạng Mục'}, inplace=True)
    if 'Đầu Việc Shopdrawing' in df.columns: df.rename(columns={'Đầu Việc Shopdrawing': 'Hạng Mục'}, inplace=True)
    if 'Ghi chú' in df.columns: df.rename(columns={'Ghi chú': 'Vướng Mắc'}, inplace=True)
    
    for col in ['Mã Dự Án', 'Dự Án', 'Hợp Đồng - PLHĐ', 'Hạng Mục']:
        if col in df.columns: df[col] = df[col].replace('', pd.NA).ffill()
    df = df.fillna('')
    
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
    selected_ql = st.multiselect("👔 CÁN BỘ QUẢN LÝ", options=df.get('Cán Bộ Quản Lý', pd.Series()).unique() if 'Cán Bộ Quản Lý' in df.columns else [])
    selected_cb = st.multiselect("👷 CÁN BỘ TRIỂN KHAI", options=df.get('Cán Bộ Triển Khai - SĐT', df.get('Người Triển Khai', pd.Series())).unique())
    
    time_filter = st.selectbox("📅 KHOẢNG THỜI GIAN", ["Tất cả", "Hôm nay", "Tuần này", "Tháng này", "Năm nay"])

# ================= 4. HIỂN THỊ KPI =================
df_display = df.copy()

# Logic lọc (Giữ nguyên)
if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
# ... (thêm các filter khác ở đây)

st.markdown("<h2 style='text-align: center;'>BÁO CÁO KẾ HOẠCH TIẾN ĐỘ</h2>", unsafe_allow_html=True)

# KPI 2 hàng
r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1: st.markdown(f'<div class="kpi-card"><div class="kpi-icon">🏢</div><div class="kpi-details"><div class="kpi-title">Tổng Dự án</div><div class="kpi-value">{df_display.get("Dự Án", pd.Series()).nunique()}</div></div></div>', unsafe_allow_html=True)
with r1_c2: st.markdown(f'<div class="kpi-card"><div class="kpi-icon">📁</div><div class="kpi-details"><div class="kpi-title">Hạng mục</div><div class="kpi-value">{df_display.get("Hạng Mục", pd.Series()).nunique()}</div></div></div>', unsafe_allow_html=True)
with r1_c3: st.markdown(f'<div class="kpi-card"><div class="kpi-icon">📋</div><div class="kpi-details"><div class="kpi-title">CV triển khai</div><div class="kpi-value">{len(df_display)}</div></div></div>', unsafe_allow_html=True)
with r1_c4: st.markdown(f'<div class="kpi-card"><div class="kpi-icon">⏱️</div><div class="kpi-details"><div class="kpi-title">Tiến độ TB</div><div class="kpi-value">{df_display["Tiến Độ (%)"].mean():.1f}%</div></div></div>', unsafe_allow_html=True)

# ================= 5. BẢNG DỮ LIỆU & XUẤT CSV =================
st.markdown("<h4 style='text-align: center; margin-top: 20px;'>BẢNG CHI TIẾT CÔNG VIỆC</h4>", unsafe_allow_html=True)

# Nút Tải Xuống
csv = df_display.to_csv(index=False).encode('utf-8-sig')
st.download_button(label="📥 Tải xuống dữ liệu CSV", data=csv, file_name='data.csv', mime='text/csv')

# Định dạng bảng (Không dùng !important để tránh lỗi block)
def color_rows(row):
    status = row.get('Trạng Thái', '')
    if status == 'Đã hoàn thành': return ['background-color: #4CAF50; color: white;'] * len(row)
    if status == 'Tạm dừng': return ['background-color: #D32F2F; color: white;'] * len(row)
    return [''] * len(row)

styled_table = df_display.style.apply(color_rows, axis=1)

st.dataframe(styled_table, use_container_width=True, hide_index=True, height=550)
