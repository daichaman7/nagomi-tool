import streamlit as st
import google.generativeai as genai
from datetime import datetime, time

# 1. APIキーの設定（Secretsがなければ直接設定）
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = "AIzaSyADjTebpiLShna5QKf5IprE90x8dpNQo6Q"

genai.configure(api_key=API_KEY)

# 画面設定
st.set_page_config(page_title="なごみ不動産 返信作成ツール", layout="centered")
st.title("反響メール返信アシスタント")

# --- 1. 基本情報の入力 ---
st.subheader("基本情報")
staff_name = st.text_input("担当者名：", value="松下 大作")
prop_name_input = st.text_input("物件名：")

col_rent, col_area = st.columns(2)
with col_rent:
    prop_rent = st.text_input("賃料：")
with col_area:
    prop_area = st.text_input("面積：")

# --- 2. 宛先情報 ---
st.write("---")
st.subheader("宛先情報")
recipient_type = st.radio("宛先種別：", ("個人", "法人"), horizontal=True)

if recipient_type == "個人":
    r_name = st.text_input("お客様名：")
    recipient_display = f"{r_name}様"
else:
    r_company = st.text_input("法人名：")
    r_title = st.text_input("役職（任意）：")
    r_name = st.text_input("ご担当者名：")
    recipient_display = f"{r_company}\n{r_title} {r_name}様" if r_title else f"{r_company}\n{r_name}様"

# --- 3. 状況の選択 ---
st.write("---")
status = st.radio(
    "状況を選択してください：",
    ("1. 募集中（最初のお礼・内覧誘致）", 
     "2. お申し込み中（お断り）", 
     "3. 内見日時の打診（日程の提案・相談）", 
     "4. 内見日時の確定（決定した日時の確認）", 
     "5. 契約ご来店のご案内（持ち物・場所の連絡）")
)

extra_info = ""
if status in ["3. 内見日時の打診（日程の提案・相談）", "4. 内見日時の確定（決定した日時の確認）"]:
    col_date, col_time = st.columns(2)
    with col_date:
        d = st.date_input("該当日付", datetime.now())
    with col_time:
        t = st.time_input("開始時間", time(10, 0))
    label = "候補日時" if "打診" in status else "確定日時"
    extra_info = f"\n【{label}】\n{d.strftime('%m月%d日')} {t.strftime('%H時%M分')}〜"

elif status == "5. 契約ご来店のご案内（持ち物・場所の連絡）":
    items_list = ["身分証明書", "履歴事項全部証明書", "収入証明書", "住民票", "印鑑証明書", "認印", "実印", "初期費用", "仲介手数料"]
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**契約者様**")
        c_selected = [item for item in items_list if st.checkbox(item, key=f"c_{item}")]
    with col_b:
        st.write("**保証人様**")
        g_selected = [item for item in items_list if st.checkbox(item, key=f"g_{item}")]
    if c_selected: extra_info += f"\n【契約者様ご持参品】\n・" + "\n・".join(c_selected)
    if g_selected: extra_info += f"\n【保証人様ご持参品】\n・" + "\n・".join(g_selected)

st.write("---")
tone = st.selectbox("トーン：", ("標準的なビジネス", "非常に丁寧", "簡潔に"))
input_text = st.text_area("内容（補足があれば）：", height=100)

if st.button("返信案を作成する"):
    if prop_name_input or r_name:
        with st.spinner("AI作成中..."):
            try:
                # ここを最新かつ安定したモデル名に変更しました
                model = genai.GenerativeModel('gemini-1.5-flash-latest')
                
                prompt = f"あなたは「なごみ不動産」の「{staff_name}」です。{recipient_display}に対し、{status}のメールをトーン「{tone}」で作成してください。物件：{prop_name_input}({prop_rent}/{prop_area})。補足：{input_text}{extra_info}。署名：なごみ不動産 担当{staff_name} 大阪府堺市北区新金岡町5-3-105-201 TEL:072-370-0001"
                
                response = model.generate_content(prompt)
                st.subheader("作成された返信案")
                st.code(response.text, language="text")
            except Exception as e:
                st.error(f"エラーが発生しました：{e}")
