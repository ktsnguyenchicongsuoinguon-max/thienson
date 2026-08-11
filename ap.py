import streamlit as st
import pandas as pd

# ================= 1. THIẾT LẬP GIAO DIỆN & CSS TÙY CHỈNH =================
# Đã cập nhật page_icon thành logothienson.png
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", page_icon="logothienson.png", layout="wide", initial_sidebar_state="expanded")

# CSS ÉP DÀN ĐỀU VÀ TẠO Ô TRẠNG THÁI + 6 THẺ KPI
st.markdown("""
<style>
    .stApp { background-color: #f4f7f6; }
    
    /* Thẻ KPI */
    .kpi-card {
        background-color: #ffffff;
        padding: 12px 10px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        border-left: 5px solid #198754; 
        display: flex;
        align-items: center;
        margin-bottom: 15px;
        min-height: 85px;
    }
    .kpi-icon {
        font-size: 1.8rem;
        margin-right: 10px;
        background-color: #e8f5e9;
        padding: 8px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        min-width: 50px;
        height: 50px;
    }
    .kpi-details { flex-grow: 1; overflow: hidden; }
    .kpi-title {
        color: #6c757d;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 3px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .kpi-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #2c3e50;
    }
    
    /* ÉP THANH TRẠNG THÁI DÀN ĐỀU 100% CHIỀU RỘNG */
    div[data-testid="stRadio"] {
        width: 100% !important;
    }
    div.row-widget.stRadio > div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        width: 100% !important;
        justify-content: space-between;
        gap: 15px;
        background-color: transparent;
        padding: 0px;
        margin-top: 15px;
        margin-bottom: 25px;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label {
        flex: 1 1 0px !important; 
        background-color: #ffffff;
        padding: 15px 5px !important;
        border-radius: 12px !important; 
        border: 1px solid #ced4da;
        box-shadow: 0 4px 6px rgba(0,0,0,0.04);
        cursor: pointer;
        transition: all 0.2s ease-in-out;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label:hover {
        background-color: #e8f5e9;
        border-color: #198754;
        box-shadow: 0 8px 15px rgba(25, 135, 84, 0.15);
        transform: translateY(-3px);
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label > div:first-child {
        display: none;
    }
    div.row-widget.stRadio > div[role="radiogroup"] > label div[data-testid="stMarkdownContainer"] p {
        font-weight: 700 !important;
        color: #495057;
        margin: 0;
        font-size: 1.1rem;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)


# ================= 2. ĐỌC DỮ LIỆU =================
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    
    if 'Đầu Việc' in df.columns: df.rename(columns={'Đầu Việc': 'Hạng Mục'}, inplace=True)
    if 'Đầu Việc Shopdrawing' in df.columns: df.rename(columns={'Đầu Việc Shopdrawing': 'Hạng Mục'}, inplace=True)
    if 'Ghi chú' in df.columns: df.rename(columns={'Ghi chú': 'Vướng Mắc'}, inplace=True)
        
    cols_to_fill = ['Mã Dự Án', 'Dự Án', 'Hợp Đồng - PLHĐ', 'Hạng Mục']
    for col in cols_to_fill:
        if col in df.columns: df[col] = df[col].replace('', pd.NA).ffill()
            
    df = df.fillna('') 
    return df

df = load_data()


# ================= 3. SIDEBAR BỘ LỌC =================
with st.sidebar:
    # Đã cập nhật ảnh hiển thị thành logothienson.png
    st.image("logothienson.png", width=120) 
    st.markdown("### BỘ LỌC DỮ LIỆU")
    
    unique_projects = [p for p in df.get('Dự Án', pd.Series()).unique() if p != '']
    selected_projects = st.multiselect("🏢 DỰ ÁN", options=unique_projects, placeholder="Chọn Tất cả")

    df_temp = df.copy()
    if selected_projects: df_temp = df_temp[df_temp['Dự Án'].isin(selected_projects)]

    hd_opts = [x for x in df_temp.get('Hợp Đồng - PLHĐ', pd.Series()).unique() if x != '']
    selected_hd = st.multiselect("📑 SỐ HỢP ĐỒNG", options=hd_opts, placeholder="Chọn Tất cả")
    if selected_hd: df_temp = df_temp[df_temp['Hợp Đồng - PLHĐ'].isin(selected_hd)]

    ql_opts = [x for x in df_temp.get('Cán Bộ Quản Lý', pd.Series()).unique() if x != ''] if 'Cán Bộ Quản Lý' in df_temp.columns else []
    selected_ql = st.multiselect("👔 CÁN BỘ QUẢN LÝ", options=ql_opts, placeholder="Chọn Tất cả")

    cb_col = 'Cán Bộ Triển Khai - SĐT' if 'Cán Bộ Triển Khai - SĐT' in df_temp.columns else ('Người Triển Khai' if 'Người Triển Khai' in df_temp.columns else None)
    cb_opts = [x for x in df_temp[cb_col].unique() if x != ''] if cb_col else []
    selected_cb = st.multiselect("👷 CÁN BỘ TRIỂN KHAI", options=cb_opts, placeholder="Chọn Tất cả")


# ================= 4. KHỞI TẠO CÁC CONTAINER ĐỂ SẮP XẾP BỐ CỤC =================
header_container = st.container()
kpi_container = st.container()
status_container = st.container()
table_container = st.container()


# ================= 5. XỬ LÝ LỌC TRẠNG THÁI (Trong Status Container) =================
with status_container:
    status_options = ["🌟 Tất cả", "⏳ Chưa bắt đầu", "🔄 Đang triển khai", "✅ Đã hoàn thành", "⏸️ Tạm dừng"]
    status_map = {
        "🌟 Tất cả": "Tất cả", "⏳ Chưa bắt đầu": "Chưa bắt đầu", 
        "🔄 Đang triển khai": "Đang triển khai", "✅ Đã hoàn thành": "Đã hoàn thành", "⏸️ Tạm dừng": "Tạm dừng"
    }
    
    selected_ui_status = st.radio("Bộ lọc Trạng Thái", options=status_options, horizontal=True, label_visibility="collapsed")
    actual_status = status_map[selected_ui_status]


# ================= 6. TỔNG HỢP DỮ LIỆU CUỐI CÙNG (Tính toán Động) =================
df_display = df.copy()

# Lọc theo Sidebar
if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]

# Lọc theo thanh Trạng Thái
if actual_status != "Tất cả": 
    df_display = df_display[df_display.get('Trạng Thái', '') == actual_status]


# ================= 7. HIỂN THỊ TIÊU ĐỀ & 6 THẺ KPI ĐỘNG =================
with header_container:
    st.markdown("<h2 style='text-align: center; color: #198754; font-weight: 800; margin-bottom: 20px;'>BÁO CÁO PHÒNG KẾ HOẠCH TIẾN ĐỘ & QUẢN LÝ THIẾT KẾ</h2>", unsafe_allow_html=True)

with kpi_container:
    # Tính toán thông minh dựa trên Dữ liệu Hiện tại (df_display)
    p_total = len(df_display)
    p_projects = df_display.get('Dự Án', pd.Series()).nunique()
    p_done = len(df_display[df_display.get('Trạng Thái', '') == 'Đã hoàn thành'])
    p_inprogress = len(df_display[df_display.get('Trạng Thái', '') == 'Đang triển khai'])
    p_paused = len(df_display[df_display.get('Trạng Thái', '') == 'Tạm dừng'])
    p_prog = df_display['Tiến Độ (%)'].mean() if ('Tiến Độ (%)' in df_display.columns and p_total > 0) else 0

    def render_kpi(title, value, icon, border_color="#198754"):
        return f"""
        <div class="kpi-card" style="border-left-color: {border_color};">
            <div class="kpi-icon">{icon}</div>
            <div class="kpi-details">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
        </div>
        """

    # 6 thẻ KPI
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    with c1: st.markdown(render_kpi("Dự án", p_projects, "🏢"), unsafe_allow_html=True)
    with c2: st.markdown(render_kpi("Tổng việc", p_total, "📋"), unsafe_allow_html=True)
    with c3: st.markdown(render_kpi("Đã xong", p_done, "✅", "#0dcaf0"), unsafe_allow_html=True)
    with c4: st.markdown(render_kpi("Đang làm", p_inprogress, "🔄", "#0d6efd"), unsafe_allow_html=True)
    with c5: st.markdown(render_kpi("Vướng mắc", p_paused, "⚠️", "#dc3545"), unsafe_allow_html=True)
    with c6: st.markdown(render_kpi("Tiến độ TB", f"{p_prog:.1f}%", "⏱️", "#ffc107"), unsafe_allow_html=True)


# ================= 8. HIỂN THỊ BẢNG DỮ LIỆU (Trong Table Container) =================
with table_container:
    st.markdown("<h4 style='text-align: center; color: #198754; margin-top: 5px; margin-bottom: 15px;'>BẢNG TỔNG HỢP CHI TIẾT CÔNG VIỆC</h4>", unsafe_allow_html=True)

    priority_map = {'Chưa bắt đầu': 1, 'Đang triển khai': 2, 'Đã hoàn thành': 3, 'Tạm dừng': 4}

    if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
        df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map).fillna(99)
        sort_cols = ['Mức Ưu Tiên', 'Tiến Độ (%)']
        if 'Hạng Mục' in df_display.columns: sort_cols = ['Hạng Mục'] + sort_cols
        df_display = df_display.sort_values(by=sort_cols, ascending=[True] * len(sort_cols))
        df_display = df_display.drop(columns=['Mức Ưu Tiên'])

    def color_rows(row):
        status = row.get('Trạng Thái', '')
        if status == 'Đã hoàn thành': return ['background-color: #e8f5e9; color: #000;'] * len(row)
        if status == 'Tạm dừng': return ['background-color: #ffebee; color: #000;'] * len(row)
        if status == 'Chưa bắt đầu': return ['background-color: #f5f5f5; color: #000;'] * len(row)
        return ['background-color: #ffffff; color: #000;'] * len(row)

    styled_df = df_display.style.apply(color_rows, axis=1)

    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
