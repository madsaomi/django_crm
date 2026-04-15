# 📚 EduCRM — CRM для учебного центра

CRM-система для управления образовательным центром. Ведёт учёт студентов, групп, преподавателей, расписания, посещаемости и платежей.

## 🖥️ Демо-доступ

| Роль | Логин | Пароль |
|------|-------|--------|
| **Админ** | `admin` | `admin` |
| **Менеджер** | `manager1` | `123` |
| **Учитель** | `teacher1` | `123` |

## 🚀 Возможности

- **Дашборд** — статистика, графики доходов (Chart.js), заполненность групп
- **Ученики** — 40 учеников с реальными именами, профили, история платежей и посещений
- **Группы** — 6 групп (Kids English, General English, IELTS, SAT), чётные/нечётные дни
- **Расписание** — визуальное расписание с Drag & Drop (Sortable.js)
- **Кабинеты** — матрица занятости помещений
- **Преподаватели** — карточки с группами и статистикой
- **Менеджеры** — панель менеджера, рекрутинг, KPI
- **Посещаемость** — журнал с матрицей по месяцам, AJAX-переключение статусов
- **Платежи** — учёт оплат, расчёт долгов, финансовый реестр с экспортом в Excel
- **KPI** — метрики эффективности менеджеров и учителей
- **Архив** — soft delete с возможностью восстановления
- **Тёмная тема** — с сохранением в localStorage
- **PWA** — работает как мобильное приложение
- **HTMX** — модальные формы без перезагрузки страницы

## 🛠 Технологии

- **Backend**: Python 3.12+, Django 6.0
- **Database**: SQLite3
- **Frontend**: Bootstrap 5.3, HTMX 1.9, Chart.js, Sortable.js
- **Шрифт**: Inter (Google Fonts)
- **Деплой**: Gunicorn + WhiteNoise, Procfile для Railway

## ⚙️ Установка и запуск

### 1. Клонирование

```bash
git clone https://github.com/your-username/django-crm.git
cd django-crm
```

### 2. Виртуальное окружение

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка окружения

```bash
cp .env.example .env
# Отредактируйте .env — установите SECRET_KEY
```

### 5. Миграции и данные

```bash
python manage.py migrate
python manage.py seed_data     # Засеивает БД реалистичными данными
python init_db.py              # Создаёт суперпользователя admin/admin
```

### 6. Запуск

```bash
python manage.py runserver
```

Откройте [http://127.0.0.1:8000](http://127.0.0.1:8000)

## 📁 Структура проекта

```
django_crm/
├── apps/
│   ├── attendance/     # Посещаемость и журнал
│   ├── groups/         # Группы, расписание, зачисления, воскресные ивенты
│   ├── kpi/            # KPI аналитика менеджеров и учителей
│   ├── managers/       # Менеджеры, рекрутинг, архив
│   ├── payments/       # Платежи, долги, финансовый реестр, Excel-экспорт
│   ├── students/       # Ученики
│   └── teachers/       # Преподаватели
├── crm_project/        # Настройки Django (settings, urls, wsgi)
├── static/css/         # Кастомные стили (glassmorphism, dark mode)
├── templates/          # HTML-шаблоны (base, dashboard, все модули)
├── manage.py
├── requirements.txt
├── Procfile            # Деплой на Railway
└── initial_data.json   # Fixture с тестовыми данными
```

## 📝 Лицензия

MIT
