# Визуализация проекта

Диаграммы AI Dialogs Bot с разных точек зрения.

## Обзор системы

### High-Level архитектура

```mermaid
graph TB
    User[👤 Пользователь<br/>Telegram] -->|Сообщения| TG[Telegram Bot API]
    TG -->|Webhook/Polling| Bot[🤖 AI Dialogs Bot]
    Bot -->|HTTP| LLM[🧠 LLM Server<br/>OpenAI API]
    
    Bot -->|Читает| Env[📄 .env<br/>Конфигурация]
    Bot -->|Читает| Prompt[📝 system_prompt.txt<br/>Роль ассистента]
    Bot -->|Пишет| Log[📋 bot.log<br/>Логи]
    
    style User fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style TG fill:#1a202c,stroke:#0088cc,stroke-width:3px,color:#ffffff
    style Bot fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style LLM fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Env fill:#1a202c,stroke:#ecc94b,stroke-width:2px,color:#ffffff
    style Prompt fill:#1a202c,stroke:#ed8936,stroke-width:2px,color:#ffffff
    style Log fill:#1a202c,stroke:#718096,stroke-width:2px,color:#ffffff
```

---

## Архитектура компонентов

### Модульная структура

```mermaid
graph LR
    subgraph "🎯 Entry Point"
        Main[main.py]
    end
    
    subgraph "⚙️ Configuration"
        Config[Config<br/>pydantic-settings]
    end
    
    subgraph "🤖 Telegram Layer"
        Bot[TelegramBot<br/>aiogram]
    end
    
    subgraph "💾 Data Layer"
        SM[SessionManager<br/>in-memory]
    end
    
    subgraph "🧠 AI Layer"
        LLM[LLMClient<br/>OpenAI]
    end
    
    Main -->|создает| Config
    Main -->|создает| LLM
    Main -->|создает| Bot
    Bot -->|использует| LLM
    Bot -->|создает| SM
    LLM -->|читает| Prompt[system_prompt.txt]
    
    style Main fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style Config fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style Bot fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style SM fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style LLM fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Prompt fill:#1a202c,stroke:#f56565,stroke-width:2px,color:#ffffff
```

### Зависимости между классами

```mermaid
classDiagram
    class Config {
        +telegram_bot_token: str
        +llm_base_url: str
        +llm_model: str
        +system_prompt_file: str
    }
    
    class LLMClient {
        -client: OpenAI
        -model: str
        -system_prompt: str
        +get_response(messages) str
        -_read_prompt_file(path) str
    }
    
    class SessionManager {
        -_sessions: dict[int, list]
        +get_session(user_id) list
        +add_message(user_id, role, content)
        +clear_session(user_id)
    }
    
    class TelegramBot {
        -bot: Bot
        -dp: Dispatcher
        -llm_client: LLMClient
        -session_manager: SessionManager
        +start()
        -_start_handler(message)
        -_reset_handler(message)
        -_role_handler(message)
        -_message_handler(message)
    }
    
    TelegramBot --> LLMClient
    TelegramBot --> SessionManager
    
    style Config fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style LLMClient fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style SessionManager fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style TelegramBot fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
```

---

## Потоки данных

### Поток обработки сообщения

```mermaid
sequenceDiagram
    autonumber
    participant U as 👤 Пользователь
    participant T as 📱 Telegram API
    participant B as 🤖 TelegramBot
    participant S as 💾 SessionManager
    participant L as 🧠 LLMClient
    participant A as ☁️ OpenAI API

    U->>T: Отправляет "Привет"
    T->>B: Message event
    
    rect rgb(45, 55, 72)
        Note over B: Обработка входящего сообщения
        B->>B: Логирует сообщение
        B->>S: add_message(123, "user", "Привет")
        S->>S: Сохраняет в _sessions[123]
    end
    
    rect rgb(45, 55, 72)
        Note over B,S: Получение истории
        B->>S: get_session(123)
        S-->>B: [{"role": "user", "content": "Привет"}]
    end
    
    rect rgb(45, 55, 72)
        Note over B,A: Запрос к LLM
        B->>L: get_response(messages)
        L->>L: Добавляет system_prompt
        L->>A: POST /chat/completions
        A-->>L: Response JSON
        L->>L: Извлекает content
        L-->>B: "Здравствуй, смертный"
    end
    
    rect rgb(45, 55, 72)
        Note over B,S: Сохранение ответа
        B->>S: add_message(123, "assistant", "Здравствуй...")
        S->>S: Добавляет в _sessions[123]
    end
    
    B->>T: send_message("Здравствуй...")
    T->>U: Показывает ответ
    
    style U fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style T fill:#1a202c,stroke:#0088cc,stroke-width:3px,color:#ffffff
    style B fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style S fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style L fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style A fill:#1a202c,stroke:#805ad5,stroke-width:3px,color:#ffffff
```

