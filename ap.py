import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# ================= 1. THIẾT LẬP GIAO DIỆN & CSS TÙY CHỈNH =================
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", page_icon="logothienson.png", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    /* 1. THANH HEADER TÀNG HÌNH (TRONG SUỐT) - GIỮ LẠI ICON VÀ 3 CHẤM */
    header[data-testid="stHeader"] { 
        background: transparent !important; 
        background-color: transparent !important;
    }
    .stAppDeployButton { display: none !important; }
    
    /* ĐẨY NỘI DUNG XUỐNG DƯỚI ĐỂ KHÔNG BỊ ĐÈ */
    .block-container { padding-top: 3rem !important; padding-bottom: 2rem !important; }
    section[data-testid="stSidebar"] .block-container { padding-top: 1rem !important; }

    /* LÀM ĐẬM HEADER BẢNG - TỰ ĐỘNG THÍCH ỨNG SÁNG/TỐI */
    div[data-testid="stDataFrame"] th {
        background-color: var(--secondary-background-color) !important; 
        color: var(--text-color) !important;
        font-weight: 800 !important; font-size: 14px !important;
    }
    
    /* ================= TÙY CHỈNH KHỐI KPI - TỰ ĐỘNG THÍCH ỨNG ================= */
    .kpi-card {
        width: 100%; padding: 20px 15px; 
        border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
        border: 1px solid var(--border-color); /* Viền tự động mờ theo theme */
        border-left: 6px solid #C62828; /* Luôn giữ viền trái màu đỏ */
        display: flex; align-items: center; margin-bottom: 15px; min-height: 115px; 
        background-color: var(--secondary-background-color); /* Màu nền khối nổi bật trong Dark Mode */
    }
    .kpi-icon {
        font-size: 2.2rem; margin-right: 15px; 
        background-color: rgba(198, 40, 40, 0.15); /* Nền đỏ trong suốt thích ứng tốt cả 2 mode */
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
    .kpi-value { 
        font-size: 1.8rem; font-weight: 900; 
        color: var(--text-color);
    }
    
    /* ================= THANH TRẠNG THÁI ================= */
    div[data-testid="stRadio"] { width: 100% !important; }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        display: flex; 
        flex-direction: row; 
        justify-content: center; 
        gap: 35px; 
        margin-top: 10px; 
        margin-bottom: 25px;
        flex-wrap: wrap; 
        background-color: transparent !important; 
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {
        cursor: pointer;
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 5px !important;
    }
    /* Chữ thanh trạng thái tự đổi trắng/đen */
    div[data-testid="stRadio"] > div[role="radiogroup"] > label p {
        font-weight: 500 !important; 
        color: var(--text-color) !important; 
        margin: 0 !important; 
        font-size: 1rem !important; 
    }
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
        
    cols_to_fill = ['Mã Dự Án', 'Dự Án', 'Hợp Đồng - PLHĐ', 'Hạng Mục']
    for col in cols_to_fill:
        if col in df.columns: df[col] = df[col].replace('', pd.NA).ffill()
            
    df = df.fillna('') 
    
    if 'Ngày Bắt Đầu' in df.columns:
        df['Ngày_Bat_Dau_Obj'] = pd.to_datetime(df['Ngày Bắt Đầu'].astype(str).str.strip(), format='%d/%m/%Y', errors='coerce')
        
    col_ht = 'Ngày hoàn thành' if 'Ngày hoàn thành' in df.columns else ('Ngày Hoàn Thành' if 'Ngày Hoàn Thành' in df.columns else None)
    if col_ht:
        df['Ngày_Hoan_Thanh_Obj'] = pd.to_datetime(df[col_ht].astype(str).str.strip(), format='%d/%m/%Y', errors='coerce')
        
    return df

df = load_data()


# ================= 3. SIDEBAR BỘ LỌC =================
with st.sidebar:
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        st.image("logothienson.png", use_container_width=True) 
        
    st.markdown("<h3 style='text-align: left; margin-top: 10px; margin-bottom: 10px;'>BỘ LỌC DỮ LIỆU</h3>", unsafe_allow_html=True)
    
    unique_projects = [p for p in df.get('Dự Án', pd.Series()).unique() if p != '']
    selected_projects = st.multiselect("🏢 DỰ ÁN", options=unique_projects, placeholder="Chọn Tất cả")

    df_temp = df.copy()
    if selected_projects: df_temp = df_temp[df_temp['Dự Án'].isin(selected_projects)]

    hd_opts = [x for x in df_temp.get('Hợp Đồng - PLHĐ', pd.Series()).unique() if x != '']
    selected_hd = st.multiselect("📑 SỐ HỢP ĐỒNG", options=hd_opts, placeholder="Chọn Tất cả")
    if selected_hd: df_temp = df_temp[df_temp['Hợp Đồng - PLHĐ'].isin(selected_hd)]

    hm_opts = [x for x in df_temp.get('Hạng Mục', pd.Series()).unique() if x != '']
    selected_hm = st.multiselect("📁 HẠNG MỤC", options=hm_opts, placeholder="Chọn Tất cả")
    if selected_hm: df_temp = df_temp[df_temp['Hạng Mục'].isin(selected_hm)]

    ql_opts = [x for x in df_temp.get('Cán Bộ Quản Lý', pd.Series()).unique() if x != ''] if 'Cán Bộ Quản Lý' in df_temp.columns else []
    selected_ql = st.multiselect("👔 CÁN BỘ QUẢN LÝ", options=ql_opts, placeholder="Chọn Tất cả")

    cb_col = 'Cán Bộ Triển Khai - SĐT' if 'Cán Bộ Triển Khai - SĐT' in df_temp.columns else ('Người Triển Khai' if 'Người Triển Khai' in df_temp.columns else None)
    cb_opts = [x for x in df_temp[cb_col].unique() if x != ''] if cb_col else []
    selected_cb = st.multiselect("👷 CÁN BỘ TRIỂN KHAI", options=cb_opts, placeholder="Chọn Tất cả")

    # ================= BỘ LỌC THỜI GIAN =================
    st.markdown("<br>", unsafe_allow_html=True)
    
    time_filter = st.selectbox("📅 KHOẢNG THỜI GIAN", 
                               ["Tất cả", "Hôm nay", "Tuần này", "Tháng này", "Năm nay", "Tùy chọn khoảng ngày"])
    
    today = datetime.today().date()
    start_date, end_date = None, None
    
    if time_filter == "Hôm nay":
        start_date = end_date = today
    elif time_filter == "Tuần này":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif time_filter == "Tháng này":
        start_date = today.replace(day=1)
        if today.month == 12:
            end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
        else:
            end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
    elif time_filter == "Năm nay":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif time_filter == "Tùy chọn khoảng ngày":
        date_range = st.date_input("Chọn khoảng thời gian:", [today, today])
        if len(date_range) == 2:
            start_date, end_date = date_range
        elif len(date_range) == 1:
            start_date = end_date = date_range[0]


# ================= 4. KHỞI TẠO CÁC CONTAINER =================
header_container = st.container()
kpi_container = st.container()
status_container = st.container()
table_container = st.container()


# ================= 5. XỬ LÝ LỌC TRẠNG THÁI =================
with status_container:
    status_options = ["🌟 Tất cả", "⏳ Chưa bắt đầu", "🔄 Đang triển khai", "✅ Đã hoàn thành", "⏸️ Tạm dừng"]
    status_map = {
        "🌟 Tất cả": "Tất cả", "⏳ Chưa bắt đầu": "Chưa bắt đầu", 
        "🔄 Đang triển khai": "Đang triển khai", "✅ Đã hoàn thành": "Đã hoàn thành", "⏸️ Tạm dừng": "Tạm dừng"
    }
    
    selected_ui_status = st.radio("Bộ lọc Trạng Thái", options=status_options, horizontal=True, label_visibility="collapsed")
    actual_status = status_map[selected_ui_status]


# ================= 6. TỔNG HỢP & ÁP DỤNG MỌI BỘ LỌC =================
df_display = df.copy()

if start_date and end_date and 'Ngày_Bat_Dau_Obj' in df_display.columns and 'Ngày_Hoan_Thanh_Obj' in df_display.columns:
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)
    
    cond_start = df_display['Ngày_Bat_Dau_Obj'].between(start_ts, end_ts)
    cond_end = df_display['Ngày_Hoan_Thanh_Obj'].between(start_ts, end_ts)
    
    df_display = df_display[cond_start | cond_end]

