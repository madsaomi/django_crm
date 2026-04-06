# 📚 Education CRM

CRM-система для управления образовательным центром. Позволяет вести учёт студентов, групп, преподавателей, посещаемости и платежей.

## 🚀 Возможности

- **Дашборд** — общая статистика и графики доходов
- **Студенты** — добавление, редактирование, профиль студента
- **Группы** — управление группами, расписание с drag & drop
- **Преподаватели** — карточки преподавателей, привязка к группам
- **Менеджеры** — панель менеджера, KPI
- **Посещаемость** — журнал посещаемости по группам
- **Платежи** — учёт оплат, долги
- **KPI** — метрики эффективности

## 🛠 Технологии

- Python 3.12+
- Django 6.0+
- PostgreSQL
- HTML / CSS / JavaScript
- Chart.js

## ⚙️ Установка и запуск

### 1. Клонирование репозитория

```bash
git clone https://github.com/your-username/education-crm.git
cd education-crm
```

### 2. Создание виртуального окружения

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка базы данных

Создайте базу данных PostgreSQL и обновите параметры подключения в `crm_project/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'crm_db',
        'USER': 'postgres',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Применение миграций

```bash
python manage.py migrate
```

### 6. Создание суперпользователя

```bash
python manage.py createsuperuser
```

### 7. Загрузка тестовых данных (опционально)

```bash
python manage.py seed_data
```

### 8. Запуск сервера

```bash
python manage.py runserver
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000) в браузере.

## 📁 Структура проекта

```
├── apps/
│   ├── attendance/     # Посещаемость
│   ├── groups/         # Группы и расписание
│   ├── kpi/            # KPI и метрики
│   ├── managers/       # Менеджеры
│   ├── payments/       # Платежи
│   ├── students/       # Студенты
│   └── teachers/       # Преподаватели
├── crm_project/        # Настройки Django
├── static/css/         # Стили
├── templates/          # HTML-шаблоны
├── manage.py
└── requirements.txt
```

## 📝 Лицензия

MIT
