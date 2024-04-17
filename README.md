## Запуск проекта

Установить зависимости:

```bash
poetry install
```

Войти в окружение poetry:

```bash
poetry shell
```

Запустить FastAPI-приложение.

```bash
uvicorn app.main:app --reload
```

После этого сервер запуститься на порту 8000. Чтобы проверить подключение сделайте запрос на [localhost:8000](http://localhost:8000).

```bash
curl localhost:8000
```

Проверка API с помощью Swagger: [localhost:8000/docs](http://localhost:8000/docs).
