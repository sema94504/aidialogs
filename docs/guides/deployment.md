# Deployment

Подготовка к продакшену и автоматизация через Makefile.

## Makefile команды

Все команды автоматизации в одном месте.

```makefile
# Качество кода
make format     # Форматирование (ruff format)
make lint       # Проверка стиля (ruff check)
make typecheck  # Проверка типов (mypy)

# Тестирование
make test       # Запуск тестов
make coverage   # Покрытие кода

# Запуск
make run        # Запуск бота

# Очистка
make clean      # Удаление временных файлов
```

## Проверка перед деплоем

### Полная проверка качества

```bash
# Последовательно
make format
make lint
make typecheck
make test
make coverage

# Одной командой
make format && make lint && make typecheck && make coverage
```

**Критерии готовности:**
- ✅ Ruff форматирование применено
- ✅ Ruff линтер: 0 ошибок
- ✅ Mypy: 0 ошибок типизации
- ✅ Pytest: все тесты зеленые
- ✅ Покрытие: >80%

## Текущий статус (на момент документа)

```bash
$ make coverage

Name                     Stmts   Miss  Cover
--------------------------------------------
src/bot.py                  57      1    98%
src/config.py                7      0   100%
src/llm_client.py           24      0   100%
src/main.py                 21      1    95%
src/session_manager.py      12      0   100%
--------------------------------------------
TOTAL                      121      2    98%

28 passed in 4.64s
```

**Статус:** ✅ Готов к продакшену

## Запуск в продакшене

### Через Makefile

```bash
make run
```

### Напрямую

```bash
uv run python -m src.main
```

### С переменными окружения

```bash
TELEGRAM_BOT_TOKEN=xxx LLM_BASE_URL=yyy uv run python -m src.main
```

## Конфигурация продакшена

### Переменные окружения

```bash
export TELEGRAM_BOT_TOKEN="production_token"
export LLM_BASE_URL="http://prod-server:3000/v1"
export LLM_MODEL="gpt-oss:latest"
export SYSTEM_PROMPT_FILE="prompts/system_prompt.txt"

make run
```

### Systemd Service

Создайте `/etc/systemd/system/aidialogs.service`:

```ini
[Unit]
Description=AI Dialogs Telegram Bot
After=network.target

[Service]
Type=simple
User=aidialogs
WorkingDirectory=/opt/aidialogs
Environment="TELEGRAM_BOT_TOKEN=your_token"
Environment="LLM_BASE_URL=http://localhost:3000/v1"
Environment="LLM_MODEL=gpt-oss:latest"
Environment="SYSTEM_PROMPT_FILE=prompts/system_prompt.txt"
ExecStart=/usr/local/bin/uv run python -m src.main
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Управление:**
```bash
# Запуск
sudo systemctl start aidialogs

# Включение автозапуска
sudo systemctl enable aidialogs

# Статус
sudo systemctl status aidialogs

# Логи
sudo journalctl -u aidialogs -f
```

## Логирование

### Текущая настройка

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),      # Консоль
        logging.FileHandler("bot.log") # Файл
    ]
)
```

### Просмотр логов

```bash
# В реальном времени
tail -f bot.log

# Последние 100 строк
tail -n 100 bot.log

# Поиск ошибок
grep ERROR bot.log

# Поиск по пользователю
grep "пользователя 123456" bot.log
```

### Ротация логов

Используйте logrotate для управления размером логов.

`/etc/logrotate.d/aidialogs`:
```
/opt/aidialogs/bot.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    copytruncate
}
```

## Мониторинг

### Проверка работоспособности

```bash
# Процесс запущен
ps aux | grep "src.main"

# Логи без ошибок
tail -n 50 bot.log | grep ERROR

# Отправка тестового сообщения боту
# (вручную через Telegram)
```

### Метрики из логов

