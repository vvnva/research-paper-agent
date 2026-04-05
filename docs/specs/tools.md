# Tools and APIs Specification


## 1. Telegram Bot API

### Назначение
- получение сообщений от пользователя
- отправка ответов пользователю

### Вход
- текстовое сообщение пользователя
- metadata Telegram update

### Выход
- отправленное текстовое сообщение с результатами поиска

### Ошибки
- network error
- Telegram rate limit
- invalid webhook/update payload

### Timeout
- `1-3 сек` на отправку сообщения

### Side effects
- отправка сообщения пользователю

### Защита
- валидация входных payload
- ограничение длины исходного сообщения
- безопасное форматирование ответа

---

## 2. arXiv API

### Назначение
- поиск научных статей по query

### Вход
- поисковый запрос
- опциональные фильтры
- лимит числа результатов

### Выход
- список статей и их metadata

### Ошибки
- timeout
- network error
- пустой ответ
- invalid response format
- rate limit / temporary unavailability

### Timeout
- `3-5 сек` на один запрос

### Side effects
- отсутствуют

### Защита
- retry только на idempotent вызовах
- нормализация и валидация ответа
- ограничение числа результатов

---

## 3. LLM API

### Назначение
Используется для:
- query rewriting
- ranking / reranking
- summarization

### Вход
- структурированный prompt
- query
- metadata статей
- abstract статей

### Выход
- rewritten query
- score / ranking explanation
- summary

### Ошибки
- timeout
- provider unavailable
- rate limit
- quota exceeded
- invalid structured output

### Timeout
- `3-5 сек` на один вызов

### Side effects
- отсутствуют

### Защита
- строгий prompt template
- ограничение контекста
- structured output validation
- fallback при недоступности модели
