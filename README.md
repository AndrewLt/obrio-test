### Відео з коментарями: https://drive.google.com/file/d/1NwllGmUVidd7VTFToZsutNv0y7FZMSt4/view?usp=sharing

Як це працює:
1. Отримуємо запит на отримання інформації про застосунок
2. Отримуємо 100 коментарів до цього застосунку
3. За допомогою https://huggingface.co/MarieAngeA13/Sentiment-Analysis-BERT класифікуємо отримані коментарі. Важливо, що працює тільки для англійської мови (найкраще)
4. Негативні коментарі відправляємо до LLM (OpenAI 4o-mini тут) аби отримати аналіз та ідеї для виправлення.
5. Розраховуємо додаткову базову інформацію.
6. Відображаємо :)

## Основні залежності
```
1. Ключ OPENAI для роботи з моделлю
2. Розгорнута локально MongoDB на стандартному порті 27017
```

## Python
```commandline
python3 -m venv venv
```

Windows
```commandline
cd venv/Scripts
activate.bat
```

Linux
```commandline
source venv/bin/activate
```

### Requirements
```commandline
pip install -r requirements.txt
```

### Task processing
```commandline
python task_processing.py
```

### Backend run
Перед запуском бекенду, в каталозі backend створити файл .env і додати наступні змінні:
```dotenv
MONGO_HOST="localhost"
MONGO_PORT=27017
```
Потім виконати
```commandline
uvicorn backend.main:app
```

### Streamlit run
```commandline
streamlit run stremlit_visualise.py
```