### Обработка команды /start

```mermaid
sequenceDiagram
    participant U as 👤 Пользователь
    participant B as 🤖 Bot
    participant S as 💾 SessionManager
    participant L as 📋 Logger

    U->>B: /start
    B->>L: INFO: Команда /start от user_id=123
    B->>S: clear_session(123)
    S->>S: _sessions[123] = []
    B->>U: "Привет! Я AI-ассистент..."
    
    style U fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style B fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style S fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style L fill:#1a202c,stroke:#718096,stroke-width:3px,color:#ffffff
```

### Обработка команды /role

```mermaid
sequenceDiagram
    participant U as 👤 Пользователь
    participant B as 🤖 Bot
    participant L as 🧠 LLMClient
    participant F as 📝 system_prompt.txt

    U->>B: /role
    B->>L: Запрашивает system_prompt
    Note over L: Промпт уже в памяти<br/>(кэш из __init__)
    L-->>B: "Ты высокородный эльф..."
    B->>U: Отправляет промпт
    
    Note over F: Файл читается<br/>только при старте
    
    style U fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style B fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style L fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style F fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
```

---

## Модель данных

### Структура SessionManager

```mermaid
graph TD
    SM[SessionManager] -->|содержит| Sessions{_sessions<br/>dict}
    
    Sessions -->|user_id: 123| U1[User Session 123]
    Sessions -->|user_id: 456| U2[User Session 456]
    Sessions -->|user_id: 789| U3[User Session 789]
    
    U1 --> M1[Message 1<br/>role: user<br/>content: Привет]
    U1 --> M2[Message 2<br/>role: assistant<br/>content: Здравствуй]
    U1 --> M3[Message 3<br/>role: user<br/>content: Как дела?]
    
    U2 --> M4[Message 1<br/>role: user<br/>content: Кто ты?]
    
    U3 --> M5[Empty list]
    
    style SM fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style Sessions fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style U1 fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style U2 fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style U3 fill:#1a202c,stroke:#718096,stroke-width:2px,color:#ffffff
    style M1 fill:#1a202c,stroke:#9f7aea,stroke-width:2px,color:#ffffff
    style M2 fill:#1a202c,stroke:#48bb78,stroke-width:2px,color:#ffffff
    style M3 fill:#1a202c,stroke:#9f7aea,stroke-width:2px,color:#ffffff
    style M4 fill:#1a202c,stroke:#9f7aea,stroke-width:2px,color:#ffffff
    style M5 fill:#1a202c,stroke:#718096,stroke-width:2px,color:#ffffff
```

### Формат сообщения в LLM API

```mermaid
graph LR
    subgraph "Запрос в OpenAI API"
        SYS[🎭 System<br/>role: system<br/>content: Ты эльф...]
        U1[💬 User 1<br/>role: user<br/>content: Привет]
        A1[🤖 Assistant 1<br/>role: assistant<br/>content: Здравствуй]
        U2[💬 User 2<br/>role: user<br/>content: Как дела?]
    end
    
    SYS --> U1
    U1 --> A1
    A1 --> U2
    
    style SYS fill:#1a202c,stroke:#f56565,stroke-width:3px,color:#ffffff
    style U1 fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style A1 fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style U2 fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
```

---

## Жизненный цикл

### Инициализация приложения

```mermaid
stateDiagram-v2
    [*] --> LoadEnv: Запуск main.py
    
    LoadEnv --> CreateConfig: Чтение .env
    CreateConfig --> ValidateConfig: pydantic-settings
    
    ValidateConfig --> Error: ValidationError
    ValidateConfig --> CreateLLM: ✅ Валидация OK
    
    CreateLLM --> ReadPrompt: Инициализация LLMClient
    ReadPrompt --> ErrorPrompt: FileNotFoundError
    ReadPrompt --> CreateBot: ✅ Промпт загружен
    
    CreateBot --> RegisterHandlers: Инициализация TelegramBot
    RegisterHandlers --> StartPolling: Регистрация команд
    
    StartPolling --> Running: Бот запущен
    Running --> [*]: KeyboardInterrupt / Exception
    
    Error --> [*]
    ErrorPrompt --> [*]
    
    style LoadEnv fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style CreateConfig fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style CreateLLM fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style CreateBot fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style Running fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style Error fill:#1a202c,stroke:#f56565,stroke-width:3px,color:#ffffff
    style ErrorPrompt fill:#1a202c,stroke:#f56565,stroke-width:3px,color:#ffffff
```

