import streamlit as st
import pandas as pd
import io
import base64
import os
from datetime import datetime, timedelta

# ================= 1. THIẾT LẬP GIAO DIỆN =================
st.set_page_config(
    page_title="Tiến độ PTK-Thiên Sơn", 
    page_icon="logothienson.png", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# ================= HÀM ĐỌC ẢNH LOCAL LÀM BACKGROUND =================
def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    return None

background_image_path = "background.jpg" 
bg_base64 = get_base64_image(background_image_path)

if bg_base64:
    bg_css = f"""
    <style>
        .stApp::before {{
            content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/jpeg;base64,{bg_base64}");
            background-size: cover; background-position: center; background-repeat: no-repeat;
            z-index: -99999;
        }}
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] {{ background: transparent !important; }}
    </style>
    """
    st.markdown(bg_css, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp::before { 
            content: ""; position: fixed; top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("https://img.freepik.com/free-photo/green-marble-texture-background_23-2150383431.jpg"); 
            background-size: cover; background-position: center; background-repeat: no-repeat;
            z-index: -99999;
        }
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"] { background: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# ================= CSS TÙY CHỈNH GỌN GÀNG =================
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,600,1,0" rel="stylesheet" />
<style>
    header[data-testid="stHeader"] { background: transparent !important; }
    
    .title-card {
        border-radius: 16px; 
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); 
        background-color: rgba(255, 255, 255, 0.3) !important; 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.4);
        width: fit-content; max-width: 100%;
        margin: 0 auto 20px auto; 
        display: flex; align-items: center; justify-content: center;
        padding: 10px 30px;
    }

    .kpi-card {
        width: 100%; padding: 18px; 
        border-radius: 20px; 
        border: 1px solid rgba(255, 255, 255, 0.4); 
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1); 
        display: flex; align-items: center; margin-bottom: 15px; min-height: 110px; 
        background-color: rgba(255, 255, 255, 0.35) !important; 
        backdrop-filter: blur(15px); -webkit-backdrop-filter: blur(15px);
    }
    
    .kpi-icon-wrapper {
        width: 55px; height: 55px; border-radius: 16px; 
        display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 15px;
    }
    .kpi-icon-wrapper .material-symbols-rounded { font-size: 30px; }
    .kpi-details { flex-grow: 1; overflow: hidden; }
    .kpi-title {
        font-size: 0.8rem; font-weight: 700; opacity: 0.85; text-transform: uppercase; margin-bottom: 4px; color: #0f172a;
    }
    .kpi-value { font-size: 1.6rem; font-weight: 800; color: #0f172a; }

    .custom-download-link {
        display: block; float: right; text-align: right;
        color: #0A3622 !important; font-size: 13px !important; font-weight: 700 !important;
        text-decoration: none !important; margin-bottom: 10px;
    }
    .custom-download-link:hover { text-decoration: underline !important; }
</style>
""", unsafe_allow_html=True)


# ================= 2. ĐỌC DỮ LIỆU GOOGLE SHEETS =================
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1dOiPWgLE8o7YUeA6l_g_eF825PnkskRn/export?format=csv&gid=418096547"
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


# ================= 3. BỘ LỌC (SIDEBAR) =================
with st.sidebar:
    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        st.image("logothienson.png", use_container_width=True) 
        
    st.markdown("<h3 style='color: #0f172a; font-size: 14px; margin-top: 5px;'>BỘ LỌC DỮ LIỆU</h3>", unsafe_allow_html=True)
    
    unique_projects = [p for p in df.get('Dự Án', pd.Series()).unique() if p != '']
    st.markdown("**DỰ ÁN**")
    selected_projects = st.multiselect("DỰ ÁN", options=unique_projects, placeholder="Chọn Tất cả", label_visibility="collapsed")

    df_temp = df.copy()
    if selected_projects: df_temp = df_temp[df_temp['Dự Án'].isin(selected_projects)]

    hd_opts = [x for x in df_temp.get('Hợp Đồng - PLHĐ', pd.Series()).unique() if x != '']
    st.markdown("**SỐ HỢP ĐỒNG**")
    selected_hd = st.multiselect("SỐ HỢP ĐỒNG", options=hd_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")
    if selected_hd: df_temp = df_temp[df_temp['Hợp Đồng - PLHĐ'].isin(selected_hd)]

    hm_opts = [x for x in df_temp.get('Hạng Mục', pd.Series()).unique() if x != '']
    st.markdown("**HẠNG MỤC**")
    selected_hm = st.multiselect("HẠNG MỤC", options=hm_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")
    if selected_hm: df_temp = df_temp[df_temp['Hạng Mục'].isin(selected_hm)]

    ql_opts = [x for x in df_temp.get('Cán Bộ Quản Lý', pd.Series()).unique() if x != ''] if 'Cán Bộ Quản Lý' in df_temp.columns else []
    st.markdown("**CÁN BỘ QUẢN LÝ**")
    selected_ql = st.multiselect("CÁN BỘ QUẢN LÝ", options=ql_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")

    cb_col = 'Cán Bộ Triển Khai - SĐT' if 'Cán Bộ Triển Khai - SĐT' in df_temp.columns else ('Người Triển Khai' if 'Người Triển Khai' in df_temp.columns else None)
    cb_opts = [x for x in df_temp[cb_col].unique() if x != ''] if cb_col else []
    st.markdown("**CÁN BỘ TRIỂN KHAI**")
    selected_cb = st.multiselect("CÁN BỘ TRIỂN KHAI", options=cb_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")

    st.markdown("**KHOẢNG THỜI GIAN**")
    time_filter = st.selectbox("KHOẢNG THỜI GIAN", 
                               ["Tất cả", "Hôm nay", "Tuần này", "Tháng này", "Năm nay", "Tùy chọn khoảng ngày"],
                               label_visibility="collapsed")
    
    today = datetime.today().date()
    start_date, end_date = None, None
    if time_filter == "Hôm nay":
        start_date = end_date = today
    elif time_filter == "Tuần này":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif time_filter == "Tháng này":
        start_date = today.replace(day=1)
        if today.month == 12: end_date = today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
        else: end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1)
    elif time_filter == "Năm nay":
        start_date = today.replace(month=1, day=1); end_date = today.replace(month=12, day=31)
    elif time_filter == "Tùy chọn khoảng ngày":
        date_range = st.date_input("Chọn khoảng thời gian:", [today, today])
        if len(date_range) == 2: start_date, end_date = date_range
        elif len(date_range) == 1: start_date = end_date = date_range[0]


# ================= 4. KHỐI CHÍNH =================
st.markdown("""
<div class="title-card">
    <div style="font-size: 26px; font-weight: 600; color: #0A3622;">BÁO CÁO KẾ HOẠCH TIẾN ĐỘ & QUẢN LÝ THIẾT KẾ</div>
</div>
""", unsafe_allow_html=True)

df_display = df.copy()
if start_date and end_date and 'Ngày_Bat_Dau_Obj' in df_display.columns and 'Ngày_Hoan_Thanh_Obj' in df_display.columns:
    start_ts = pd.to_datetime(start_date)
    end_ts = pd.to_datetime(end_date)
    df_display = df_display[df_display['Ngày_Bat_Dau_Obj'].between(start_ts, end_ts) | df_display['Ngày_Hoan_Thanh_Obj'].between(start_ts, end_ts)]

if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
if selected_hm: df_display = df_display[df_display['Hạng Mục'].isin(selected_hm)]
if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]

p_projects = df_display.get('Dự Án', pd.Series()).nunique()
p_categories = df_display.get('Hạng Mục', pd.Series()).nunique()
p_total = len(df_display)
p_prog = df_display['Tiến Độ (%)'].mean() if ('Tiến Độ (%)' in df_display.columns and p_total > 0) else 0

p_done = len(df_display[df_display.get('Trạng Thái', '') == 'Đã hoàn thành'])
p_inprogress = len(df_display[df_display.get('Trạng Thái', '') == 'Đang triển khai'])
p_notstarted = len(df_display[df_display.get('Trạng Thái', '') == 'Chưa bắt đầu'])
p_paused = len(df_display[df_display.get('Trạng Thái', '') == 'Tạm dừng'])

def render_kpi(title, value, icon_name, bg_color, icon_color):
    return f"""
    <div class="kpi-card">
        <div class="kpi-icon-wrapper" style="background-color: {bg_color}; color: {icon_color};">
            <span class="material-symbols-rounded">{icon_name}</span>
        </div>
        <div class="kpi-details">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
    </div>
    """

r1_c1, r1_c2, r1_c3, r1_c4 = st.columns(4)
with r1_c1: st.markdown(render_kpi("Tổng Dự án", p_projects, "domain", "#cfe2ff", "#0d6efd"), unsafe_allow_html=True)
with r1_c2: st.markdown(render_kpi("Hạng mục", p_categories, "folder_open", "#cfe2ff", "#0d6efd"), unsafe_allow_html=True)
with r1_c3: st.markdown(render_kpi("Công việc", p_total, "assignment", "#cfe2ff", "#0d6efd"), unsafe_allow_html=True)
with r1_c4: st.markdown(render_kpi("Tiến độ TB", f"{p_prog:.1f}%", "speed", "#e0cffc", "#6f42c1"), unsafe_allow_html=True)

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1: st.markdown(render_kpi("Đã hoàn thành", p_done, "check_circle", "#d1e7dd", "#198754"), unsafe_allow_html=True)
with r2_c2: st.markdown(render_kpi("Đang triển khai", p_inprogress, "sync", "#cff4fc", "#0dcaf0"), unsafe_allow_html=True)
with r2_c3: st.markdown(render_kpi("Chưa bắt đầu", p_notstarted, "hourglass_empty", "#e2e3e5", "#6c757d"), unsafe_allow_html=True)
with r2_c4: st.markdown(render_kpi("Vướng mắc", p_paused, "error", "#f8d7da", "#dc3545"), unsafe_allow_html=True)

status_options = ["Tất cả", "Chưa bắt đầu", "Đang triển khai", "Đã hoàn thành", "Tạm dừng"]
actual_status = st.radio("Bộ lọc Trạng Thái", options=status_options, horizontal=True, label_visibility="collapsed")

if actual_status != "Tất cả": 
    df_display = df_display[df_display.get('Trạng Thái', '') == actual_status]

df_export = df_display.copy()
for col in ['Ngày_Bat_Dau_Obj', 'Ngày_Hoan_Thanh_Obj']:
    if col in df_display.columns: df_display = df_display.drop(columns=[col])
    if col in df_export.columns: df_export = df_export.drop(columns=[col])

st.markdown("""
<div class="title-card" style="padding: 6px 20px; margin-top: 15px; margin-bottom: 15px;">
    <div style="font-size: 18px; font-weight: 600; color: #0A3622;">BẢNG TỔNG HỢP CHI TIẾT CÔNG VIỆC</div>
</div>
""", unsafe_allow_html=True)

try:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_export.to_excel(writer, index=False, sheet_name='TienDo')
    excel_bytes = output.getvalue()
    b64 = base64.b64encode(excel_bytes).decode()
    mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    filename = "Bao_cao_tien_do_Thien_Son.xlsx"
except Exception:
    csv_bytes = df_export.to_csv(index=False).encode('utf-8-sig')
    b64 = base64.b64encode(csv_bytes).decode()
    mime_type = "text/csv"
    filename = "Bao_cao_tien_do_Thien_Son.csv"

st.markdown(f'<a class="custom-download-link" href="data:{mime_type};base64,{b64}" download="{filename}">Tải Excel</a>', unsafe_allow_html=True)

priority_map = {'Chưa bắt đầu': 1, 'Đang triển khai': 2, 'Đã hoàn thành': 3, 'Tạm dừng': 4}
if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
    df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map).fillna(99)
    sort_cols = ['Mức Ưu Tiên', 'Tiến Độ (%)']
    if 'Hạng Mục' in df_display.columns: sort_cols = ['Hạng Mục'] + sort_cols
    df_display = df_display.sort_values(by=sort_cols, ascending=[True] * len(sort_cols))
    df_display = df_display.drop(columns=['Mức Ưu Tiên'])

def color_rows(row):
    status = row.get('Trạng Thái', '')
    if status == 'Đã hoàn thành': return ['background-color: #a5d6a7; color: #000;'] * len(row)
    if status == 'Tạm dừng': return ['background-color: #ef9a9a; color: #000;'] * len(row)
    if status == 'Chưa bắt đầu': return ['background-color: #f5f5f5; color: #000;'] * len(row)
    return ['background-color: #ffffff; color: #000;'] * len(row)

styled_df = df_display.style.apply(color_rows, axis=1).set_table_styles([{
    'selector': 'th',
    'props': [('background-color', 'rgba(226, 232, 240, 0.9)'), ('color', '#0F172A'), ('font-weight', 'bold')]
}])

st.dataframe(styled_df, use_container_width=True, hide_index=True, height=450)
