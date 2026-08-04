# MusicCenter

Веб-пульт для Raspberry Pi: показывает библиотеку с домашнего Airsonic-сервера
(артисты, альбомы, поиск), а звук воспроизводит **сам Raspberry Pi** через
`mpv`, подключённый аудиовыходом к музыкальному центру. Управлять можно с
любого устройства в домашней сети (телефон, ноутбук) — открыв в браузере
`http://<IP-адрес-Pi>:5000`.

## Требования

- Raspberry Pi (или любой Linux-хост), подключённый аудиовыходом
  (jack/HDMI/Bluetooth) к музыкальному центру
- Python 3.10+
- `mpv`, установленный в системе: `sudo apt install mpv`
- Работающий Airsonic / Navidrome / другой Subsonic-совместимый сервер в той
  же сети

## Установка и запуск

```bash
git clone <репозиторий> MusicCenter
cd MusicCenter

cp .env.example .env
# отредактируйте .env - впишите AIRSONIC_URL/USERNAME/PASSWORD

set -a; source .env; set +a
./run.sh
```

`run.sh` сам создаст виртуальное окружение, поставит зависимости из
`requirements.txt` и запустит сервер через gunicorn на `0.0.0.0:5000`.

Для разработки можно запускать напрямую:

```bash
pip install -r requirements.txt
python app.py
```

## Настройка

Все параметры — в [`config.py`](config.py), большинство можно переопределить
переменными окружения (см. [`.env.example`](.env.example)):

| Переменная | Назначение | По умолчанию |
|---|---|---|
| `AIRSONIC_URL` | адрес Airsonic-сервера | `http://airsonic.local:4040` |
| `AIRSONIC_USERNAME` / `AIRSONIC_PASSWORD` | логин/пароль | пусто — обязательно задать |
| `PLAYER_DEFAULT_VOLUME` | громкость mpv при старте (0-100) | `70` |
| `PORT` | порт веб-интерфейса | `5000` |
| `DEBUG` | режим отладки Flask | `false` |

Версия Subsonic REST API, которую понимает сервер, может отличаться — если
после запуска библиотека не загружается, проверьте `AIRSONIC_API_VERSION` в
`config.py` (для Airsonic-Advanced обычно подходит `1.15.0`).

## Автозапуск (systemd)

Чтобы сервер поднимался сам при включении Pi и перезапускался при падении:

```bash
sudo cp deploy/musiccenter.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now musiccenter
```

Юнит ожидает, что проект лежит в `/home/admin/MusicCenter`, а `.env` с
настройками — рядом (`/home/admin/MusicCenter/.env`). Если путь или
пользователь другие — поправьте `deploy/musiccenter.service` перед копированием.

Проверить статус и логи:

```bash
sudo systemctl status musiccenter
sudo journalctl -u musiccenter -f
```

## Telegram-бот

Отдельный процесс (`bot/main.py`), управляет плеером через тот же REST API,
что и сайт (`/player/*`, `/search/api`), по `http://127.0.0.1:5000` — не
трогает Airsonic/mpv напрямую и не требует, чтобы сайт был открыт где-либо.

1. Создайте бота через **@BotFather** (`/newbot`), получите токен.
2. Узнайте свой Telegram ID через **@userinfobot** (и остальных, кому нужен
   доступ).
3. В `.env`:
   ```
   TELEGRAM_BOT_TOKEN=<токен от BotFather>
   TELEGRAM_ALLOWED_IDS=123456789,987654321
   ```
   Без ID в списке бот отвечает "Доступ запрещён" — это не публичный бот.
4. Запуск вручную (для проверки):
   ```bash
   set -a; source .env; set +a
   python -m bot.main
   ```
5. Автозапуск через systemd — так же, как для сайта:
   ```bash
   sudo cp deploy/musiccenter-bot.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now musiccenter-bot
   ```

Команды: `/now` — что играет + кнопки play/pause/prev/next/громкость,
`/search <запрос>` — найти альбом/трек и запустить кнопкой из списка.

## Возможности

- Библиотека: артисты, альбомы, поиск с живыми подсказками
- Плеер: очередь, shuffle, повтор (off/all/one), громкость, перемотка
- **Radio-режим** — когда очередь заканчивается, подтягивает похожие треки
  (`getSimilarSongs2`), а если сервер не отдал похожих — просто продолжает
  случайными треками из библиотеки
- **Таймер сна** — ставится в полноэкранном плеере (иконка 🌙), выключает
  паузу через 15/30/45/60 минут; переживает закрытие браузера, так как
  таймер живёт на сервере, а не на клиенте
- **Избранное** — ★ на альбомах/исполнителях/треках
- **Плейлисты** — создание, добавление/удаление треков, воспроизведение
- Полноэкранный "Сейчас играет" — тап по обложке в мини-плеере
- Устанавливается как приложение на телефон (PWA) — "Добавить на экран"
  в браузере (Android/Chrome; на iOS иконка будет системной заглушкой -
  своей PNG-иконки пока нет, только SVG)

## Если звука нет

- Проверьте, что `mpv` установлен: `mpv --version`. Если бинарник не найден,
  плеер на сайте покажет баннер "mpv не найден на этом устройстве" — сайт при
  этом продолжает работать (можно смотреть библиотеку и искать), но
  воспроизведение недоступно.
- Убедитесь, что аудиовыход Pi по умолчанию — тот самый, что подключён к
  музыкальному центру (`raspi-config` → System Options → Audio, либо
  `amixer` / `pactl` в зависимости от дистрибутива).
- В `run.sh` намеренно используется один воркер gunicorn (`--workers 1`) —
  очередь воспроизведения и процесс `mpv` держатся в памяти одного процесса,
  несколько воркеров запустили бы несколько независимых плееров.

## Структура проекта

- `app.py` — точка входа Flask, регистрация blueprint'ов
- `api/airsonic.py` — клиент Subsonic REST API
- `services/` — бизнес-логика: `airsonic_service.py` (нормализация данных),
  `artwork.py` (кэш обложек), `queue.py` (очередь воспроизведения)
- `core/player.py` — управление локальным `mpv` через JSON IPC
- `routes/` — HTTP-роуты (страницы + `/player/*`, `/favorites/*`,
  `/playlists/*` REST API)
- `templates/`, `static/` — интерфейс
- `bot/` — Telegram-бот, отдельный процесс поверх REST API сайта
- `deploy/musiccenter.service`, `deploy/musiccenter-bot.service` —
  systemd-юниты для автозапуска
- `.env.example` — шаблон переменных окружения (реальный `.env` в
  `.gitignore`, туда секреты не попадут)
