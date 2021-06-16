# kfm-grabber

Проект представляет собой Web-приложение на Flask для управления данными о террористических лицах и организациях\
**Требования**\
Python 3.6+\
PostgreSQL\
Интеграция с Sentry\
**Установка**

- Скачать проект
- Установить virtualenv при помощи pip

```
pip install virtualenv
```

- Проект создавался на платформе Windows\
  Установку виртуальной среды на других платформах можно посмотреть на странице
  официальной [документации](https://docs.python.org/3/library/venv.html)
- В директории проекта создать новую виртуальную среду

```
# cmd.exe
cd path_to_project
py -m venv venv
```

- Активировать виртуальную среду

```
# cmd.exe
venv\Scripts\activate.bat
```

- Установить требуемые зависимости

```
# cmd.exe
pip install -r requirements.txt
```

- Создать и настроить файл .env конфигурации переменных окружения перед запуском сервера

```
# Flask secret key
SECRET_KEY=some_key
# Database URL connection args (PostgreSQL)
DATABASE_USER=user
DATABASE_PASSWORD=password
HOST=localhost
PORT=5432
DATABASE_NAME=postgres
# Sentry integration
SENTRY_DSN=project_dsn
# Update database every (minutes)
INTERVAL=60
```

- Запуск сервера

```
export FLASK_APP
python -m flask run
```

**TODO LIST**

- [x] Интеграция с sentry
- [x] Конфигурацию переменными окружения
- [x] Фоновое обновление базы данных
- [x] Логирование
- [x] Поиск в базе данных
- [ ] Фильтрация
- [ ] _Детальное_ логирование