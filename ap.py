import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
df = pd.read_csv("simulated_data.csv")
# Tính Sản lượng = Giá trị * Tiến độ / 100
df['Sản Lượng'] = df['Giá Trị (VNĐ)'] * (df['Tiến Độ (%)'] / 100.0)

# Cài đặt font và style
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans'] # Tránh lỗi font tiếng Việt nếu có

fig = plt.figure(figsize=(16, 11))
fig.patch.set_facecolor('#f4f7f6')
fig.suptitle('BÁO CÁO TỔNG QUAN TIẾN ĐỘ SHOPDRAWING & THANH QUYẾT TOÁN', fontsize=22, fontweight='bold', color='#1b5e20', y=0.97)

# Top KPI row using text
ax_kpi = plt.subplot2grid((4, 3), (0, 0), colspan=3)
ax_kpi.axis('off')

# Vẽ các khối KPI
kpis = [
    ("SỐ LƯỢNG DỰ ÁN", str(df['Dự Án'].nunique()), "#e8f5e9", "#2e7d32"),
    ("TỔNG ĐẦU VIỆC", str(len(df)), "#e3f2fd", "#1565c0"),
    ("GIÁ TRỊ HỢP ĐỒNG", f"{df['Giá Trị (VNĐ)'].sum() / 1e9:.1f} Tỷ", "#fff8e1", "#f57f17"),
    ("SẢN LƯỢNG THI CÔNG", f"{df['Sản Lượng'].sum() / 1e9:.1f} Tỷ", "#fce4ec", "#c2185b"),
    ("% HOÀN THÀNH", f"{(df['Sản Lượng'].sum()/df['Giá Trị (VNĐ)'].sum()*100):.1f}%", "#e8f5e9", "#2e7d32")
]

for i, (title, val, bg_color, text_color) in enumerate(kpis):
    # Vẽ hộp
    box = plt.Rectangle((0.02 + i*0.19, 0.2), 0.18, 0.6, fill=True, facecolor=bg_color, edgecolor='gray', lw=0.5, transform=ax_kpi.transAxes)
    ax_kpi.add_patch(box)
    ax_kpi.text(0.11 + i*0.19, 0.6, title, fontsize=11, fontweight='bold', color='#555555', ha='center', transform=ax_kpi.transAxes)
    ax_kpi.text(0.11 + i*0.19, 0.35, str(val), fontsize=22, fontweight='bold', color=text_color, ha='center', transform=ax_kpi.transAxes)

# Chart 1: Status Count (Tình trạng bản vẽ)
ax1 = plt.subplot2grid((4, 3), (1, 0), rowspan=2)
status_counts = df['Trạng Thái'].value_counts()
sns.barplot(x=status_counts.values, y=status_counts.index, hue=status_counts.index, palette='Greens_r', ax=ax1, legend=False)
ax1.set_title('Tình Trạng Bản Vẽ (Số lượng)', fontweight='bold', fontsize=14)
ax1.set_xlabel('')
for i, v in enumerate(status_counts.values):
    ax1.text(v + 2, i, str(v), color='black', va='center', fontweight='bold')

# Chart 2: Top Nhân sự chậm tiến độ
ax2 = plt.subplot2grid((4, 3), (1, 1), rowspan=2, colspan=2)
emp_prog = df.groupby('Người Phụ Trách')['Tiến Độ (%)'].mean().sort_values().head(8)
sns.barplot(x=emp_prog.values, y=emp_prog.index, hue=emp_prog.index, palette='Reds_r', ax=ax2, legend=False)
ax2.set_title('Cảnh Báo: Top 8 Nhân Sự Có Tiến Độ Thấp Nhất (%)', fontweight='bold', color='#c62828', fontsize=14)
ax2.set_xlim(0, 100)
for i, v in enumerate(emp_prog.values):
    ax2.text(v + 1, i, f"{v:.1f}%", color='#c62828', va='center', fontweight='bold')

# Chart 3: Top Dự án
ax3 = plt.subplot2grid((4, 3), (3, 0), colspan=3)
proj_val = df.groupby('Dự Án')[['Giá Trị (VNĐ)', 'Sản Lượng']].sum().sort_values('Giá Trị (VNĐ)', ascending=False).head(5)
proj_val = proj_val / 1e9 # Convert to Ty VND
proj_val.columns = ['Giá Trị Hợp Đồng (Tỷ)', 'Sản Lượng Đạt Được (Tỷ)']
proj_val.plot(kind='bar', ax=ax3, color=['#81c784', '#2e7d32'])
ax3.set_title('Tiến Độ Thanh Toán & Sản Lượng 5 Dự Án Lớn Nhất', fontweight='bold', fontsize=14)
ax3.set_xticklabels(ax3.get_xticklabels(), rotation=10, ha='right')
ax3.legend(loc='upper right')

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig('dashboard_simulation.png', dpi=150, bbox_inches='tight')
print("Dashboard saved.")
