import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Thiết lập giao diện trang web (Dùng layout wide để tối ưu không gian)
st.set_page_config(page_title="Tiến độ PTK-Thiên Sơn", layout="wide")

# ================= ĐỌC VÀ XỬ LÝ DỮ LIỆU =================
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
            
    df = df.fillna('') 
    return df

df = load_data()

# Tạo bảng màu cố định cho từng Dự án 
unique_projects = [p for p in df.get('Dự Án', pd.Series()).unique() if p != '']
color_palette = px.colors.qualitative.Pastel 
project_colors = {proj: color_palette[i % len(color_palette)] for i, proj in enumerate(unique_projects)}

# ================= THANH BÊN (SIDEBAR) - CHỨA BỘ LỌC GÓC TRÁI =================
st.sidebar.markdown("## 🔍 BỘ LỌC DỮ LIỆU")
st.sidebar.write("Chọn các tiêu chí bên dưới để tra cứu chi tiết:")

# Lọc đa tầng trong Sidebar
selected_projects = st.sidebar.multiselect("📁 1. Chọn Dự Án:", options=unique_projects)

# Tạo dataframe tạm để lọc bậc thang (chọn dự án nào thì các bộ lọc dưới chỉ hiện danh sách của dự án đó)
df_temp = df.copy()
if selected_projects:
    df_temp = df_temp[df_temp['Dự Án'].isin(selected_projects)]

# Lấy options dựa trên df_temp
hd_opts = [x for x in df_temp.get('Hợp Đồng - PLHĐ', pd.Series()).unique() if x != '']
selected_hd = st.sidebar.multiselect("📜 2. Hợp Đồng - PLHĐ:", options=hd_opts)
if selected_hd: df_temp = df_temp[df_temp['Hợp Đồng - PLHĐ'].isin(selected_hd)]

hm_opts = [x for x in df_temp.get('Hạng Mục', pd.Series()).unique() if x != '']
selected_hm = st.sidebar.multiselect("📑 3. Hạng Mục:", options=hm_opts)

ql_opts = [x for x in df_temp.get('Cán Bộ Quản Lý', pd.Series()).unique() if x != ''] if 'Cán Bộ Quản Lý' in df_temp.columns else []
selected_ql = st.sidebar.multiselect("👔 4. Cán Bộ Quản Lý:", options=ql_opts)

cb_col = 'Cán Bộ Triển Khai - SĐT' if 'Cán Bộ Triển Khai - SĐT' in df_temp.columns else ('Người Triển Khai' if 'Người Triển Khai' in df_temp.columns else None)
cb_opts = [x for x in df_temp[cb_col].unique() if x != ''] if cb_col else []
selected_cb = st.sidebar.multiselect("👷 5. Cán Bộ Triển Khai:", options=cb_opts)


# ================= KHU VỰC CHÍNH (MAIN AREA) =================
st.markdown("<h1 style='text-align: center; color: #4285F4;'>TIẾN ĐỘ TRIỂN KHAI DỰ ÁN PTK-THIÊN SƠN</h1>", unsafe_allow_html=True)

# BỘ LỌC TRẠNG THÁI (Nằm ngang ở chính giữa màn hình để click luôn)
st.write("---")
status_options = ["Tất cả", "Chưa bắt đầu", "Đang triển khai", "Đã hoàn thành", "Tạm dừng"]
selected_status = st.radio("📌 **Click chọn nhanh Trạng Thái Công Việc:**", options=status_options, horizontal=True)

# Áp dụng TẤT CẢ các bộ lọc vào dataframe chính để tính toán
df_display = df.copy()
if selected_projects: df_display = df_display[df_display['Dự Án'].isin(selected_projects)]
if selected_hd: df_display = df_display[df_display['Hợp Đồng - PLHĐ'].isin(selected_hd)]
if selected_hm: df_display = df_display[df_display['Hạng Mục'].isin(selected_hm)]
if selected_ql: df_display = df_display[df_display['Cán Bộ Quản Lý'].isin(selected_ql)]
if selected_cb: df_display = df_display[df_display[cb_col].isin(selected_cb)]
if selected_status != "Tất cả": df_display = df_display[df_display.get('Trạng Thái', '') == selected_status]

# Biến kiểm tra xem người dùng CÓ đang dùng bộ lọc nào không
is_filtering = bool(selected_projects or selected_hd or selected_hm or selected_ql or selected_cb or selected_status != "Tất cả")

# ================= KPI ĐỘNG (Tự động thay đổi theo dữ liệu lọc) =================
p_total = len(df_display)
p_done = len(df_display[df_display.get('Trạng Thái', '') == 'Đã hoàn thành'])
p_paused = len(df_display[df_display.get('Trạng Thái', '') == 'Tạm dừng'])
p_prog = df_display['Tiến Độ (%)'].mean() if ('Tiến Độ (%)' in df_display.columns and p_total > 0) else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TỔNG CÔNG VIỆC (Đang lọc)", f"{p_total}")
col2.metric("SỐ CÔNG VIỆC ĐÃ XONG", f"{p_done}")
col3.metric("TIẾN ĐỘ TRUNG BÌNH", f"{p_prog:.1f}%")
col4.metric("ĐANG BỊ VƯỚNG MẮC", f"{p_paused}")

st.write("---")

# ================= ĐIỀU KIỆN HIỂN THỊ (BIỂU ĐỒ vs BẢNG CHI TIẾT) =================
if is_filtering:
    # KHI ĐANG LỌC: Ẩn biểu đồ, Hiện bảng thông tin chi tiết chiếm trọn màn hình
    st.markdown("<h3 style='color: #34A853;'>📊 BÁO CÁO CHI TIẾT THEO TIÊU CHÍ LỌC</h3>", unsafe_allow_html=True)
else:
    # KHI CHƯA LỌC GÌ: Hiện biểu đồ tổng quan
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
            
    st.markdown("<h3 style='color: #4285F4; margin-top: 20px;'>📋 BẢNG THEO DÕI TỔNG HỢP (TẤT CẢ)</h3>", unsafe_allow_html=True)

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
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600 if is_filtering else 400)
