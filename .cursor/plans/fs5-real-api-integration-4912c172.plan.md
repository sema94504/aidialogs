<!-- 4912c172-0b86-4178-acc0-490eb682125a 82498d7e-178f-46ff-b9f6-8a4e71309f11 -->
# Спринт FS4: ИИ-чат для администратора

## Обзор

Реализация полнофункционального чат-интерфейса на основе референса 21st.dev с интеграцией в существующий дашборд. Поддержка двух режимов работы: обычный чат с LLM и режим администратора для запросов по статистике.

## Контекст

**Существующая инфраструктура:**

- Frontend: Next.js 15.5.6 + Tailwind CSS 4 + shadcn/ui
- Backend: FastAPI + LLMClient (OpenAI-compatible)
- БД: SQLite (users, messages) через DatabaseManager
- Навигация: уже есть ссылка на /chat в layout

**Референсы:**

- `docs/references/21st-ai-chat.md` - компонент чата
- `frontend/doc/front-vision.md` - design system

## Реализация

### Phase 1: Frontend UI компоненты

#### 1.1 Зависимости

Добавить в `frontend/package.json`:

```json
"dependencies": {
  "framer-motion": "^11.0.0"
}
```

Команда: `cd frontend && pnpm add framer-motion`

#### 1.2 Базовый компонент чата

**Файл:** `frontend/components/ui/ai-chat.tsx`

Адаптация референса из 21st-ai-chat.md:

- Убрать фиксированные размеры (360px × 460px) → responsive
- Добавить пропсы: `mode: "normal" | "admin"`, `onSendMessage`
- Подключить реальный API вместо mock данных
- Сохранить анимации и визуальные эффекты

Интерфейс:

```typescript
interface Message {
  id: string;
  sender: "ai" | "user";
  text: string;
  timestamp: string;
}

interface AIChatProps {
  mode: "normal" | "admin";
  onSendMessage: (text: string) => Promise<void>;
  messages: Message[];
  isTyping: boolean;
  className?: string;
}
```

#### 1.3 Floating Chat Button

**Файл:** `frontend/components/chat/floating-chat-button.tsx`

Компонент для правого нижнего угла:

```typescript
- Кнопка: fixed bottom-4 right-4, z-50
- Иконка: MessageCircle (lucide-react)
- Анимация: scale + bounce эффект
- onClick: toggle состояния чата (свернут/развернут)
- Badge: индикатор непрочитанных (опционально)
```

#### 1.4 Chat Container

**Файл:** `frontend/components/chat/chat-container.tsx`

Контейнер с состоянием и логикой:

- State: messages, mode, isTyping, isExpanded
- API calls через fetch к `/api/chat/message`
- Переключатель режимов (Toggle/Switch)
- Интеграция AIChatCard + FloatingChatButton

#### 1.5 Страница /chat

**Файл:** `frontend/app/chat/page.tsx`

Полноэкранный вариант чата:

- Использует ChatContainer
- Centered layout
- Возможность переключения режимов в UI

#### 1.6 Интеграция в Dashboard

**Файл:** `frontend/app/dashboard/page.tsx`

Добавить FloatingChatButton в конец компонента:

```tsx
<FloatingChatButton />
```

### Phase 2: Backend API

#### 2.1 Pydantic модели

**Файл:** `src/api/chat_models.py`

```python
class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ChatRequest(BaseModel):
    message: str
    mode: Literal["normal", "admin"] = "normal"
    session_id: str | None = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    mode: str
```

#### 2.2 Chat Service

**Файл:** `src/api/chat_service.py`

Класс для обработки запросов:

```python
class ChatService:
    def __init__(self, llm_client: LLMClient, db: DatabaseManager):
        self.llm_client = llm_client
        self.db = db
        self.sessions = {}  # in-memory хранилище сессий
    
    async def process_message(
        self, 
        message: str, 
        mode: str, 
        session_id: str | None
    ) -> tuple[str, str]:
        # Получить или создать сессию
        # Добавить сообщение пользователя в историю
        # Обработать в зависимости от режима
        # Вернуть ответ и session_id
```

