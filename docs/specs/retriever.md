# Retriever Specification



## Источник данных

Текущий источник:
- `arXiv API`

PoC работает с одним внешним источником без локального индекса

---

## Вход

Входные данные:
- `query`: строка поискового запроса после query rewriting
- `filters`:
  - `year_from` — опционально
  - `max_results` — число кандидатов
  - `category` — опционально

Пример:

```json
{
  "query": "graph neural networks traffic forecasting",
  "filters": {
    "year_from": 2022,
    "max_results": 15
  }
}
```

---

## Выход

Выход модуля — список кандидатов в нормализованном формате:

```json
[
  {
    "paper_id": "arxiv:1234.5678",
    "title": "Paper title",
    "abstract": "Short abstract text",
    "authors": ["Author A", "Author B"],
    "published_at": "2024-03-10",
    "categories": ["cs.LG"],
    "url": "https://arxiv.org/abs/1234.5678"
  }
]
```

---

## Основные шаги

1. Получить rewritten query
2. Сформировать запрос к arXiv API
3. Выполнить вызов внешнего API
4. Преобразовать ответ в внутренний формат
5. Отфильтровать пустые и некорректные записи
6. Удалить дубли
7. Вернуть список кандидатов в `Ranker`

---

## Поиск и reranking

`Retriever` отвечает только за retrieval и базовую фильтрацию.

Внутри модуля допускаются:
- deduplication
- базовая сортировка по дате или релевантности источника
- отсечение пустых записей

Полноценный reranking выполняется отдельным модулем `Ranker`.

---

## Ограничения

- только один внешний источник
- локальный индекс отсутствует
- embeddings retrieval не используется
- анализ полного PDF не выполняется
- число кандидатов ограничено конфигурацией
- retrieval должен быть idempotent
