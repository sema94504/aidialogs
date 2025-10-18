# Инструкция для финального теста Docker Setup

## Предварительные требования

✅ Docker установлен  
✅ Docker Compose установлен  
✅ Порты 3000 и 8000 свободны  
✅ ~10 GB свободного места  

---

## Шаг 1: Настройка переменных окружения

```bash
# 1. Скопировать шаблон
cp env.docker.template .env.docker

# 2. Отредактировать (минимум - указать TELEGRAM_BOT_TOKEN)
nano .env.docker
```

**Обязательно изменить:**
- `TELEGRAM_BOT_TOKEN=your_bot_token_here` → указать реальный токен

**Опционально изменить (если нужно):**
- `LLM_BASE_URL` - если LLM сервер на другом адресе
- `USE_MOCK_STATS=true` - для тестирования без реальных данных

---

## Шаг 2: Сборка образов (5-10 минут)

```bash
make docker-build
```

**Ожидаемый результат:**
- Соберутся 3 образа: aidialogs-bot, aidialogs-api, aidialogs-frontend
- Процесс займет 5-10 минут
- В конце должно быть "Successfully built" для каждого образа

**Если ошибка:**
```bash
# Посмотреть детали ошибки
docker compose build
```

---

## Шаг 3: Запуск сервисов

```bash
make docker-up
```

**Ожидаемый результат:**
```
Creating aidialogs-bot ... done
Creating aidialogs-api ... done
Creating aidialogs-frontend ... done
```

---

## Шаг 4: Проверка статуса

```bash
make docker-status
```

**Ожидаемый результат:**
Все 3 контейнера в статусе "Up":
```
NAME                  STATUS
aidialogs-bot         Up X seconds
aidialogs-api         Up X seconds  
aidialogs-frontend    Up X seconds
```

**Если контейнер не запустился:**
```bash
# Посмотреть логи проблемного сервиса
make docker-logs-bot
make docker-logs-api
make docker-logs-frontend
```

---

## Шаг 5: Проверка логов

```bash
# Все сервисы
make docker-logs

# Или по отдельности
make docker-logs-bot
make docker-logs-api
make docker-logs-frontend
```

**Что искать в логах:**

**Bot:**
- ✅ "Бот запущен" или "Bot started"
- ❌ Ошибки подключения к БД
- ❌ Ошибки токена Telegram

**API:**
- ✅ "Uvicorn running on http://0.0.0.0:8000"
- ✅ "Application startup complete"
- ❌ Ошибки подключения к БД

**Frontend:**
- ✅ "ready started server on 0.0.0.0:3000"
- ✅ "compiled successfully"
- ❌ Build errors

---

## Шаг 6: Проверка HTTP доступности

### API Health Check
```bash
curl http://localhost:8000/health
```
**Ожидается:** `{"status":"ok"}`

### API Root
```bash
curl http://localhost:8000/
```
**Ожидается:** JSON с информацией об API

### API Docs (в браузере)
Открыть: http://localhost:8000/docs

**Ожидается:** Swagger UI с документацией API

### Frontend (в браузере)
Открыть: http://localhost:3000

**Ожидается:** Веб-интерфейс приложения

---

## Шаг 7: Проверка базы данных

```bash
# Проверить, что БД создалась
ls -lh ./data/

# Должен быть файл aidialogs.db
```

---

## Шаг 8: Тест взаимодействия

### Через Telegram бот
1. Найти бота в Telegram по токену
2. Отправить `/start`
3. Отправить тестовое сообщение
4. Получить ответ от LLM

### Через API (curl)
```bash
# Получить статистику
curl http://localhost:8000/api/stats

# Отправить сообщение в чат
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Привет!",
    "mode": "assistant"
  }'
```

### Через Frontend
1. Открыть http://localhost:3000
2. Проверить отображение статистики
3. Попробовать отправить сообщение в чате

---

## Остановка и очистка

### Остановка сервисов
```bash
make docker-down
```

### Просмотр логов после остановки
```bash
docker compose logs
```

### Полная очистка (удаление volumes)
```bash
make docker-clean
```
⚠️ Это удалит ./data/ с базой данных!

---

## Чеклист успешного теста

### Обязательные проверки
- [ ] Все 3 образа собрались без ошибок
- [ ] Все 3 контейнера запустились (Status: Up)
- [ ] `curl http://localhost:8000/health` → `{"status":"ok"}`
- [ ] http://localhost:8000/docs открывается
- [ ] http://localhost:3000 открывается
- [ ] ./data/aidialogs.db существует

### Дополнительные проверки
- [ ] Telegram бот отвечает на /start
- [ ] API возвращает статистику
- [ ] Frontend отображает данные
- [ ] Нет критических ошибок в логах

---

## Типичные проблемы и решения

### Проблема 1: Порты заняты
```bash
# Проверить
netstat -tuln | grep -E ':(3000|8000)'

# Найти процесс
lsof -i :3000
lsof -i :8000

# Убить процесс (замените PID)
kill -9 <PID>
```

### Проблема 2: Недостаточно места
```bash
# Проверить место
df -h

# Очистить неиспользуемые образы
docker system prune -a
```

### Проблема 3: Ошибка сборки UV
```
ERROR: Could not find uv.lock
```
**Решение:** Убедитесь, что uv.lock существует в корне проекта

### Проблема 4: Frontend не собирается
```
ERROR: Cannot find module 'next'
```
**Решение:** Проверьте frontend/package.json и frontend/pnpm-lock.yaml

### Проблема 5: Bot не подключается к Telegram
```
ERROR: Unauthorized
```
**Решение:** Проверьте TELEGRAM_BOT_TOKEN в .env.docker

### Проблема 6: LLM не отвечает
```
ERROR: Connection refused to LLM server
```
**Решение:** 
- Проверьте LLM_BASE_URL в .env.docker
- Используйте `http://host.docker.internal:ПОРТ` для локального сервера
- Или установите `USE_MOCK_STATS=true` для тестирования

---

## Время выполнения теста

| Этап | Время |
|------|-------|
| Настройка .env.docker | 2 мин |
| Сборка образов | 5-10 мин |
| Запуск контейнеров | 30 сек |
| Проверки | 5 мин |
| **Итого** | **~15-20 мин** |

---

## Результат успешного теста

После успешного прохождения всех шагов:

✅ Docker setup работает  
✅ Все сервисы доступны  
✅ Можно использовать для разработки  
✅ Готово к переходу на спринт D1  

---

## Следующие шаги

После успешного теста можно:
1. Остановить сервисы: `make docker-down`
2. Переходить к спринту **D1: Build & Publish**
3. Настроить GitHub Actions для автоматической сборки

---

## Полезные команды

```bash
# Список контейнеров
docker ps

# Логи в реальном времени
docker compose logs -f

# Перезапуск конкретного сервиса
docker compose restart bot

# Зайти внутрь контейнера
docker compose exec bot bash
docker compose exec api bash
docker compose exec frontend sh

# Просмотр использования ресурсов
docker stats

# Удалить все контейнеры и образы
docker compose down --rmi all -v
```

---

**Готово!** Следуйте инструкциям по порядку и отмечайте выполненные шаги.