### Состояния сессии пользователя

```mermaid
stateDiagram-v2
    [*] --> NoSession: Новый пользователь
    
    NoSession --> EmptySession: /start или первое сообщение
    EmptySession --> ActiveSession: Добавлено сообщение
    
    ActiveSession --> GrowingSession: Диалог продолжается
    GrowingSession --> GrowingSession: Новые сообщения
    
    GrowingSession --> EmptySession: /reset
    ActiveSession --> EmptySession: /start
    
    EmptySession --> [*]: Перезапуск бота
    GrowingSession --> [*]: Перезапуск бота
    
    note right of NoSession
        Сессия не существует
        в _sessions dict
    end note
    
    note right of EmptySession
        _sessions[user_id] = []
    end note
    
    note right of GrowingSession
        История растет бесконечно
        (MVP ограничение)
    end note
    
    style NoSession fill:#1a202c,stroke:#718096,stroke-width:3px,color:#ffffff
    style EmptySession fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style ActiveSession fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style GrowingSession fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
```

---

## TDD Workflow

### Цикл разработки

```mermaid
graph TB
    Start([Новая фича]) --> Red
    
    subgraph "🔴 RED Phase"
        Red[Написать падающий тест] --> RunTest1[make test]
        RunTest1 --> CheckRed{Тест падает?}
        CheckRed -->|Нет| FixTest[Исправить тест]
        FixTest --> Red
        CheckRed -->|Да ✅| Green
    end
    
    subgraph "🟢 GREEN Phase"
        Green[Минимальная реализация] --> RunTest2[make test]
        RunTest2 --> CheckGreen{Тест проходит?}
        CheckGreen -->|Нет| FixCode[Исправить код]
        FixCode --> Green
        CheckGreen -->|Да ✅| Refactor
    end
    
    subgraph "♻️ REFACTOR Phase"
        Refactor[Оптимизация кода] --> Quality[make format<br/>make lint<br/>make typecheck]
        Quality --> RunTest3[make test]
        RunTest3 --> CheckTests{Тесты зеленые?}
        CheckTests -->|Нет| Refactor
        CheckTests -->|Да ✅| Commit
    end
    
    Commit[Коммит] --> End([Готово])
    End --> Start
    
    style Red fill:#1a202c,stroke:#f56565,stroke-width:4px,color:#ffffff
    style Green fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style Refactor fill:#1a202c,stroke:#4299e1,stroke-width:4px,color:#ffffff
    style Commit fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Start fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style End fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
```

### Процесс коммита

```mermaid
flowchart TD
    Start([Изменения готовы]) --> Format
    
    Format[make format<br/>Форматирование] --> Lint
    Lint[make lint<br/>Проверка стиля] --> LintOK{0 ошибок?}
    LintOK -->|Нет| FixLint[Исправить ошибки]
    FixLint --> Format
    LintOK -->|Да| Type
    
    Type[make typecheck<br/>Проверка типов] --> TypeOK{0 ошибок?}
    TypeOK -->|Нет| FixType[Исправить типы]
    FixType --> Format
    TypeOK -->|Да| Test
    
    Test[make test<br/>Все тесты] --> TestOK{Все зеленые?}
    TestOK -->|Нет| FixTest[Исправить тесты]
    FixTest --> Format
    TestOK -->|Да| Coverage
    
    Coverage[make coverage<br/>Покрытие] --> CovOK{>80%?}
    CovOK -->|Нет| AddTests[Добавить тесты]
    AddTests --> Test
    CovOK -->|Да| Commit
    
    Commit[git commit] --> End([✅ Готово])
    
    style Format fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style Lint fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style Type fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Test fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style Coverage fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style Commit fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style End fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style FixLint fill:#1a202c,stroke:#f56565,stroke-width:2px,color:#ffffff
    style FixType fill:#1a202c,stroke:#f56565,stroke-width:2px,color:#ffffff
    style FixTest fill:#1a202c,stroke:#f56565,stroke-width:2px,color:#ffffff
    style AddTests fill:#1a202c,stroke:#f56565,stroke-width:2px,color:#ffffff
```

---

## Deployment

### Окружения

