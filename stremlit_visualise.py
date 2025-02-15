import streamlit as st
import requests
import time
import matplotlib.pyplot as plt
import seaborn as sns

API_URL = "http://127.0.0.1:8000/api/v1/get-review"

MAX_ATTEMPTS = 5
SLEEP_TIME = 20


def fetch_data(query_params: dict) -> dict|None:
    try:
        response = requests.get(API_URL, params=query_params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Помилка запиту: {e}")
        return {}


def get_data_with_retry(query_params: dict) -> dict:
    for attempt in range(1, MAX_ATTEMPTS + 1):
        with st.spinner(f"Спроба {attempt}: очікуємо результат..."):
            time.sleep(SLEEP_TIME)
            try:
                response = requests.get(API_URL, params=query_params)
                response.raise_for_status()
                response_data = response.json()
                if response_data.get('status') == 'done':
                    return response.json()
            except requests.exceptions.RequestException as e:
                st.warning(f"Спроба {attempt} не вдалася: {e}")
    st.error("Не вдалося отримати дані після декількох спроб.")
    return {}


def display_statistics(basic_stats_data: dict):
    """
    Відображає основні статистичні показники.
    """
    mean = basic_stats_data.get("mean", "Немає даних")
    median = basic_stats_data.get("median", "Немає даних")
    st.markdown(
        f"### Статистичні показники\n"
        f"- **Середнє значення:** {mean}\n"
        f"- **Медіана:** {median}"
    )


def plot_rating_chart(percent_count: dict):
    labels = list(percent_count.keys())
    values = list(percent_count.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=labels, y=values, ax=ax, palette='deep')
    ax.set_xlabel("Оцінки")
    ax.set_ylabel("Відсоток")
    ax.set_title("Розподіл оцінок")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)

    st.pyplot(fig)

def plot_tone_chart(percent_count: dict):
    labels = list(percent_count.keys())
    values = list(percent_count.values())

    fig, ax = plt.subplots(figsize=(8, 5))
    sns.barplot(x=labels, y=values, ax=ax, palette='colorblind')
    ax.set_xlabel("Тон")
    ax.set_ylabel("Відсоток")
    ax.set_title("Розподіл")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)

    st.pyplot(fig)


st.title("Аналіз застосунку")

# Поля введення для app_id і task_id
app_id = st.text_input("Введіть app_id:", key='app_id')
task_id = st.text_input("Введіть task_id:", key='task_id')

placeholder = st.empty()
if st.button("Отримати аналіз"):
    if app_id or task_id:
        # Формування параметрів запиту (ігноруються пусті значення)
        query = {"app_id": app_id, "task_id": task_id}
        query = {key: value for key, value in query.items() if value}

        # Отримання даних з API
        with st.spinner("Отримання даних з API..."):
            data = fetch_data(query)
        if data is None:
            st.stop()

        placeholder.json(data)

        # Якщо в відповіді є taskId і статус не done, виконуємо повторний запит
        if "taskId" in data and data.get('status') != 'done':
            query["taskId"] = data["taskId"]
            # виконується запит кілька разів (очікування коли виконається задача)
            data = get_data_with_retry(query)
            if data is None:
                st.stop()
            placeholder.empty()
            placeholder.json(data)

        # Відображення статистики, якщо дані присутні
        if "basicStats" in data:
            basic_stats = data["basicStats"]
            display_statistics(basic_stats)

            # Відображення графіку, якщо є percentCount
            if "percentCount" in basic_stats:
                plot_rating_chart(basic_stats["percentCount"])
            else:
                st.warning("Немає даних для побудови графіку.")

            # відображення графіку тону
            if "sentimentalPercent" in basic_stats:
                plot_tone_chart(basic_stats["sentimentalPercent"])
            else:
                st.warning("Немає даних для побудови графіку.")

        if "llmInsight" in data:
            st.markdown("### Пропозиції покращення")
            st.markdown(data["llmInsight"])
    else:
        st.warning("Будь ласка, введіть app_id і task_id!")
