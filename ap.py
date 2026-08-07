import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Thiết lập giao diện
st.set_page_config(page_title="Dashboard Shopdrawing", layout="wide")
st.markdown("<h1 style='text-align: center; color: #4285F4;'>BẢNG ĐIỀU KHIỂN TIẾN ĐỘ SHOPDRAWING</h1>", unsafe_allow_html=True)
st.write("---")

# 2. Đọc và làm sạch dữ liệu
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    
    # SỬA LỖI TRỐNG Ô: Tự động điền tên dự án cho các dòng bị trống bên dưới (ffill)
    if 'Dự Án' in df.columns:
        df['Dự Án'] = df['Dự Án'].replace('', pd.NA).ffill()
    if 'Mã Dự Án' in df.columns:
        df['Mã Dự Án'] = df['Mã Dự Án'].replace('', pd.NA).ffill()
        
    if 'Đầu Việc Shopdrawing' in df.columns:
        df.rename(columns={'Đầu Việc Shopdrawing': 'Đầu Việc'}, inplace=True)
    if 'Hạng Mục' in df.columns:
        df.rename(columns={'Hạng Mục': 'Đầu Việc'}, inplace=True)
        
    df = df.fillna('')
    return df

df = load_data()

# 3. Tạo bảng màu cố định cho từng Dự án (Đồng bộ Biểu đồ & Bảng)
unique_projects = [p for p in df['Dự Án'].unique() if p != '']
# Sử dụng dải màu Pastel (nhạt) để khi bôi nền chữ vẫn dễ đọc
color_palette = px.colors.qualitative.Pastel 
project_colors = {proj: color_palette[i % len(color_palette)] for i, proj in enumerate(unique_projects)}

# 4. Tạo Thẻ KPI
total_tasks = len(df)
done_tasks = len(df[df['Trạng Thái'] == 'Đã hoàn thành'])
paused_tasks = len(df[df['Trạng Thái'] == 'Tạm dừng'])
avg_progress = df['Tiến Độ (%)'].mean() if 'Tiến Độ (%)' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("TỔNG ĐẦU VIỆC", f"{total_tasks}")
col2.metric("SỐ BẢN VẼ ĐÃ XONG", f"{done_tasks}")
col3.metric("TIẾN ĐỘ TRUNG BÌNH", f"{avg_progress:.1f}%")
col4.metric("ĐANG BỊ VƯỚNG MẮC", f"{paused_tasks}")
st.write("---")

# 5. Khu vực Biểu đồ
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Tỉ Lệ Trạng Thái")
    if 'Trạng Thái' in df.columns:
        status_counts = df['Trạng Thái'].value_counts().reset_index()
        status_counts.columns = ['Trạng Thái', 'Số Lượng']
        status_color = {'Đã hoàn thành': '#34A853', 'Đang triển khai': '#4285F4', 'Chưa bắt đầu': '#9AA0A6', 'Tạm dừng': '#EA4335'}
        fig_pie = px.pie(status_counts, values='Số Lượng', names='Trạng Thái', color='Trạng Thái', color_discrete_map=status_color, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.markdown("### Tiến Độ Hoàn Thành Theo Dự Án (%)")
    if 'Dự Án' in df.columns and 'Tiến Độ (%)' in df.columns:
        proj_prog = df.groupby('Dự Án')['Tiến Độ (%)'].mean().reset_index().sort_values(by='Tiến Độ (%)')
        # Tự động thay đổi chiều cao biểu đồ nếu có quá nhiều dự án
        dynamic_height = max(400, len(unique_projects) * 40)
        
        # Gán màu theo Dự án thay vì theo dải màu gradient
        fig_bar = px.bar(proj_prog, x='Tiến Độ (%)', y='Dự Án', orientation='h', 
                         color='Dự Án', color_discrete_map=project_colors, height=dynamic_height)
        fig_bar.update_layout(xaxis=dict(range=[0, 100]), showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

st.write("---")

# 6. Khu vực Bảng Dữ liệu (Có bộ lọc và tô màu)
st.markdown("### BẢNG THEO DÕI TỔNG HỢP CÔNG VIỆC")

# BỐ CỤC KHI CÓ NHIỀU DỰ ÁN: Thêm thanh Lọc dự án
selected_projects = st.multiselect("Lọc nhanh theo Dự Án (Để trống nếu muốn xem tất cả):", options=unique_projects)

df_display = df.copy()
if selected_projects:
    df_display = df_display[df_display['Dự Án'].isin(selected_projects)]

priority_map = {'Chưa bắt đầu': 1, 'Đang triển khai': 2, 'Đã hoàn thành': 3, 'Tạm dừng': 4}

if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
    df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map)
    df_display = df_display.sort_values(by=['Mức Ưu Tiên', 'Tiến Độ (%)'], ascending=[True, True])
    df_display = df_display.drop(columns=['Mức Ưu Tiên'])

# Hàm tô màu dòng theo màu của dự án
def color_rows(row):
    proj = row['Dự Án']
    bg_color = project_colors.get(proj, '#ffffff')
    # Trả về CSS cho toàn bộ các cột trong dòng đó (chữ màu đen để nổi trên nền màu nhạt)
    return [f'background-color: {bg_color}; color: #000000;'] * len(row)

# Áp dụng màu sắc vào bảng
styled_df = df_display.style.apply(color_rows, axis=1)
st.dataframe(styled_df, use_container_width=True, hide_index=True, height=600)