```mermaid
graph LR
    subgraph "💻 Development"
        DevEnv[.env<br/>localhost]
        DevLLM[Local LLM<br/>ollama]
        DevBot[Dev Bot<br/>@test_bot]
    end
    
    subgraph "🧪 Testing"
        TestEnv[.env.test]
        TestMock[Mocked LLM]
        TestBot[CI/CD Tests<br/>pytest]
    end
    
    subgraph "🚀 Production"
        ProdEnv[Environment Vars<br/>systemd]
        ProdLLM[Production LLM<br/>remote server]
        ProdBot[Prod Bot<br/>@prod_bot]
    end
    
    DevEnv --> DevLLM
    DevEnv --> DevBot
    DevBot --> DevLLM
    
    TestEnv --> TestMock
    TestEnv --> TestBot
    TestBot --> TestMock
    
    ProdEnv --> ProdLLM
    ProdEnv --> ProdBot
    ProdBot --> ProdLLM
    
    style DevEnv fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style TestEnv fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style ProdEnv fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style DevBot fill:#1a202c,stroke:#4299e1,stroke-width:2px,color:#ffffff
    style TestBot fill:#1a202c,stroke:#ecc94b,stroke-width:2px,color:#ffffff
    style ProdBot fill:#1a202c,stroke:#48bb78,stroke-width:2px,color:#ffffff
```

### Мониторинг и логирование

```mermaid
graph TB
    Bot[🤖 Running Bot] --> Console
    Bot --> File
    Bot --> Metrics
    
    subgraph "📊 Outputs"
        Console[stdout<br/>Консоль]
        File[bot.log<br/>Файл]
        Metrics[Метрики<br/>из логов]
    end
    
    Console --> Human[👤 Разработчик]
    File --> Rotate[logrotate<br/>Ротация]
    Metrics --> Monitor[📈 Мониторинг]
    
    Rotate --> Archive[Архив логов]
    Monitor --> Alert[🚨 Алерты]
    
    style Bot fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style Console fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style File fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style Metrics fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Human fill:#1a202c,stroke:#4299e1,stroke-width:2px,color:#ffffff
    style Monitor fill:#1a202c,stroke:#48bb78,stroke-width:2px,color:#ffffff
    style Alert fill:#1a202c,stroke:#f56565,stroke-width:3px,color:#ffffff
```

---

## Обработка ошибок

### Поток обработки исключений

```mermaid
graph TD
    Start[Запрос пользователя] --> TryBlock[try блок]
    
    TryBlock --> LLMCall[LLM API вызов]
    
    LLMCall -->|Success| Response[Получен ответ]
    LLMCall -->|Exception| Catch[except Exception]
    
    Response --> SaveMsg[Сохранить в историю]
    SaveMsg --> SendUser[Отправить пользователю]
    SendUser --> End[✅ Успех]
    
    Catch --> LogError[logger.error<br/>с контекстом]
    LogError --> SendError[Отправить<br/>Извините, ошибка...]
    SendError --> EndError[⚠️ Graceful failure]
    
    style Start fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style TryBlock fill:#1a202c,stroke:#ecc94b,stroke-width:3px,color:#ffffff
    style LLMCall fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Response fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style Catch fill:#1a202c,stroke:#f56565,stroke-width:3px,color:#ffffff
    style LogError fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style End fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style EndError fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
```

---

## Структура файлов

### Дерево проекта

```mermaid
graph TD
    Root[📁 aidialogs/] --> Src[📁 src/]
    Root --> Tests[📁 tests/]
    Root --> Docs[📁 docs/]
    Root --> Prompts[📁 prompts/]
    Root --> Files[📄 Конфиг файлы]
    
    Src --> Main[main.py<br/>Точка входа]
    Src --> Config[config.py<br/>Config класс]
    Src --> Bot[bot.py<br/>TelegramBot]
    Src --> LLM[llm_client.py<br/>LLMClient]
    Src --> SM[session_manager.py<br/>SessionManager]
    
    Tests --> TConfig[test_config.py]
    Tests --> TBot[test_bot.py]
    Tests --> TLLM[test_llm_client.py]
    Tests --> TSM[test_session_manager.py]
    Tests --> TInt[test_integration.py]
    
    Docs --> Guides[📁 guides/<br/>Гайды]
    Docs --> Vision[vision.md]
    Docs --> Task[tasklist.md]
    
    Prompts --> Prompt[system_prompt.txt<br/>Роль ассистента]
    
    Files --> Make[Makefile<br/>Команды]
    Files --> Pyproject[pyproject.toml<br/>Зависимости]
    Files --> Pytest[pytest.ini<br/>Настройки]
    Files --> Env[.env<br/>Секреты]
    
    style Root fill:#1a202c,stroke:#48bb78,stroke-width:4px,color:#ffffff
    style Src fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style Tests fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style Docs fill:#1a202c,stroke:#ed8936,stroke-width:3px,color:#ffffff
    style Prompts fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
    style Main fill:#1a202c,stroke:#f56565,stroke-width:2px,color:#ffffff
    style Config fill:#1a202c,stroke:#ecc94b,stroke-width:2px,color:#ffffff
    style Bot fill:#1a202c,stroke:#4299e1,stroke-width:2px,color:#ffffff
    style LLM fill:#1a202c,stroke:#9f7aea,stroke-width:2px,color:#ffffff
    style SM fill:#1a202c,stroke:#ed8936,stroke-width:2px,color:#ffffff
```

