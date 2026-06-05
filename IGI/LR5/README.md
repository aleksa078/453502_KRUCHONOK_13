# LR5 homeFULL — Django риэлтерское агентство

Проект реализует сайт риэлтерского агентства homeFULL по варианту 13: объекты недвижимости, категории, владельцы, покупатели, сотрудники, продажи, новости, контакты, отзывы, промокоды, статистика, внешние API, таймзона пользователя, текстовый календарь, Docker и Render.

## Локальный запуск без Docker

Локально без Docker база: db.sqlite3
Она используется, когда запускаю: python manage.py runserver

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
Remove-Item db.sqlite3 -ErrorAction SilentlyContinue - удалить старую бд
python manage.py migrate
python manage.py seed_data --with-demo-users --with-demo-admin
python manage.py check
python manage.py makemigrations --check --dry-run
python -m pytest
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

Админка: http://127.0.0.1:8000/admin/

Локальные demo-аккаунты создаются только при явных флагах:

```bash
python manage.py seed_data --with-demo-users --with-demo-admin
```

В production demo-admin не создаётся.

## Локальный запуск через Docker

Docker-БД — это PostgreSQL-база

```bash
docker compose down -v
docker compose up --build
```

Docker Compose поднимает PostgreSQL, ждёт healthcheck базы, запускает миграции, collectstatic и seed_data. Для локальной демонстрации создаются demo-users и demo-admin. Картинки подключаются из локальной папки `./media`, поэтому они не перекрываются пустым Docker volume.

Выдаст 
Listening at: http://0.0.0.0:800

Переходим на сайт 
http://localhost:8000/


В конце (когда все посмотрела):
docker compose down - когда просто хочу остановить Docker, но сохранить данные.
ИЛИ
docker compose down -v  - когда хочу удалить все изменения (при запуске демоданные запишутся заново)

docker compose up потом (некст раз)

## Render hosting

В проекте есть `render.yaml` и `build.sh`.

Render создаёт PostgreSQL, передаёт `DATABASE_URL`, выполняет:

```bash
bash build.sh
```

Build script устанавливает зависимости, выполняет миграции, загружает демонстрационные данные без demo-admin и собирает static files. На Render включён `DJANGO_SERVE_MEDIA_FILES=True`, поэтому учебные изображения из `media/` и графики из `media/charts/` отображаются даже при `DJANGO_DEBUG=False`.

После деплоя нужно проверить:

- `/` — главная и последняя новость;
- `/news/` — новости homeFULL с картинками;
- `/contacts/` — 10 контактов с фото;
- `/properties/` — 5 домов и 5 квартир, часть продана, часть доступна для покупки;
- `/statistics/` — графики matplotlib;
- `/api/sales/` — JSON API требует авторизацию.

## Основные файлы реализации

- `core/models.py` — модели, связи, model validation, timestamps UTC/local.
- `core/forms.py` — формы, HTML5 и серверная валидация, загрузка 1–3 фото недвижимости.
- `core/views.py` — Function-Based Views, CRUD, покупка, API, статистика.
- `core/urls.py` — URL, включая `re_path`.
- `core/statistics.py` — расчёт статистики.
- `core/charts.py` — диаграммы matplotlib без JavaScript.
- `core/timezone_utils.py`, `core/middleware.py`, `core/context_processors.py` — ZoneInfo-таймзона и текстовый календарь.
- `core/external_api.py`, `core/parallel_utils.py` — внешние API и ThreadPoolExecutor.
- `core/management/commands/seed_data.py` — базовые сущности и demo-данные.
- `docs/erd.svg` — ER-диаграмма моделей.

## Картинки

Картинки уже лежат в `media/`:

- `media/news/news_01.jpg` ... `news_10.jpg`;
- `media/contacts/contact_01.jpg` ... `contact_10.jpg`;
- `media/properties/house_01_01.jpg` ...;
- `media/properties/apartment_01_01.jpg` ...;
- `media/company/logo.png`.

Если картинка не найдена, шаблоны показывают static-заглушку из `static/img/`.
