import streamlit as st
import pandas as pd
import io
import base64
import os
from datetime import datetime, timedelta

# ================= 1. THIẾT LẬP GIAO DIỆN =================
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", page_icon="logothienson.png", layout="wide", initial_sidebar_state="expanded")

def get_base64_image(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return None

bg_base64 = get_base64_image("background.jpg")
bg_url = f"data:image/jpeg;base64,{bg_base64}" if bg_base64 else "https://img.freepik.com/free-photo/green-marble-texture-background_23-2150383431.jpg"

st.markdown(f"""
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@24,600,1,0" rel="stylesheet" />
<style>
    .stApp {{
        background-image: url("{bg_url}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    .block-container {{
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
        background-color: rgba(255, 255, 255, 0.35) !important;
        backdrop-filter: blur(20px) !important;
        border-radius: 24px;
        margin-top: 30px;
        margin-bottom: 30px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.15);
        border: 1px solid rgba(255, 255, 255, 0.4);
    }
    section[data-testid="stSidebar"] {{
        background-color: rgba(255, 255, 255, 0.45) !important;
        backdrop-filter: blur(20px) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.3);
    }}
    header[data-testid="stHeader"] {{ background: transparent !important; }}
    .stAppDeployButton {{ display: none !important; }}
    
    div[data-testid="stDataFrame"] th {{
        background-color: rgba(226, 232, 240, 0.9) !important;
        color: #0F172A !important;
        font-weight: 800 !important; font-size: 14px !important;
    }}
    
    .sidebar-title {{
        display: flex; align-items: center; gap: 8px;
        font-size: 14px; font-weight: 700; color: #0f172a;
        margin-bottom: 5px; margin-top: 12px; text-transform: uppercase;
    }
    .sidebar-title .material-symbols-rounded {{ font-size: 20px; color: #0A3622; }}

    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(12px) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] * {{
        color: #0f172a !important;
        font-weight: 400 !important;
    }}

    .custom-download-link {{
        display: block; float: right; text-align: right;
        color: #64748b !important; font-size: 13.5px !important; font-weight: 600 !important;
        text-decoration: none !important; margin-top: -42px !important; margin-bottom: 15px !important;
        position: relative; z-index: 9999; cursor: pointer;
    }}
    .custom-download-link:hover {{ color: #0A3622 !important; text-decoration: underline !important; }}

    .kpi-card {{
        width: 100%; padding: 20px 18px; border-radius: 24px; border: none !important;
        box-shadow: 0 20px 40px rgba(0,0,0,0.2), 0 8px 16px rgba(0,0,0,0.1);
        display: flex; align-items: center; margin-bottom: 15px; min-height: 120px;
        background-color: rgba(255, 255, 255, 0.4) !important;
        backdrop-filter: blur(15px); transition: transform 0.3s ease, box-shadow 0.3s ease;
    }}
    .kpi-card:hover {{ transform: translateY(-5px); box-shadow: 0 25px 50px rgba(0,0,0,0.25); }}
    .kpi-icon-wrapper {{
        width: 65px; height: 65px; border-radius: 20px;
        display: flex; align-items: center; justify-content: center; flex-shrink: 0; margin-right: 18px;
    }}
    .kpi-icon-wrapper .material-symbols-rounded {{ font-size: 36px; }}
    .kpi-details {{ flex-grow: 1; overflow: hidden; }}
    .kpi-title {{
        font-size: 0.85rem; font-weight: 800; opacity: 0.85;
        text-transform: uppercase; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #0f172a;
    }}
    .kpi-value {{ font-size: 1.8rem; font-weight: 900; color: #0f172a; }}

    div[data-testid="stRadio"] {{ width: 100% !important; }}
    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        display: flex; flex-direction: row; justify-content: center; gap: 35px;
        margin-top: 10px; margin-bottom: 25px; flex-wrap: wrap; background-color: transparent !important;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label {{ cursor: pointer; background: transparent !important; border: none !important; padding: 5px !important; }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label p {{ font-weight: 500 !important; color: #0f172a !important; margin: 0 !important; font-size: 1rem !important; }}
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

# ================= 3. SIDEBAR BỘ LỌC =================
with st.sidebar:
    if os.path.exists("logothienson.png"):
        st.image("logothienson.png", use_container_width=True)
    st.markdown("<h3 style='text-align: left; margin-top: 10px; margin-bottom: 10px; color: #0f172a;'>BỘ LỌC DỮ LIỆU</h3>", unsafe_allow_html=True)
    
    unique_projects = [p for p in df.get('Dự Án', pd.Series()).unique() if p != '']
    st.markdown('<div class="sidebar-title"><span class="material-symbols-rounded">domain</span> DỰ ÁN</div>', unsafe_allow_html=True)
    selected_projects = st.multiselect("DỰ ÁN", options=unique_projects, placeholder="Chọn Tất cả", label_visibility="collapsed")

    df_temp = df.copy()
    if selected_projects: df_temp = df_temp[df_temp['Dự Án'].isin(selected_projects)]

    hd_opts = [x for x in df_temp.get('Hợp Đồng - PLHĐ', pd.Series()).unique() if x != '']
    st.markdown('<div class="sidebar-title"><span class="material-symbols-rounded">description</span> SỐ HỢP ĐỒNG</div>', unsafe_allow_html=True)
    selected_hd = st.multiselect("SỐ HỢP ĐỒNG", options=hd_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")
    if selected_hd: df_temp = df_temp[df_temp['Hợp Đồng - PLHĐ'].isin(selected_hd)]

    hm_opts = [x for x in df_temp.get('Hạng Mục', pd.Series()).unique() if x != '']
    st.markdown('<div class="sidebar-title"><span class="material-symbols-rounded">folder_open</span> HẠNG MỤC</div>', unsafe_allow_html=True)
    selected_hm = st.multiselect("HẠNG MỤC", options=hm_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")
    if selected_hm: df_temp = df_temp[df_temp['Hạng Mục'].isin(selected_hm)]

    ql_opts = [x for x in df_temp.get('Cán Bộ Quản Lý', pd.Series()).unique() if x != ''] if 'Cán Bộ Quản Lý' in df_temp.columns else []
    st.markdown('<div class="sidebar-title"><span class="material-symbols-rounded">manage_accounts</span> CÁN BỘ QUẢN LÝ</div>', unsafe_allow_html=True)
    selected_ql = st.multiselect("CÁN BỘ QUẢN LÝ", options=ql_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")

    cb_col = 'Cán Bộ Triển Khai - SĐT' if 'Cán Bộ Triển Khai - SĐT' in df_temp.columns else ('Người Triển Khai' if 'Người Triển Khai' in df_temp.columns else None)
    cb_opts = [x for x in df_temp[cb_col].unique() if x != ''] if cb_col else []
    st.markdown('<div class="sidebar-title"><span class="material-symbols-rounded">engineering</span> CÁN BỘ TRIỂN KHAI</div>', unsafe_allow_html=True)
    selected_cb = st.multiselect("CÁN BỘ TRIỂN KHAI", options=cb_opts, placeholder="Chọn Tất cả", label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title"><span class="material-symbols-rounded">calendar_month</span> KHOẢNG THỜI GIAN</div>', unsafe_allow_html=True)
    time_filter = st.selectbox("KHOẢNG THỜI GIAN", ["Tất cả", "Hôm nay", "Tuần này", "Tháng này", "Năm nay", "Tùy chọn khoảng ngày"], label_visibility="collapsed")
    
    today = datetime.today().date()
    start_date, end_date = None, None
    if time_filter == "Hôm nay":
        start_date = end_date = today
    elif time_filter == "Tuần này":
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
    elif time_filter == "Tháng này":
        start_date = today.replace(day=1)
        end_date = today.replace(month=today.month+1, day=1) - timedelta(days=1) if today.month < 12 else today.replace(year=today.year+1, month=1, day=1) - timedelta(days=1)
    elif time_filter == "Năm nay":
        start_date = today.replace(month=1, day=1)
        end_date = today.replace(month=12, day=31)
    elif time_filter == "Tùy chọn khoảng ngày":
        date_range = st.date_input("Chọn khoảng thời gian:", [today, today])
        if len(date_range) == 2: start_date, end_date = date_range
        elif len(date_range) == 1: start_date = end_date = date_range[0]

# ================= 4. KHỞI TẠO CONTAINER & LỌC DỮ LIỆU =================
header_container = st.container()
kpi_container = st.container()
status_container = st.container()
table_container = st.container()

with status_container:
    actual_status = st.radio("Bộ lọc Trạng Thái", options=["Tất cả", "Chưa bắt đầu", "Đang triển khai", "Đã hoàn thành", "Tạm dừng"], horizontal=True, label_visibility="collapsed")

df_display = df.copy()
if start_date and end_date and 'Ngày_Bat_Dau_Obj' in df_display.columns and 'Ngày_Hoan_Thanh_Obj' in df_display.columns:
    df_display = df_display[df_display['Ngày_Bat_Dau_Obj'].between(pd.to_datetime(start_date), pd.to_datetime(end_date)) | df_display['Ngày_Hoan_Thanh_Obj'].between(pd.to_datetime(start_date), pd.to_datetime(end_date))]

if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
if selected_hm: df_display = df_display[df_display['Hạng Mục'].isin(selected_hm)]
if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]

if actual_status != "Tất cả": 
    df_display = df_display[df_display.get('Trạng Thái', '') == actual_status]

df_export = df_display.copy()
for col in ['Ngày_Bat_Dau_Obj', 'Ngày_Hoan_Thanh_Obj']:
    if col in df_display.columns:
        df_display = df_display.drop(columns=[col])
        if col in df_export.columns: df_export = df_export.drop(columns=[col])

# ================= 5. HIỂN THỊ GIAO DIỆN CHÍNH =================
with header_container:
    st.markdown("<h2 style='text-align: center; color: #0A3622; font-weight: 900; text-shadow: 0 2px 8px rgba(0,0,0,0.2); margin-top: 10px; margin-bottom: 25px;'>BÁO CÁO KẾ HOẠCH TIẾN ĐỘ & QUẢN LÝ THIẾT KẾ</h2>", unsafe_allow_html=True)

with kpi_container:
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

with table_container:
    st.markdown("<h4 style='text-align: center; color: #0A3622; font-weight: 900; text-shadow: 0 2px 6px rgba(0,0,0,0.15); margin-top: 35px; margin-bottom: 25px;'>BẢNG TỔNG HỢP CHI TIẾT CÔNG VIỆC</h4>", unsafe_allow_html=True)

    def generate_excel(df_data):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df_data.to_excel(writer, index=False, sheet_name='TienDo')
        output.seek(0)
        import openpyxl
        from openpyxl.styles import PatternFill
        wb = openpyxl.load_workbook(output)
        ws = wb.active
        green_fill = PatternFill(start_color="A5D6A7", end_color="A5D6A7", fill_type="solid")
        red_fill = PatternFill(start_color="EF9A9A", end_color="EF9A9A", fill_type="solid")
        gray_fill = PatternFill(start_color="F5F5F5", end_color="F5F5F5", fill_type="solid")
        
        status_col_idx = next((i for i, col in enumerate(df_data.columns, 1) if col == 'Trạng Thái'), None)
        if status_col_idx:
            for row_idx in range(2, ws.max_row + 1):
                val = str(ws.cell(row=row_idx, column=status_col_idx).value).strip()
                fill = green_fill if val == 'Đã hoàn thành' else (red_fill if val == 'Tạm dừng' else (gray_fill if val == 'Chưa bắt đầu' else None))
                if fill:
                    for col in range(1, ws.max_column + 1):
                        ws.cell(row=row_idx, column=col).fill = fill
        final_output = io.BytesIO()
        wb.save(final_output)
        return final_output.getvalue()

    try:
        excel_bytes = generate_excel(df_export)
        b64 = base64.b64encode(excel_bytes).decode()
        mime, fname = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "Bao_cao_tien_do_Thien_Son.xlsx"
    except:
        csv_bytes = df_export.to_csv(index=False).encode('utf-8-sig')
        b64 = base64.b64encode(csv_bytes).decode()
        mime, fname = "text/csv", "Bao_cao_tien_do_Thien_Son.csv"

    st.markdown(f'<a class="custom-download-link" href="data:{mime};base64,{b64}" download="{fname}">Tải Excel</a>', unsafe_allow_html=True)

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
        'selector': 'th', 'props': [('background-color', 'rgba(226, 232, 240, 0.9)'), ('color', '#0f172a'), ('font-weight', 'bold')]
    }])
    st.dataframe(styled_df, use_container_width=True, hide_index=True, height=550)
