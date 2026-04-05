# Memory and Context Specification


## Session state

На уровне сессии хранятся:
- `session_id` или `user_id`
- `last_user_query`
- `normalized_query`
- `active_filters`
- `last_results`
- `last_interaction_ts`

---

## Пример состояния

```json
{
  "session_id": "tg_123456",
  "last_user_query": "graph neural networks for traffic prediction",
  "normalized_query": "graph neural networks traffic forecasting",
  "active_filters": {
    "year_from": 2022
  },
  "last_results": ["arxiv:1111.1111", "arxiv:2222.2222"],
  "last_interaction_ts": "2026-04-02T12:00:00Z"
}
```

---

## Memory policy

- память ограничена одной активной сессией
- долгосрочная персональная память не используется
- после истечения TTL состояние очищается
- если контекст не найден, follow-up обрабатывается как новый запрос

---

## Context budget

В LLM передается только ограниченный контекст:
- текущий пользовательский запрос
- нормализованный запрос
- активные фильтры
- title + abstract + metadata ограниченного числа статей

Не передаются:
- полная история сообщений
- полные результаты прошлых запросов
- лишние служебные логи

---

## Ограничения

- session state должен быть компактным
- хранение PII не допускается
- состояние не должно быть критической зависимостью для основного workflow
- отсутствие memory не должно приводить к ошибке сервиса