if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
if selected_hm: df_display = df_display[df_display['Hạng Mục'].isin(selected_hm)]
if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]

if actual_status != "Tất cả": 
    df_display = df_display[df_display.get('Trạng Thái', '') == actual_status]

for col in ['Ngày_Bat_Dau_Obj', 'Ngày_Hoan_Thanh_Obj']:
    if col in df_display.columns:
        df_display = df_display.drop(columns=[col])


# ================= 7. HIỂN THỊ TIÊU ĐỀ & KPI 2 HÀNG =================
with header_container:
    st.markdown("<h2 style='text-align: center; color: #198754; font-weight: 900; margin-top: 10px; margin-bottom: 25px;'>BÁO CÁO KẾ HOẠCH TIẾN ĐỘ & QUẢN LÝ THIẾT KẾ</h2>", unsafe_allow_html=True)

with kpi_container:
    p_projects = df_display.get('Dự Án', pd.Series()).nunique()
    p_categories = df_display.get('Hạng Mục', pd.Series()).nunique()
    p_total = len(df_display)
    p_prog = df_display['Tiến Độ (%)'].mean() if ('Tiến Độ (%)' in df_display.columns and p_total > 0) else 0
    
    p_done = len(df_display[df_display.get('Trạng Thái', '') == 'Đã hoàn thành'])
    p_inprogress = len(df_display[df_display.get('Trạng Thái', '') == 'Đang triển khai'])
    p_notstarted = len(df_display[df_display.get('Trạng Thái', '') == 'Chưa bắt đầu'])
    p_paused = len(df_display[df_display.get('Trạng Thái', '') == 'Tạm dừng'])

    def render_kpi(title, value, icon):
        return f"""
        <div class="kpi-card">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-details">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
        </div>
        """

    r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
    with r1_c1: st.markdown(render_kpi("Tổng Dự án", p_projects, "🏢"), unsafe_allow_html=True)
    with r1_c2: st.markdown(render_kpi("Hạng mục", p_categories, "📁"), unsafe_allow_html=True)
    with r1_c3: st.markdown(render_kpi("Công việc triển khai", p_total, "📋"), unsafe_allow_html=True)
    with r1_c4: st.markdown(render_kpi("Tiến độ TB", f"{p_prog:.1f}%", "⏱️"), unsafe_allow_html=True)
    
    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1: st.markdown(render_kpi("Đã hoàn thành", p_done, "✅"), unsafe_allow_html=True)
    with r2_c2: st.markdown(render_kpi("Đang triển khai", p_inprogress, "🔄"), unsafe_allow_html=True)
    with r2_c3: st.markdown(render_kpi("Chưa bắt đầu", p_notstarted, "⏳"), unsafe_allow_html=True)
    with r2_c4: st.markdown(render_kpi("Vướng mắc", p_paused, "⚠️"), unsafe_allow_html=True)


