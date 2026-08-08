import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Thiết lập giao diện trang web
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4285F4;'>TIẾN ĐỘ TRIỂN KHAI DỰ ÁN PTK-THIÊN SƠN</h1>", unsafe_allow_html=True)
st.write("---")

# 2. Đọc dữ liệu TRỰC TIẾP TỪ GOOGLE SHEETS
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    
    # Đổi tên cột chuẩn hóa
    if 'Đầu Việc' in df.columns: df.rename(columns={'Đầu Việc': 'Hạng Mục'}, inplace=True)
    if 'Đầu Việc Shopdrawing' in df.columns: df.rename(columns={'Đầu Việc Shopdrawing': 'Hạng Mục'}, inplace=True)
    if 'Ghi chú' in df.columns: df.rename(columns={'Ghi chú': 'Vướng Mắc'}, inplace=True)
        
    # TỰ ĐỘNG ĐIỀN THÔNG TIN BỊ TRỐNG DO GỘP Ô CHO TẤT CẢ CÁC CỘT CHÍNH
    cols_to_fill = ['Mã Dự Án', 'Dự Án', 'Hợp Đồng - PLHĐ', 'Hạng Mục']
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].replace('', pd.NA).ffill()
            
    # Xử lý toàn bộ các ô trống thành khoảng trắng
    df = df.fillna('') 
    return df

df = load_data()

# 3. Tạo bảng màu cố định cho từng Dự án 
unique_projects = [p for p in df.get('Dự Án', pd.Series()).unique() if p != '']
color_palette = px.colors.qualitative.Pastel 
project_colors = {proj: color_palette[i % len(color_palette)] for i, proj in enumerate(unique_projects)}

# ================= KHOANG KPI & BIỂU ĐỒ TỔNG =================
total_projects = df.get('Dự Án', pd.Series()).nunique()
total_items = len(df)
done_tasks = len(df[df.get('Trạng Thái', '') == 'Đã hoàn thành']) 
avg_progress = df['Tiến Độ (%)'].mean() if 'Tiến Độ (%)' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TỔNG DỰ ÁN", f"{total_projects}")
col2.metric("TỔNG CÔNG VIỆC", f"{total_items}")
col3.metric("SỐ CÔNG VIỆC ĐÃ XONG", f"{done_tasks}") 
col4.metric("TIẾN ĐỘ TRUNG BÌNH", f"{avg_progress:.1f}%")
st.write("---")

