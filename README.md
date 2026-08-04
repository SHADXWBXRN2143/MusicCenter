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

## Экран на самом Pi (киоск-режим)

Есть отдельная компактная страница `http://<IP-Pi>:5000/kiosk` — большая
обложка, название/исполнитель, часы, play/pause/prev/next. Без сайдбара и
навигации, вёрстка резиновая (`vh`/`vw`/`clamp`), рассчитана на маленький
экран (типично 3.5", ~480×320), но не привязана к конкретному разрешению.

**Выбор экрана.** Проще всего — 3.5" экран, где GPIO только для питания/тача,
а видео идёт по отдельному mini-HDMI кабелю: он определяется как обычный
монитор, без возни с драйверами фреймбуфера под конкретную модель. Если
берёте "чистый" SPI/GPIO-экран (Waveshare и т.п., видео через GPIO) — там
нужен драйвер под конкретную модель, напишите, какая именно, когда выберете.

**Настройка автозапуска в киоск-режим** (Raspberry Pi OS Lite, без рабочего
стола — меньше накладных расходов для устройства, которое всегда показывает
одно и то же):

```bash
sudo apt install --no-install-recommends -y \
    xserver-xorg x11-xserver-utils xinit openbox chromium-browser unclutter

sudo raspi-config
# System Options → Boot / Auto Login → Console Autologin
```

В конец `~/.bash_profile` (создайте, если нет):
```bash
if [ -z "$DISPLAY" ] && [ "$(tty)" = "/dev/tty1" ]; then
    startx
fi
```

Создайте `~/.xinitrc`:
```bash
xset -dpms
xset s off
xset s noblank
unclutter -idle 0.5 -root &
openbox-session &
chromium-browser \
    --kiosk \
    --noerrdialogs \
    --disable-infobars \
    --disable-session-crashed-bubble \
    --check-for-update-interval=31536000 \
    http://localhost:5000/kiosk
```

`sudo reboot` — Pi должен загрузиться прямо в это окно, без рабочего стола и
без возможности из него выйти (что и нужно для приборной панели).

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
- Отдельный компактный экран `/kiosk` для маленького дисплея на самом Pi

## Если звука нет

- Проверьте, что `mpv` установлен: `mpv --version`. Если бинарник не найден,
  плеер на сайте покажет баннер "mpv не найден на этом устройстве" — сайт при
  этом продолжает работать (можно смотреть библиотеку и искать), но
  воспроизведение недоступно.
- Тот же баннер появляется и когда `mpv` установлен, но не может стартовать —
  в логе (`sudo journalctl -u musiccenter -n 40`) это выглядит как
  `mpv did not create its IPC socket in time`. Частая причина: **сервис
  запущен через systemd, а не в интерактивном логине**, поэтому у mpv нет
  доступа к пользовательской сессии PipeWire/PulseAudio, через которую он
  обычно выводит звук, и он падает при попытке открыть аудио-устройство.
  Решение уже встроено — mpv по умолчанию выводит звук через ALSA напрямую
  (`PLAYER_AUDIO_OUTPUT=alsa` в `.env`), в обход PipeWire/Pulse. Если у вас
  несколько аудиоустройств (HDMI/джек/USB) и звук идёт не туда, посмотрите
  доступные карты через `aplay -l` и укажите конкретную:
  `PLAYER_AUDIO_OUTPUT=alsa/hw:1,0`.
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
