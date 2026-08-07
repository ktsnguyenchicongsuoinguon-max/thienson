import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Thiết lập giao diện trang web
st.set_page_config(page_title="Dashboard Shopdrawing", layout="wide")
st.markdown("<h1 style='text-align: center; color: #1a237e;'>GIAO DIỆN APP QUẢN LÝ TIẾN ĐỘ SHOPDRAWING</h1>", unsafe_allow_html=True)
st.write("---")

# 2. Đọc dữ liệu TRỰC TIẾP TỪ GOOGLE SHEETS
# (Sử dụng link export CSV trực tiếp từ Google Sheets của bạn)
@st.cache_data(ttl=60) # Cứ 60 giây app sẽ tự động tải lại dữ liệu mới từ Sheet
def load_data():
    sheet_url = "https://docs.google.com/spreadsheets/d/1Ps6Bq1q_asSuR3FW5FXMJ46Tr6G02HWJh3gqX3LGG0M/export?format=csv&gid=162795196"
    df = pd.read_csv(sheet_url)
    
    # Chuẩn hóa tên cột để tránh lỗi
    if 'Hạng Mục' in df.columns:
        df.rename(columns={'Hạng Mục': 'Đầu Việc'}, inplace=True)
    if 'Ghi chú' in df.columns:
        df.rename(columns={'Ghi chú': 'Vướng Mắc'}, inplace=True)
        
    df['Vướng Mắc'] = df['Vướng Mắc'].fillna('')
    return df

df = load_data()

# 3. Tạo Thẻ KPI (4 ô trên cùng)
total_tasks = len(df)
done_tasks = len(df[df['Trạng Thái'] == 'Đã hoàn thành'])
paused_tasks = len(df[df['Trạng Thái'] == 'Tạm dừng'])
avg_progress = df['Tiến Độ (%)'].mean()

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
    # Biểu đồ tròn
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
    # Biểu đồ thanh ngang
    proj_prog = df.groupby('Dự Án')['Tiến Độ (%)'].mean().reset_index().sort_values(by='Tiến Độ (%)')
    fig_bar = px.bar(proj_prog, x='Tiến Độ (%)', y='Dự Án', orientation='h', 
                     color='Tiến Độ (%)', color_continuous_scale='Viridis')
    fig_bar.update_layout(xaxis=dict(range=[0, 100]))
    st.plotly_chart(fig_bar, use_container_width=True)

st.write("---")

# 5. Bảng Cảnh Báo Vướng Mắc
st.markdown("<h3 style='color: #c62828;'>BẢNG THEO DÕI VƯỚNG MẮC - CẦN GIẢI QUYẾT GẤP</h3>", unsafe_allow_html=True)

issues_df = df[(df['Trạng Thái'] == 'Tạm dừng') | (df['Vướng Mắc'] != '')].copy()
if not issues_df.empty:
    issues_display = issues_df[['Dự Án', 'Đầu Việc', 'Người Triển Khai', 'Vướng Mắc']]
    st.dataframe(issues_display, use_container_width=True, hide_index=True)
else:
    st.success("Tuyệt vời! Hiện tại không có bản vẽ nào bị vướng mắc.")