col_chart1, col_chart2 = st.columns(2)
with col_chart1:
    st.markdown("### Tỉ Lệ Trạng Thái Tổng")
    if 'Trạng Thái' in df.columns:
        status_counts = df['Trạng Thái'].value_counts().reset_index()
        status_counts.columns = ['Trạng Thái', 'Số Lượng']
        color_map = {'Đã hoàn thành': '#34A853', 'Đang triển khai': '#4285F4', 'Chưa bắt đầu': '#9AA0A6', 'Tạm dừng': '#EA4335'}
        fig_pie = px.pie(status_counts, values='Số Lượng', names='Trạng Thái', color='Trạng Thái', color_discrete_map=color_map, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.markdown("### Tiến Độ Theo Dự Án (%)")
    if 'Dự Án' in df.columns and 'Tiến Độ (%)' in df.columns:
        proj_prog = df.groupby('Dự Án')['Tiến Độ (%)'].mean().reset_index().sort_values(by='Tiến Độ (%)')
        dynamic_height = max(400, len(unique_projects) * 40)
        fig_bar = px.bar(proj_prog, x='Tiến Độ (%)', y='Dự Án', orientation='h', color='Dự Án', color_discrete_map=project_colors, height=dynamic_height)
        fig_bar.update_layout(xaxis=dict(range=[0, 100]), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

st.write("---")


# ================= BỘ LỌC ĐA LỚP & BẢNG DỮ LIỆU =================
st.markdown("<h3 style='color: #4285F4;'>BẢNG THEO DÕI & QUẢN LÝ CÔNG VIỆC CHI TIẾT</h3>", unsafe_allow_html=True)

df_display = df.copy()

# Hộp chứa 6 bộ lọc
with st.expander("🔍 MỞ BỘ LỌC TÌM KIẾM CHI TIẾT (Click để mở/đóng)", expanded=True):
    f_col1, f_col2, f_col3 = st.columns(3)
    f_col4, f_col5, f_col6 = st.columns(3)
    
    # Lớp 1: Dự án
    with f_col1:
        selected_projects = st.multiselect("1. Chọn Dự Án:", options=unique_projects)
        if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
            
    # Lớp 2: Hợp đồng
    with f_col2:
        hd_opts = [x for x in df_display.get('Hợp Đồng - PLHĐ', pd.Series()).unique() if x != '']
        selected_hd = st.multiselect("2. Hợp Đồng - PLHĐ:", options=hd_opts)
        if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
            
    # Lớp 3: Hạng mục
    with f_col3:
        hm_opts = [x for x in df_display.get('Hạng Mục', pd.Series()).unique() if x != '']
        selected_hm = st.multiselect("3. Hạng Mục:", options=hm_opts)
        if selected_hm: df_display = df_display[df_display['Hạng Mục'].isin(selected_hm)]
            
    # Lớp 4: Cán bộ triển khai
    with f_col4:
        # Tự nhận diện tên cột cán bộ
        cb_col = 'Cán Bộ Triển Khai - SĐT' if 'Cán Bộ Triển Khai - SĐT' in df_display.columns else ('Người Triển Khai' if 'Người Triển Khai' in df_display.columns else None)
        if cb_col:
            cb_opts = [x for x in df_display[cb_col].unique() if x != '']
            selected_cb = st.multiselect("4. Cán Bộ Triển Khai:", options=cb_opts)
            if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]
            
    # Lớp 5: Cán bộ quản lý
    with f_col5:
        if 'Cán Bộ Quản Lý' in df_display.columns:
            ql_opts = [x for x in df_display['Cán Bộ Quản Lý'].unique() if x != '']
            selected_ql = st.multiselect("5. Cán Bộ Quản Lý:", options=ql_opts)
            if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
            
    # Lớp 6: Trạng thái
    with f_col6:
        if 'Trạng Thái' in df_display.columns:
            tt_opts = [x for x in df_display['Trạng Thái'].unique() if x != '']
            selected_status = st.multiselect("6. Trạng Thái:", options=tt_opts)
            if selected_status: df_display = df_display[df_display['Trạng Thái'].isin(selected_status)]


# ================= BÁO CÁO NHANH MỞ RỘNG (Chỉ hiện khi chọn 1 dự án) =================
if selected_projects and len(selected_projects) == 1:
    proj_name = selected_projects[0]
    st.markdown(f"<h3 style='color: #34A853; margin-top: 20px;'>📊 BÁO CÁO NHANH DỰ ÁN: {proj_name.upper()}</h3>", unsafe_allow_html=True)
    
    p_total = len(df_display)
    p_done = len(df_display[df_display.get('Trạng Thái', '') == 'Đã hoàn thành'])
    p_paused = len(df_display[df_display.get('Trạng Thái', '') == 'Tạm dừng'])
    p_prog = df_display['Tiến Độ (%)'].mean() if 'Tiến Độ (%)' in df_display.columns else 0
    
    pc1, pc2, pc3, pc4 = st.columns(4)
    pc1.info(f"**Tổng công việc:**\n### {p_total}")
    pc2.success(f"**Đã hoàn thành:**\n### {p_done}")
    pc3.warning(f"**Tiến độ Trung bình:**\n### {p_prog:.1f}%")
    pc4.error(f"**Vướng mắc / Tạm dừng:**\n### {p_paused}")
    st.write("---")


# ================= HIỂN THỊ BẢNG DỮ LIỆU CUỐI CÙNG =================
priority_map = {'Chưa bắt đầu': 1, 'Đang triển khai': 2, 'Đã hoàn thành': 3, 'Tạm dừng': 4}

if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
    df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map).fillna(99)
    sort_cols = ['Mức Ưu Tiên', 'Tiến Độ (%)']
    if 'Hạng Mục' in df_display.columns: sort_cols = ['Hạng Mục'] + sort_cols
    df_display = df_display.sort_values(by=sort_cols, ascending=[True] * len(sort_cols))
    df_display = df_display.drop(columns=['Mức Ưu Tiên'])

def color_rows(row):
    proj = row.get('Dự Án', '')
    bg_color = project_colors.get(proj, '#ffffff')
    return [f'background-color: {bg_color}; color: #000000;'] * len(row)

styled_df = df_display.style.apply(color_rows, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