---

## Покрытие тестами

### Распределение по модулям

```mermaid
pie title Покрытие тестами (98% общее)
    "bot.py : 98%" : 98
    "config.py : 100%" : 100
    "llm_client.py : 100%" : 100
    "main.py : 95%" : 95
    "session_manager.py : 100%" : 100
```

### Типы тестов

```mermaid
graph LR
    subgraph "📦 Тестовый набор"
        Unit[🔬 Unit тесты<br/>23 теста]
        Integration[🔗 Интеграционные<br/>3 теста]
        Main[⚙️ Main тесты<br/>3 теста]
    end
    
    Unit --> Config[Config<br/>валидация]
    Unit --> SM[SessionManager<br/>CRUD]
    Unit --> LLM[LLMClient<br/>API моки]
    Unit --> Bot[TelegramBot<br/>команды]
    
    Integration --> Full[Полный поток<br/>Bot+LLM+SM]
    Integration --> Smoke[Smoke тесты<br/>Инициализация]
    
    Main --> Init[Инициализация]
    Main --> Errors[Обработка ошибок]
    
    style Unit fill:#1a202c,stroke:#48bb78,stroke-width:3px,color:#ffffff
    style Integration fill:#1a202c,stroke:#4299e1,stroke-width:3px,color:#ffffff
    style Main fill:#1a202c,stroke:#9f7aea,stroke-width:3px,color:#ffffff
```

---

## Временная шкала проекта

### Завершенные итерации

```mermaid
gantt
    title Прогресс разработки AI Dialogs Bot
    dateFormat YYYY-MM-DD
    
    section MVP
    Итерация 1: Эхо-бот           :done, i1, 2025-10-10, 1d
    Итерация 2: LLMClient          :done, i2, 2025-10-10, 1d
    Итерация 3: LLM + История      :done, i3, 2025-10-10, 1d
    Итерация 4: Команда /reset     :done, i4, 2025-10-10, 1d
    Итерация 5: Логирование        :done, i5, 2025-10-10, 1d
    Итерация 6: Команда /role      :done, i6, 2025-10-11, 1d
    
    section Documentation
    Создание гайдов               :done, d1, 2025-10-16, 1d
```

---

## Принципы разработки

### SOLID в проекте

```mermaid
mindmap
    root((🎯 SOLID))
        S[Single Responsibility]
            Config_only_config[Config<br/>только конфигурация]
            SM_only_sessions[SessionManager<br/>только сессии]
            LLM_only_api[LLMClient<br/>только LLM API]
            Bot_only_telegram[TelegramBot<br/>только Telegram]
        
        O[Open/Closed]
            Extension_ready[Готов к расширению<br/>новые команды]
            No_modification[Без модификации<br/>существующего]
        
        L[Liskov Substitution]
            Not_applicable[Нет наследования<br/>MVP простота]
        
        I[Interface Segregation]
            Minimal_interfaces[Минимальные интерфейсы<br/>только нужное]
        
        D[Dependency Inversion]
            Constructor_injection[Зависимости через<br/>конструктор]
            Easy_mocking[Простое<br/>мокирование]
```

### Архитектурные принципы

```mermaid
mindmap
    root((⚡ Принципы))
        KISS[KISS]
            Простота[Максимальная<br/>простота]
            No_patterns[Без избыточных<br/>паттернов]
            Direct[Прямой код]
        
        MVP[MVP]
            Minimal[Минимальный<br/>функционал]
            No_db[Без БД<br/>для старта]
            Memory[В памяти]
        
        TDD[TDD]
            Red[🔴 RED фаза]
            Green[🟢 GREEN фаза]
            Refactor[♻️ REFACTOR фаза]
        
        Quality[Качество]
            Tests[98% покрытие]
            Types[Типизация везде]
            Lint[0 ошибок линтера]
```


