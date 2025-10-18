# Быстрый старт Production

Развёртывание полной системы (Bot, API, Frontend) на production сервере.

## Предварительные требования

- Docker и Docker Compose
- 2GB+ RAM
- 1GB+ свободного диска
- Telegram Bot Token
- LLM API доступный

## Установка за 5 минут

### 1. Клонирование и подготовка

```bash
git clone https://github.com/sema94504/aidialogs.git
cd aidialogs
```

### 2. Конфигурация

```bash
cp .env.example .env
nano .env
```

Обязательно заполните:
- `TELEGRAM_BOT_TOKEN` - токен вашего бота
- `LLM_BASE_URL` - адрес LLM сервера
- `API_URL` - публичный URL вашего API (например, https://api.yourdomain.com)

### 3. Запуск

```bash
# Production с оптимизациями
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

## Управление данными

**Volumes:**
- `db_volume` - SQLite БД (автоматически создаётся Docker)
- `logs_volume` - Логи сервисов

**Откуда найти:**

```bash
# Узнать путь volume на сервере
docker volume inspect aidialogs_db_volume

# Обычно находится в:
/var/lib/docker/volumes/aidialogs_db_volume/_data/

# Backup БД
docker run --rm -v aidialogs_db_volume:/data -v $(pwd):/backup \
  alpine cp /data/app.db /backup/backup-$(date +%Y%m%d).db
```

## Доступные сервисы

- **Frontend**: http://localhost:3063
- **API**: http://localhost:8063
- **API Docs**: http://localhost:8063/docs
- **Health Check**: http://localhost:8063/health

## Управление

```bash
# Остановка
docker-compose down

# Перезапуск
docker-compose restart

# Полная очистка (включая data)
docker-compose down -v

# Логи отдельного сервиса
docker-compose logs -f <service_name>
```

## Мониторинг здоровья

```bash
# Проверка статуса healthcheck
docker-compose ps

# Проверка API
curl http://localhost:8063/health

# Проверка Frontend
curl http://localhost:3063/
```

## Troubleshooting

### Контейнеры не запускаются

```bash
docker-compose logs
# Проверьте конфиг .env
```

### Нет доступа к БД

```bash
# Проверьте права на директорию
ls -la /var/lib/aidialogs/
chmod -R 755 /var/lib/aidialogs
```

### LLM не доступен

```bash
# Проверьте LLM_BASE_URL в .env
# Убедитесь, что LLM сервер запущен и доступен
curl $LLM_BASE_URL
```

## Production best practices

1. Используйте reverse proxy (nginx/traefik) спереди
2. Настройте SSL/TLS сертификаты
3. Регулярно сохраняйте БД из /var/lib/aidialogs/data
4. Мониторьте логи из /var/log/aidialogs
5. Используйте docker-compose.prod.yml для лучшей производительности

## Дополнительно

Полная документация: см. [DOCKER.md](./DOCKER.md)
