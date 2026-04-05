# Serving and Configuration Specification

## Serving

Сервис состоит из следующих runtime-компонентов:
- Telegram bot interface
- backend application
- orchestrator
- session state store
- logging / observability layer

PoC предполагает один backend service без горизонтального масштабирования

---

## Конфигурация

Конфигурация задается через `.env`.

Примеры параметров:
- `TELEGRAM_BOT_TOKEN`
- `LLM_API_KEY`
- `ARXIV_TIMEOUT_SEC`
- `LLM_TIMEOUT_SEC`
- `MAX_CANDIDATES`
- `SESSION_TTL_SEC`
- `RETRY_COUNT`
- `LOG_LEVEL`

---

## Секреты

К секретам относятся:
- Telegram bot token
- LLM API key

Требования:
- не хранить секреты в репозитории
- передавать секреты через environment
- ограничить доступ к production secrets

---

## Версии моделей

Для PoC фиксируются:
- одна основная LLM для rewriting / ranking / summarization
- версия модели задается конфигурацией
- смена модели не должна требовать переписывания бизнес-логики

---

## Ресурсные ограничения

- ограниченное число LLM-вызовов на запрос
- ограниченный размер контекста
- ограниченное число кандидатов для ranking
- отсутствие batch processing и фоновых workers в первой версии

---

## Надежность запуска

- сервис должен стартовать без session store в degraded mode
- при недоступности LLM сервис не должен падать на уровне процесса
- конфигурация валидируется на старте приложения

---

## Deployment assumptions

Для PoC допускается:
- локальный запуск
- single-instance deployment
- ручное управление конфигурацией