```bash
# Количество обработанных сообщений сегодня
grep "$(date +%Y-%m-%d)" bot.log | grep "Сообщение от" | wc -l

# Количество ошибок
grep ERROR bot.log | wc -l

# Уникальные пользователи
grep "пользователя" bot.log | grep -oP 'пользователя \K\d+' | sort -u | wc -l
```

## Backup и восстановление

### Что бэкапить

**Конфигурация:**
- `.env` (секреты)
- `prompts/system_prompt.txt` (роль)

**Код:**
- Git репозиторий (основной backup)

**Данные:**
- Нет персистентных данных (все в памяти)
- История теряется при перезапуске (MVP)

### Backup конфигурации

```bash
# Создание backup
tar -czf aidialogs-backup-$(date +%Y%m%d).tar.gz .env prompts/

# Восстановление
tar -xzf aidialogs-backup-20251016.tar.gz
```

## Обновление в продакшене

### Процесс обновления

```bash
# 1. Остановка бота
sudo systemctl stop aidialogs

# 2. Backup конфигурации
tar -czf backup-$(date +%Y%m%d).tar.gz .env prompts/

# 3. Обновление кода
git pull origin main

# 4. Обновление зависимостей
uv sync --extra dev

# 5. Проверка качества
make format && make lint && make typecheck && make test

# 6. Запуск
sudo systemctl start aidialogs

# 7. Проверка логов
sudo journalctl -u aidialogs -f
```

### Откат при проблемах

```bash
# 1. Остановка
sudo systemctl stop aidialogs

# 2. Откат кода
git checkout <previous-commit>

# 3. Восстановление конфига (если нужно)
tar -xzf backup-20251016.tar.gz

# 4. Запуск
sudo systemctl start aidialogs
```

## Безопасность

### Секреты

**НЕ коммитьте:**
- `.env` файл
- Токены в коде
- API ключи

**Используйте:**
- Переменные окружения
- Systemd Environment
- Secret management сервисы (для больших проектов)

### Права доступа

```bash
# Ограничение доступа к .env
chmod 600 .env

# Отдельный пользователь для бота
sudo useradd -r -s /bin/false aidialogs
sudo chown -R aidialogs:aidialogs /opt/aidialogs
```

## Масштабирование

### Текущие ограничения

**Однопоточность:**
- Один процесс бота
- SessionManager в памяти процесса
- При перезапуске история теряется

**Для MVP это достаточно.**

### Горизонтальное масштабирование (будущее)

Если понадобится:
1. Добавить Redis для сессий
2. Несколько инстансов бота
3. Load balancer для Telegram webhook

**Но для MVP это оверинжиниринг.**

## Troubleshooting в продакшене

### Бот не отвечает

**Проверка:**
```bash
# Процесс запущен?
ps aux | grep "src.main"

# Есть ошибки в логах?
tail -n 50 bot.log

# LLM API доступен?
curl http://your-server:3000/v1/models

# Telegram API доступен?
curl https://api.telegram.org
```

### Высокое потребление памяти

**Причина:** История диалогов растет бесконечно.

**Решение:**
- Пользователи делают `/reset`
- Или перезапуск бота (история очищается)

### Медленные ответы

**Причины:**
- LLM API медленный
- Большая история диалога (много токенов)

**Решение:**
- Оптимизация LLM сервера
- Ограничение длины истории (будущая фича)

## Проверочный чеклист

Перед деплоем в продакшен:

- [ ] Все тесты зеленые (`make test`)
- [ ] Покрытие >80% (`make coverage`)
- [ ] Линтер чист (`make lint`)
- [ ] Типы проверены (`make typecheck`)
- [ ] `.env` настроен правильно
- [ ] `prompts/system_prompt.txt` готов
- [ ] Логирование работает
- [ ] Тестовый запуск успешен
- [ ] Секреты не в git
- [ ] Документация актуальна

## Следующие шаги

- [Troubleshooting](troubleshooting.md) - решение проблем
- [Configuration](configuration.md) - настройка конфигурации
- [Development](development.md) - процесс разработки


