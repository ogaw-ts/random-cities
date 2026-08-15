import streamlit as st
import requests
import random
import time

# 地方と都道府県のマッピング
REGIONS = {
    "北海道": ["北海道"],
    "東北": ["青森県", "岩手県", "宮城県", "秋田県", "山形県", "福島県"],
    "関東": ["茨城県", "栃木県", "群馬県", "埼玉県", "千葉県", "東京都", "神奈川県"],
    "中部": [
        "新潟県",
        "富山県",
        "石川県",
        "福井県",
        "山梨県",
        "長野県",
        "岐阜県",
        "静岡県",
        "愛知県",
    ],
    "近畿": ["三重県", "滋賀県", "京都府", "大阪府", "兵庫県", "奈良県", "和歌山県"],
    "中国": ["鳥取県", "島根県", "岡山県", "広島県", "山口県"],
    "四国": ["徳島県", "香川県", "愛媛県", "高知県"],
    "九州": ["福岡県", "佐賀県", "長崎県", "熊本県", "大分県", "宮崎県", "鹿児島県"],
    "沖縄": ["沖縄県"],
}

ALL_PREFECTURES = [pref for prefs in REGIONS.values() for pref in prefs]


@st.cache_data(show_spinner=False)
def get_cities(prefecture):
    """APIから指定した都道府県の市町村を取得し、キャッシュする"""
    url = f"http://geoapi.heartrails.com/api/json?method=getCities&prefecture={prefecture}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if "response" in data and "location" in data["response"]:
                return list(set(loc["city"] for loc in data["response"]["location"]))
    except Exception as e:
        st.error(f"{prefecture}のデータ取得に失敗しました: {e}")
    return []


# --- UI構築（縦型レイアウト） ---

st.set_page_config(page_title="おでかけルーレット", page_icon="🎲")

st.title("🎲 おでかけルーレット 🗾")
st.write("市町村をランダムに１つ選びます！")

# 折りたたみメニューでオプション設定を配置
with st.expander("⚙️ オプション", expanded=True):
    st.info("💡 地方・都道府県を指定しない場合は全国が対象になります")

    selected_regions = st.multiselect("地方を選ぶ", options=list(REGIONS.keys()))

    selected_prefectures = st.multiselect("都道府県を選ぶ", options=ALL_PREFECTURES)

    st.write("対象とする自治体")
    # 縦型画面でも綺麗に収まるようカラムで分割
    col1, col2, col3 = st.columns(3)
    with col1:
        use_city = st.checkbox("市", value=True)
    with col2:
        use_town = st.checkbox("町", value=True)
    with col3:
        use_village = st.checkbox("村", value=True)

types = []
if use_city:
    types.append("市")
if use_town:
    types.append("町")
if use_village:
    types.append("村")

# 余白を追加してボタンを目立たせる
# st.markdown("<br>", unsafe_allow_html=True)

# --- メイン処理（ルーレット） ---

if st.button("🎯 ルーレットを回す！", use_container_width=True):
    if not types:
        st.error("市、町、村のいずれかにチェックを入れてください！")
    else:
        target_prefs = set()
        if selected_regions:
            for region in selected_regions:
                target_prefs.update(REGIONS[region])
        if selected_prefectures:
            target_prefs.update(selected_prefectures)

        if not target_prefs:
            target_prefs.update(ALL_PREFECTURES)

        with st.status(
            f"対象となる {len(target_prefs)} 都道府県のデータを集めています...",
            expanded=True,
        ) as status:
            all_cities = []
            progress_bar = st.progress(0)

            for idx, pref in enumerate(target_prefs):
                cities = get_cities(pref)
                for city in cities:
                    all_cities.append({"prefecture": pref, "city": city})
                progress_bar.progress((idx + 1) / len(target_prefs))

            status.update(label="データ取得完了！", state="complete", expanded=False)

        filtered_cities = [
            item for item in all_cities if any(item["city"].endswith(t) for t in types)
        ]

        if not filtered_cities:
            st.warning(
                "指定された条件に合致する市町村が見つかりませんでした。条件を変えてお試しください。"
            )
        else:
            st.write("### 🥁 抽選中...")
            placeholder = st.empty()

            for _ in range(15):
                temp_choice = random.choice(filtered_cities)
                placeholder.markdown(
                    f"<h3 style='text-align: center; color: gray;'>{temp_choice['prefecture']} {temp_choice['city']}</h3>",
                    unsafe_allow_html=True,
                )
                time.sleep(0.1)

            result = random.choice(filtered_cities)
            placeholder.empty()

            st.balloons()
            st.success("🎉 行き先が決定しました！")
            st.markdown(
                f"<h1 style='text-align: center; color: #ff4b4b;'>{result['prefecture']}<br>{result['city']}</h1>",
                unsafe_allow_html=True,
            )
