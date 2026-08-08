import streamlit as st
import pandas as pd

# ================= 1. THIẾT LẬP GIAO DIỆN & CSS TÙY CHỈNH =================
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", layout="wide", initial_sidebar_state="expanded")

# CSS Tùy chỉnh để tạo giao diện Card KPI và Sidebar
st.markdown("""
<style>
    /* Nền trang web */
    .stApp { background-color: #f4f7f6; }
    
    /* Tùy chỉnh thẻ KPI */
    .kpi-card {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        border-left: 5px solid #198754; /* Tone Xanh Lục */
        display: flex;
        align-items: center;
        margin-bottom: 15px;
    }
    .kpi-icon {
        font-size: 2.5rem;
        margin-right: 15px;
        background-color: #e8f5e9;
        padding: 10px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .kpi-details { flex-grow: 1; }
    .kpi-title {
        color: #6c757d;
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 5px;
    }
    .kpi-value {
        font-size: 1.6rem;
        font-weight: 800;
        color: #2c3e50;
    }
</style>
""", unsafe_allow_html=True)


# ================= 2. ĐỌC VÀ XỬ LÝ DỮ LIỆU =================
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


# ================= 3. CỘT BÊN TRÁI (SIDEBAR LỌC DỮ LIỆU) =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/10313/10313098.png", width=80) # Icon Logo minh họa
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
    

# ================= 4. KHU VỰC TRUNG TÂM (MAIN BẢNG ĐIỀU KHIỂN) =================
st.markdown("<h2 style='text-align: center; color: #198754; font-weight: 800; margin-bottom: 30px;'>BÁO CÁO PHÒNG KẾ HOẠCH TIẾN ĐỘ & QUẢN LÝ THIẾT KẾ</h2>", unsafe_allow_html=True)

# Lọc Dữ Liệu Thực Tế
df_display = df.copy()
if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]

# Lọc Trạng Thái (Thanh Ngang)
status_options = ["Tất cả", "Chưa bắt đầu", "Đang triển khai", "Đã hoàn thành", "Tạm dừng"]
st.markdown("<div style='background-color: white; padding: 10px; border-radius: 8px; border: 1px solid #ddd; margin-bottom: 20px;'>", unsafe_allow_html=True)
selected_status = st.radio("TÌNH TRẠNG THI CÔNG / TRIỂN KHAI", options=status_options, horizontal=True)
st.markdown("</div>", unsafe_allow_html=True)

if selected_status != "Tất cả": df_display = df_display[df_display.get('Trạng Thái', '') == selected_status]

# Tính Toán Biến Số KPI
p_total = len(df_display)
p_projects = df_display.get('Dự Án', pd.Series()).nunique()
p_done = len(df_display[df_display.get('Trạng Thái', '') == 'Đã hoàn thành'])
p_paused = len(df_display[df_display.get('Trạng Thái', '') == 'Tạm dừng'])
p_prog = df_display['Tiến Độ (%)'].mean() if ('Tiến Độ (%)' in df_display.columns and p_total > 0) else 0

# Hàm Render HTML KPI
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

# Hiển Thị 2 Hàng KPI (4 thẻ mỗi hàng)
c1, c2, c3, c4 = st.columns(4)
with c1: st.markdown(render_kpi("Số lượng dự án", p_projects, "🏢"), unsafe_allow_html=True)
with c2: st.markdown(render_kpi("Tổng số công việc", p_total, "📋"), unsafe_allow_html=True)
with c3: st.markdown(render_kpi("Công việc hoàn thành", p_done, "✅", "#0dcaf0"), unsafe_allow_html=True)
with c4: st.markdown(render_kpi("Tiến độ trung bình", f"{p_prog:.1f}%", "⏱️", "#ffc107"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ================= 5. KHU VỰC BẢNG THEO DÕI =================
st.markdown("<h4 style='text-align: center; color: #198754; margin-bottom: 10px;'>BẢNG TỔNG HỢP TIẾN ĐỘ THI CÔNG</h4>", unsafe_allow_html=True)

priority_map = {'Chưa bắt đầu': 1, 'Đang triển khai': 2, 'Đã hoàn thành': 3, 'Tạm dừng': 4}

if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
    df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map).fillna(99)
    sort_cols = ['Mức Ưu Tiên', 'Tiến Độ (%)']
    if 'Hạng Mục' in df_display.columns: sort_cols = ['Hạng Mục'] + sort_cols
    df_display = df_display.sort_values(by=sort_cols, ascending=[True] * len(sort_cols))
    df_display = df_display.drop(columns=['Mức Ưu Tiên'])

# Bôi nền tự động
def color_rows(row):
    status = row.get('Trạng Thái', '')
    if status == 'Đã hoàn thành': return ['background-color: #e8f5e9; color: #000;'] * len(row)
    if status == 'Tạm dừng': return ['background-color: #ffebee; color: #000;'] * len(row)
    if status == 'Chưa bắt đầu': return ['background-color: #f5f5f5; color: #000;'] * len(row)
    return ['background-color: #ffffff; color: #000;'] * len(row)

styled_df = df_display.style.apply(color_rows, axis=1)

# Render bảng với độ cao lớn để fill màn hình
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=650)
