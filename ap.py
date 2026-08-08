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
    
    # Đổi tên cột theo yêu cầu: Đầu Việc -> Hạng Mục
    if 'Đầu Việc' in df.columns:
        df.rename(columns={'Đầu Việc': 'Hạng Mục'}, inplace=True)
    if 'Đầu Việc Shopdrawing' in df.columns:
        df.rename(columns={'Đầu Việc Shopdrawing': 'Hạng Mục'}, inplace=True)
    if 'Ghi chú' in df.columns:
        df.rename(columns={'Ghi chú': 'Vướng Mắc'}, inplace=True)
        
    # TỰ ĐỘNG ĐIỀN THÔNG TIN BỊ TRỐNG DO GỘP Ô
    cols_to_fill = ['Mã Dự Án', 'Dự Án', 'Hợp Đồng - PLHĐ', 'Hạng Mục']
    for col in cols_to_fill:
        if col in df.columns:
            df[col] = df[col].replace('', pd.NA).ffill()
            
    # Xử lý toàn bộ các ô trống (NaN/None) thành khoảng trắng
    df = df.fillna('') 
    return df

df = load_data()

# 3. Tạo bảng màu cố định cho từng Dự án 
unique_projects = [p for p in df['Dự Án'].unique() if p != '']
color_palette = px.colors.qualitative.Pastel 
project_colors = {proj: color_palette[i % len(color_palette)] for i, proj in enumerate(unique_projects)}

# 4. Tạo Thẻ KPI
total_projects = df['Dự Án'].nunique()
total_items = len(df)
done_tasks = len(df[df['Trạng Thái'] == 'Đã hoàn thành']) 
avg_progress = df['Tiến Độ (%)'].mean() if 'Tiến Độ (%)' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TỔNG DỰ ÁN", f"{total_projects}")
col2.metric("TỔNG CÔNG VIỆC", f"{total_items}")
col3.metric("SỐ CÔNG VIỆC ĐÃ XONG", f"{done_tasks}") 
col4.metric("TIẾN ĐỘ TRUNG BÌNH", f"{avg_progress:.1f}%")

st.write("---")

# 5. Tạo Biểu đồ
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Tỉ Lệ Trạng Thái")
    if 'Trạng Thái' in df.columns:
        status_counts = df['Trạng Thái'].value_counts().reset_index()
        status_counts.columns = ['Trạng Thái', 'Số Lượng']
        
        color_map = {
            'Đã hoàn thành': '#34A853', 
            'Đang triển khai': '#4285F4', 
            'Chưa bắt đầu': '#9AA0A6', 
            'Tạm dừng': '#EA4335'
        }
        
        fig_pie = px.pie(status_counts, values='Số Lượng', names='Trạng Thái', 
                         color='Trạng Thái', color_discrete_map=color_map, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.markdown("### Tiến Độ Hoàn Thành Theo Dự Án (%)")
    if 'Dự Án' in df.columns and 'Tiến Độ (%)' in df.columns:
        proj_prog = df.groupby('Dự Án')['Tiến Độ (%)'].mean().reset_index().sort_values(by='Tiến Độ (%)')
        dynamic_height = max(400, len(unique_projects) * 40)
        
        fig_bar = px.bar(proj_prog, x='Tiến Độ (%)', y='Dự Án', orientation='h', 
                         color='Dự Án', color_discrete_map=project_colors, height=dynamic_height)
        fig_bar.update_layout(xaxis=dict(range=[0, 100]), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

st.write("---")

# 6. Bảng Dữ Liệu Tích Hợp Bộ Lọc 2 Lớp (Dự Án -> Hạng Mục)
st.markdown("<h3 style='color: #4285F4;'>BẢNG THEO DÕI TỔNG HỢP CÔNG VIỆC</h3>", unsafe_allow_html=True)

df_display = df.copy()

# Hàng bộ lọc
filter_col1, filter_col2 = st.columns(2)

with filter_col1:
    selected_projects = st.multiselect("1. Lọc theo Dự Án:", options=unique_projects)
    if selected_projects:
        df_display = df_display[df_display['Dự Án'].isin(selected_projects)]

with filter_col2:
    if 'Hạng Mục' in df_display.columns:
        # Lấy danh sách hạng mục của các dự án đang được chọn
        unique_categories = [c for c in df_display['Hạng Mục'].unique() if c != '']
        selected_categories = st.multiselect("2. Lọc chi tiết theo Hạng Mục:", options=unique_categories)
        if selected_categories:
            df_display = df_display[df_display['Hạng Mục'].isin(selected_categories)]

# Định nghĩa mức độ ưu tiên
priority_map = {
    'Chưa bắt đầu': 1,
    'Đang triển khai': 2,
    'Đã hoàn thành': 3,
    'Tạm dừng': 4
}

if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
    df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map)
    
    # Sắp xếp 3 cấp: Gom nhóm theo Hạng mục -> Mức Ưu Tiên -> Tiến Độ (%)
    sort_columns = ['Mức Ưu Tiên', 'Tiến Độ (%)']
    if 'Hạng Mục' in df_display.columns:
        sort_columns = ['Hạng Mục'] + sort_columns
        
    df_display = df_display.sort_values(by=sort_columns, ascending=[True] * len(sort_columns))
    df_display = df_display.drop(columns=['Mức Ưu Tiên'])

# Hàm tô màu dòng theo màu của dự án
def color_rows(row):
    proj = row.get('Dự Án', '')
    bg_color = project_colors.get(proj, '#ffffff')
    return [f'background-color: {bg_color}; color: #000000;'] * len(row)

# Hiển thị bảng
styled_df = df_display.style.apply(color_rows, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