**Режим Normal:**

- Прямой вызов `llm_client.get_response(messages)`
- Контекст: история из session

**Режим Admin (MVP - упрощенный):**

- Специальный system prompt: "Ты помощник администратора для анализа статистики Telegram бота"
- Прямой вызов LLM с контекстом о доступных данных
- Опционально: можно добавить несколько простых команд типа `/stats today`

**Режим Admin (полный - опционально):**

- Text2SQL pipeline:

  1. Промпт для генерации SQL из вопроса
  2. Валидация и выполнение SQL через db.fetchall()
  3. Форматирование результатов
  4. Финальный промпт LLM для ответа на естественном языке

#### 2.3 FastAPI endpoint

**Файл:** `src/api/main.py` (добавить)

```python
from src.api.chat_service import ChatService
from src.api.chat_models import ChatRequest, ChatResponse

# В lifespan добавить инициализацию ChatService
chat_service = ChatService(llm_client, db)

@app.post("/api/chat/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest) -> ChatResponse:
    response_text, session_id = await chat_service.process_message(
        message=request.message,
        mode=request.mode,
        session_id=request.session_id
    )
    return ChatResponse(
        message=response_text,
        session_id=session_id,
        mode=request.mode
    )
```

#### 2.4 Конфигурация

Добавить в `.env` (опционально):

```bash
CHAT_SYSTEM_PROMPT_NORMAL=prompts/chat_normal.txt
CHAT_SYSTEM_PROMPT_ADMIN=prompts/chat_admin.txt
```

### Phase 3: Тестирование

#### 3.1 Backend тесты

**Файл:** `tests/api/test_chat.py`

Тесты для:

- POST /api/chat/message в normal режиме
- POST /api/chat/message в admin режиме
- Валидация Pydantic моделей
- Session management

#### 3.2 Интеграционное тестирование

- Тест полного flow: отправка → обработка → ответ
- Проверка сохранения контекста в сессии
- Проверка работы обоих режимов

### Phase 4: Улучшения (опционально)

- Streaming ответов (Server-Sent Events)
- Сохранение истории чата в БД
- Markdown рендеринг в сообщениях
- Code syntax highlighting
- Кнопка "Очистить историю"
- Экспорт чата

## Ключевые файлы

**Новые (Frontend):**

- `frontend/components/ui/ai-chat.tsx`
- `frontend/components/chat/floating-chat-button.tsx`
- `frontend/components/chat/chat-container.tsx`
- `frontend/app/chat/page.tsx`

**Новые (Backend):**

- `src/api/chat_models.py`
- `src/api/chat_service.py`
- `tests/api/test_chat.py`

**Изменяемые:**

- `frontend/package.json` - добавить framer-motion
- `src/api/main.py` - добавить chat endpoint
- `frontend/app/dashboard/page.tsx` - FloatingChatButton

## Критерии готовности

✅ Floating button появляется на всех страницах

✅ Чат открывается/закрывается по клику

✅ Сообщения отправляются и получают ответы

✅ Normal режим: общение с LLM работает

✅ Admin режим: базовые запросы обрабатываются

✅ Переключение режимов работает

✅ Адаптивный дизайн (mobile/desktop)

✅ История сообщений сохраняется в рамках сессии

✅ Тесты API проходят

## Примечания

- Режим Admin на MVP этапе может быть упрощен (без полного text2sql)
- Streaming можно добавить в следующих итерациях
- Фокус на работающем UI и базовой функциональности

### To-dos

- [ ] Установить framer-motion в frontend
- [ ] Создать компонент ai-chat.tsx на основе референса
- [ ] Создать FloatingChatButton компонент
- [ ] Создать ChatContainer с API интеграцией
- [ ] Создать страницу /chat
- [ ] Интегрировать FloatingButton в dashboard
- [ ] Создать Pydantic модели для чата
- [ ] Реализовать ChatService с normal/admin режимами
- [ ] Добавить POST /api/chat/message endpoint
- [ ] Написать тесты для chat API
- [ ] Протестировать работу чата end-to-end