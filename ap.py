import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Thiết lập giao diện trang web
st.set_page_config(page_title="Dashboard Shopdrawing", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a237e;'>BÁO CÁO TIẾN ĐỘ CÔNG VIỆC PTK-THIÊN SƠN</h1>", unsafe_allow_html=True)
st.write("---")

# 2. Đọc dữ liệu TRỰC TIẾP TỪ GOOGLE SHEETS
@st.cache_data(ttl=60)
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    
    # Chuẩn hóa tên cột để hiển thị ngắn gọn hơn
    if 'Đầu Việc Shopdrawing' in df.columns:
        df.rename(columns={'Đầu Việc Shopdrawing': 'Đầu Việc'}, inplace=True)
        
    # Xử lý toàn bộ các ô trống (NaN/None) thành khoảng trắng để bảng không bị lỗi chữ "None"
    df = df.fillna('') 
    return df

df = load_data()

# 3. Tạo Thẻ KPI (4 ô trên cùng)
total_tasks = len(df)
done_tasks = len(df[df['Trạng Thái'] == 'Đã hoàn thành'])
paused_tasks = len(df[df['Trạng Thái'] == 'Tạm dừng'])
avg_progress = df['Tiến Độ (%)'].mean() if 'Tiến Độ (%)' in df.columns else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric(label="TỔNG ĐẦU VIỆC BẢN VẼ", value=f"{total_tasks}")
col2.metric(label="SỐ BẢN VẼ ĐÃ XONG", value=f"{done_tasks}")
col3.metric(label="TIẾN ĐỘ TRUNG BÌNH", value=f"{avg_progress:.1f}%")
col4.metric(label="ĐANG BỊ VƯỚNG MẮC", value=f"{paused_tasks}")

st.write("---")

# 4. Tạo Biểu đồ
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.markdown("### Tỉ Lệ Trạng Thái")
    if 'Trạng Thái' in df.columns:
        status_counts = df['Trạng Thái'].value_counts().reset_index()
        status_counts.columns = ['Trạng Thái', 'Số Lượng']
        
        color_map = {
            'Đã hoàn thành': '#66bb6a', 
            'Đang triển khai': '#29b6f6', 
            'Chưa bắt đầu': '#bdbdbd', 
            'Tạm dừng': '#ef5350'
        }
        
        fig_pie = px.pie(status_counts, values='Số Lượng', names='Trạng Thái', 
                         color='Trạng Thái', color_discrete_map=color_map, hole=0.4)
        st.plotly_chart(fig_pie, use_container_width=True)

with col_chart2:
    st.markdown("### Tiến Độ Hoàn Thành Theo Dự Án (%)")
    if 'Dự Án' in df.columns and 'Tiến Độ (%)' in df.columns:
        proj_prog = df.groupby('Dự Án')['Tiến Độ (%)'].mean().reset_index().sort_values(by='Tiến Độ (%)')
        fig_bar = px.bar(proj_prog, x='Tiến Độ (%)', y='Dự Án', orientation='h', 
                         color='Tiến Độ (%)', color_continuous_scale='Viridis')
        fig_bar.update_layout(xaxis=dict(range=[0, 100]))
        st.plotly_chart(fig_bar, use_container_width=True)

st.write("---")

# 5. Bảng Dữ Liệu Tổng Hợp Đầy Đủ (Sắp xếp theo yêu cầu)
st.markdown("<h3 style='color: #1565c0;'>BẢNG THEO DÕI TỔNG HỢP CÔNG VIỆC</h3>", unsafe_allow_html=True)

df_display = df.copy()

# Định nghĩa mức độ ưu tiên theo đúng thứ tự bạn cần
priority_map = {
    'Chưa bắt đầu': 1,
    'Đang triển khai': 2,
    'Đã hoàn thành': 3,
    'Tạm dừng': 4
}

if 'Trạng Thái' in df_display.columns and 'Tiến Độ (%)' in df_display.columns:
    # Tạo một cột tạm để làm tiêu chí sắp xếp
    df_display['Mức Ưu Tiên'] = df_display['Trạng Thái'].map(priority_map)
    
    # Sắp xếp 2 cấp: 
    # Cấp 1: Theo 'Mức Ưu Tiên' (1 -> 4)
    # Cấp 2: Theo 'Tiến Độ (%)' tăng dần (từ người làm ít nhất đến người làm nhiều nhất)
    df_display = df_display.sort_values(by=['Mức Ưu Tiên', 'Tiến Độ (%)'], ascending=[True, True])
    
    # Xóa cột tạm đi để bảng hiển thị sạch sẽ
    df_display = df_display.drop(columns=['Mức Ưu Tiên'])

# Hiển thị toàn bộ dữ liệu đầy đủ thay vì chỉ hiện 4 cột như trước
st.dataframe(df_display, use_container_width=True, hide_index=True)
