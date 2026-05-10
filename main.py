import streamlit as st
import google.generativeai as genai
from datetime import datetime, time

# --- 1. セキュリティ設定（Secretsを優先的に読み込み） ---
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    # クラウド未設定時の予備（念のため）
    API_KEY = "AIzaSyADjTebpiLShna5QKf5IprE90x8dpNQo6Q"

genai.configure(api_key=API_KEY)

# 画面設定
st.set_page_config(page_title="なごみ不動産 返信作成ツール", layout="centered")
st.title("反響メール返信アシスタント")

# --- 2. 基本情報の入力 ---
st.subheader("基本情報")
staff_name = st.text_input("担当者名：", value="松下 大作")
prop_name_input = st.text_input("物件名：", placeholder="例：東大阪市川田 倉庫事務所")

col_rent, col_area = st.columns(2)
with col_rent:
    prop_rent = st.text_input("賃料：", placeholder="例：29.7万円")
with col_area:
    prop_area = st.text_input("面積：", placeholder="例：335.54平米")

# --- 3. 宛先情報の設定 ---
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

# --- 4. 状況の選択 ---
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

# 日時選択（状況3または4）
if status in ["3. 内見日時の打診（日程の提案・相談）", "4. 内見日時の確定（決定した日時の確認）"]:
    st.write("---")
    st.subheader("日時の選択")
    col_date, col_time = st.columns(2)
    with col_date:
        d = st.date_input("該当日付", datetime.now())
    with col_time:
        t = st.time_input("開始時間", time(10, 0))
    label = "候補日時" if "打診" in status else "確定日時"
    extra_info = f"\n【{label}】\n{d.strftime('%m月%d日')} {t.strftime('%H時%M分')}〜"

# 契約時の持ち物選択（状況5）
elif status == "5. 契約ご来店のご案内（持ち物・場所の連絡）":
    st.write("---")
    st.subheader("ご持参いただくものの選択")
    items_list = ["身分証明書", "履歴事項全部証明書", "収入証明書", "住民票", "印鑑証明書", "認印", "実印", "初期費用（持参・振込）", "仲介手数料（持参・振込）"]
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**契約者様 持ち物**")
        c_selected = [item for item in items_list if st.checkbox(item, key=f"c_{item}")]
    with col_b:
        st.write("**保証人様 持ち物**")
        g_selected = [item for item in items_list if st.checkbox(item, key=f"g_{item}")]
    if c_selected: extra_info += f"\n【契約者様のご持参品】\n・" + "\n・".join(c_selected)
    if g_selected: extra_info += f"\n【保証人様のご持参品】\n・" + "\n・".join(g_selected)

st.write("---")
tone = st.selectbox("トーン：", ("標準的なビジネス", "非常に丁寧", "簡潔に"))
input_text = st.text_area("内容（補足があれば入力してください）：", height=100)

if st.button("返信案を作成する"):
    if prop_name_input or r_name:
        with st.spinner("AIが文章を作成中..."):
            try:
                # 最新の安定モデルを指定
                model = genai.GenerativeModel("gemini-1.5-flash-latest")
                
                prompt = f"""
あなたは「なごみ不動産」の「{staff_name}」として、プロフェッショナルな不動産メールを作成してください。
【宛先】{recipient_display}
【物件】{prop_name_input} (賃料:{prop_rent}, 面積:{prop_area})
【状況】{status}
【トーン】{tone}
【補足】{input_text}
{extra_info}

【ルール】
1. 挨拶：冒頭は「{recipient_display}」とし、「なごみ不動産の{staff_name}でございます。」と名乗る。
2. 件名：物件名のみ（例：{prop_name_input} のお問い合わせについて）。
3. 本文：スペック（賃料・面積）を必ず明記。
4. 結び：「引き続きよろしくお願い申し上げます。」で締める。
5. 署名：
なごみ不動産
担当：{staff_name}
大阪府堺市北区新金岡町5-3-105-201
TEL：072-370-0001
E-mail: matsushita@nagomihudousan.com
"""
                response = model.generate_content(prompt)
                st.subheader("作成されたメール案")
                st.code(response.text, language="text")
            except Exception as e:
                st.error(f"エラーが発生しました：{e}")
    else:
        st.warning("物件名またはお客様名を入力してください。")
