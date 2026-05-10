import streamlit as st
from google import genai
from datetime import datetime, time

# 1. APIキーの設定
API_KEY = "AIzaSyADjTebpiLShna5QKf5IprE90x8dpNQo6Q"
client = genai.Client(api_key=API_KEY)

# 画面設定
st.set_page_config(page_title="なごみ不動産 返信作成ツール", layout="centered")
st.title("反響メール返信アシスタント")

# --- 1. 基本情報の入力 ---
st.subheader("基本情報")
staff_name = st.text_input("担当者名：", value="松下 大作")
prop_name_input = st.text_input("物件名：", placeholder="例：東大阪市川田 倉庫事務所")

col_rent, col_area = st.columns(2)
with col_rent:
    prop_rent = st.text_input("賃料：", placeholder="例：29.7万円")
with col_area:
    prop_area = st.text_input("面積：", placeholder="例：335.54平米")

# --- 2. 宛先情報の設定 ---
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
    items_list = ["身分証明書（運転免許証など両面必須）", "履歴事項全部証明書", "収入証明書（源泉徴収票など）", "住民票", "印鑑証明書", "認印", "実印", "初期費用（ご持参またはお振込み）", "仲介手数料（ご持参またはお振込み）"]
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
input_text = st.text_area("内容（空欄でもOK。補足があれば入力してください）：", height=100)

if st.button("返信案を作成する"):
    # 物件名かお客様名のどちらかがあれば作成開始
    if prop_name_input or r_name:
        with st.spinner("作成中..."):
            try:
                scenario_instruction = ""
                if status == "3. 内見日時の打診（日程の提案・相談）":
                    scenario_instruction = f"内覧の打診として以下の日時を提示してください。{extra_info}"
                elif status == "4. 内見日時の確定（決定した日時の確認）":
                    scenario_instruction = f"以下の日時で内覧が確定した旨を伝え、最終確認をしてください。{extra_info}"
                elif status == "5. 契約ご来店のご案内（持ち物・場所の連絡）":
                    scenario_instruction = f"契約（重説）のご来店案内です。店舗（堺市北区新金岡町）へお越しいただく旨を伝え、以下の持ち物を明記してください。{extra_info}"

                prompt = f"""
あなたは「なごみ不動産」の「{staff_name}」です。
以下の情報を元に、プロフェッショナルな不動産メールを作成してください。

【宛先】
{recipient_display}

【物件情報】
物件名：{prop_name_input}
賃料：{prop_rent}
面積：{prop_area}

【状況】
{status}

【補足内容（空欄の場合あり）】
{input_text}

【必須ルール】
1. 挨拶：冒頭は【宛先】を記載し、直後に「なごみ不動産の{staff_name}でございます。」と名乗ること。
2. 件名：物件名のみの形式にすること（例：{prop_name_input} のお問い合わせについて）。人名・社名・担当者名は含めない。
3. 本文：物件名、賃料、面積を必ず明記。補足内容が空欄の場合でも、選択された【状況】にふさわしい丁寧な文面をゼロから作成すること。
4. 禁止事項：他物件の紹介、システム定型文、管理番号の記載はすべて禁止。
5. 結び：必ず「引き続きよろしくお願い申し上げます。」で締めること。
6. 署名：以下の署名をすべて黒文字で付けること。

なごみ不動産
担当：{staff_name}
大阪府堺市北区新金岡町5-3-105-201
TEL：072-370-0001
E-mail: matsushita@nagomihudousan.com
"""
                response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
                st.subheader("作成されたメール案")
                st.code(response.text, language="text")
            except Exception as e:
                st.error(f"エラー：{e}")
    else:
        st.warning("物件名またはお客様名を入力してください。")