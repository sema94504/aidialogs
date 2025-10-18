# GitHub CLI - Инструкция настройки

**Статус:** ✅ GitHub CLI установлен (версия 2.45.0)

---

## Быстрая настройка

### Вариант 1: Веб-браузер (рекомендуется)

```bash
gh auth login
```

Ответить на вопросы:
```
? What is your preferred protocol for Git operations?
  HTTPS

? Authenticate Git with your GitHub credentials?
  y

? How would you like to authenticate GitHub CLI?
  Login with a web browser
```

Браузер автоматически откроется для завершения авторизации.

### Вариант 2: Personal Access Token (для CI/CD)

1. Создать token на https://github.com/settings/tokens
   - Название: `gh-cli-automation`
   - Scopes:
     - `repo` (полный доступ к репозиториям)
     - `read:packages` (читать пакеты)
     - `write:packages` (писать пакеты)

2. Авторизоваться:
```bash
gh auth login --with-token < token.txt
# или просто ввести при запросе
```

---

## Проверка авторизации

```bash
# Проверить текущего пользователя
gh auth status

# Вывод:
# ✓ Logged in to github.com as sema94504
# ✓ Git operations for github.com configured to use https protocol.
# ✓ Token: ghu_XXXXX...
# ✓ Token scopes: repo, read:packages, write:packages
```

---

## Использование GitHub CLI с Sprint D1

После авторизации можно использовать для:

### 1. Создать Pull Request

```bash
gh pr create \
  --base main \
  --head workflow/gh-actions-build \
  --title "D1: Add GitHub Actions CI/CD" \
  --body "Автоматическая сборка и публикация Docker образов"
```

### 2. Проверить статус workflow

```bash
# Список всех workflow runs
gh run list -L 10

# Проверить статус конкретного run'а
gh run view <run-id>

# Смотреть логи
gh run view <run-id> --log
```

### 3. Управление образами в registry

```bash
# Список пакетов
gh api repos/sema94504/aidialogs/packages

# Сделать пакет публичным
gh api repos/sema94504/aidialogs/packages/aidialogs-bot \
  -X PATCH \
  -f visibility=public
```

### 4. Слить Pull Request

```bash
# Получить информацию о PR
gh pr view

# Слить PR
gh pr merge --merge

# Удалить ветку после merge'а
gh pr delete --yes
```

---

## Статус GitHub CLI

| Компонент | Статус |
|-----------|--------|
| Установка | ✅ 2.45.0 |
| Авторизация | ⏳ Требуется |
| Репозиторий | ✅ sema94504/aidialogs |
| Ветка | ✅ workflow/gh-actions-build |
| Удаленный | ✅ origin |

---

## Следующие шаги

### 1. Авторизоваться в GitHub CLI
```bash
gh auth login
```

### 2. Создать PR (вместо ручного на GitHub UI)
```bash
cd /root/work/aidialogs
gh pr create \
  --base main \
  --head workflow/gh-actions-build \
  --title "D1: Add GitHub Actions CI/CD and registry support" \
  --body-file - << 'EOF'
Добавлены компоненты для автоматической сборки и публикации Docker образов

## Основное:
- GitHub Actions workflow с matrix strategy
- Публикация в GHCR с кэшированием
- docker-compose.registry.yml для deployment
- registry-pull.sh скрипт
- Makefile команды

## Документация:
- docs/github-actions-guide.md (284 строки)
- docs/REGISTRY.md (270 строк)
- README.md обновлен с badge

## Статус:
Все локальные проверки пройдены. Готово к GitHub Actions тестированию.
EOF
```

### 3. Проверить workflow выполнение
```bash
gh run list --workflow build.yml -L 5
```

### 4. После успешной сборки - слить PR
```bash
gh pr merge --merge
```

---

## Полезные команды GitHub CLI

```bash
# Информация о репозитории
gh repo view

# Клоны
gh repo clone owner/repo

# Issues
gh issue list
gh issue create

# Pull Requests
gh pr list
gh pr view
gh pr merge
gh pr close

# Workflow/Actions
gh run list
gh run view <run-id>
gh run rerun <run-id>

# Packages
gh api repos/owner/repo/packages
```

---

**GitHub CLI готов к использованию!**

После авторизации можно использовать все команды для автоматизации работы с GitHub.
