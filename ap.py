# --- CẬP NHẬT KIỂU DÁNG CĂN GIỮA VÀ THU NHỎ CỘT ---
table_styles = [
    {
        "selector": "th",
        "props": [
            ("background-color", "#e9d8fd"),
            ("color", "#000000"),
            ("font-weight", "800"),
            ("font-size", "14.5px"),
            ("text-transform", "uppercase"),
            ("text-align", "center"),     # Căn giữa ngang cho tiêu đề
            ("vertical-align", "middle"), # Căn giữa dọc cho tiêu đề
        ],
    }
]

# Nhóm 1: Thu nhỏ hẳn (1/2) cho các cột Chủ đầu tư, Hợp đồng
target_shrink_keywords = ["chủ đầu tư", "hợp đồng", "hđ", "plhđ", "cdt", "cđt"]

# Nhóm 2: Thu nhỏ vừa đủ để ÉP CÁC CỘT DÀI RỚT XUỐNG 2 DÒNG
target_wrap_keywords = ["chuyên viên", "chủ nhiệm", "tình trạng"]

for idx, col_name in enumerate(df_display.columns):
  col_str = str(col_name).lower()
  
  if any(kw in col_str for kw in target_shrink_keywords):
    table_styles.append({
        "selector": f"th.col{idx}, td.col{idx}",
        "props": [
            ("width", "95px"),
            ("max-width", "110px"),
            ("min-width", "75px"),
            ("white-space", "normal !important"),
            ("word-break", "break-word"),
            ("font-size", "12.5px"),
            ("text-align", "center"), # Ép data bên dưới cũng căn giữa
        ],
    })
  elif any(kw in col_str for kw in target_wrap_keywords):
    table_styles.append({
        "selector": f"th.col{idx}, td.col{idx}",
        "props": [
            ("width", "125px"),        # Giới hạn kích thước vừa đủ cho 2 dòng
            ("max-width", "140px"),
            ("min-width", "100px"),
            ("white-space", "normal !important"), 
            ("word-break", "break-word"),
            ("font-size", "13px"), 
            ("text-align", "center"), # Ép data bên dưới cũng căn giữa
        ],
    })

styled_df = df_display.style.apply(color_rows, axis=1).set_table_styles(table_styles)

try:
  styled_df = styled_df.hide(axis="index")
except Exception:
  try:
    styled_df = styled_df.hide_index()
  except:
    pass

html_table = styled_df.to_html()
html_table = html_table.replace("<table", '<table class="custom-table"')
st.markdown(
    f'<div class="custom-table-wrapper">{html_table}</div>',
    unsafe_allow_html=True,
)