# ================= 8. HIỂN THỊ BẢNG DỮ LIỆU =================
with table_container:
    st.markdown("<h4 style='text-align: center; color: #198754; margin-top: 35px; margin-bottom: 20px; font-weight: 800;'>BẢNG TỔNG HỢP CHI TIẾT CÔNG VIỆC</h4>", unsafe_allow_html=True)

    priority_map = {'Chưa bắt đầu': 1, 'Đang triển khai': 2, 'Đã hoàn thành': 3, 'Tạm dừng': 4}

    if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
        df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map).fillna(99)
        sort_cols = ['Mức Ưu Tiên', 'Tiến Độ (%)']
        if 'Hạng Mục' in df_display.columns: sort_cols = ['Hạng Mục'] + sort_cols
        df_display = df_display.sort_values(by=sort_cols, ascending=[True] * len(sort_cols))
        df_display = df_display.drop(columns=['Mức Ưu Tiên'])

    # THÊM !IMPORTANT VÀO MÀU CHỮ ĐỂ DARK MODE ĐỌC ĐƯỢC
    def color_rows(row):
        status = row.get('Trạng Thái', '')
        if status == 'Đã hoàn thành': return ['background-color: #c8e6c9 !important; color: #1b5e20 !important;'] * len(row)
        if status == 'Tạm dừng': return ['background-color: #ffcdd2 !important; color: #b71c1c !important;'] * len(row)
        if status == 'Chưa bắt đầu': return ['background-color: #e2e3e5 !important; color: #212121 !important;'] * len(row)
        return [''] * len(row) # Đang triển khai để trống (chạy theo mặc định nền đen chữ trắng của Dark Mode)

    styled_df = df_display.style.apply(color_rows, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=550)
