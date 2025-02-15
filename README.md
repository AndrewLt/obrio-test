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
```commandline
uvicorn backend.main:app
```

### Streamlit run
```commandline
streamlit run stremlit_visualise.py
```

