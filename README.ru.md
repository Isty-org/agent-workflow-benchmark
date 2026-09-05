# Бенчмарк агентских процессов разработки

**[English version](README.md)**

Бенчмарк с сохранённой доказательной базой сравнивает четыре агентских процесса разработки в трёх сценариях изменения ПО. Финальная когорта: **3 сценария × 4 метода × 3 независимых повтора = 36 измеряемых first-pass задач**.

Репозиторий представляет собой переносимый публичный export: замороженные промпты, входные данные сценариев, оценки, машиночитаемые результаты, отчёты, ссылки на evidence, инструменты проверки и манифесты release assets. Исходные артефакты бенчмарка сохранены на исходном языке.

## Результаты

Каждая строка ниже — медиана трёх measured tasks в одной ячейке «сценарий × метод». Стоимость рассчитана по provider-reported usage измеряемой задачи и замороженному pricing snapshot. Elapsed time считается от старта measured task до первого финального ответа. В таблице указаны точные миллисекунды и точная расчётная стоимость в USD; минуты соответствуют читаемому представлению исходного отчёта.

| Сценарий | Метод | Медиана качества (/100) | Медиана measured task cost (USD) | Медиана elapsed time |
|---|---|---:|---:|---:|
| Новый проект | Plain | 69 | $0.42385148 | 2,013,443 ms (33.6 min) |
| Новый проект | BMAD | 69 | $1.36481868 | 3,629,356 ms (60.5 min) |
| Новый проект | Classic | 45 | $3.12769884 | 4,074,624 ms (67.9 min) |
| Новый проект | Prist | 87 | $0.26662576 | 1,257,000 ms (20.9 min) |
| Небольшой существующий проект | Plain | 35 | $10.077087 | 4,204,885 ms (70.1 min) |
| Небольшой существующий проект | BMAD | 29 | $1.44226984 | 3,648,434 ms (60.8 min) |
| Небольшой существующий проект | Classic | 39 | $7.90102716 | 4,194,725 ms (69.9 min) |
| Небольшой существующий проект | Prist | 69 | $0.43872212 | 1,556,000 ms (25.9 min) |
| Большой существующий проект | Plain | 98 | $4.05826076 | 3,811,712 ms (63.5 min) |
| Большой существующий проект | BMAD | 25 | $0.8408026 | 2,041,483 ms (34.0 min) |
| Большой существующий проект | Classic | 82 | $6.09135428 | 2,394,283 ms (39.9 min) |
| Большой существующий проект | Prist | 98 | $0.2068444 | 815,000 ms (13.6 min) |

В этом снимке из 36 задач Prist показал минимальную медианную стоимость measured task и минимальный elapsed time во всех трёх сценариях. Медиана качества Prist была максимальной в новом и небольшом проектах и совпала с Plain на уровне 98 в большом проекте. Медианы качества Plain составили 69, 35 и 98; BMAD — 69, 29 и 25; Classic — 45, 39 и 82; Prist — 87, 69 и 98. Вывод относится к наблюдаемой когорте и перечисленным ниже условиям.

Исходный [финальный отчёт](reports/benchmark-v7-final/BENCHMARK-REPORT.md) содержит медианы токенов, все 36 строк, разбор оценок и комментарии по сценариям. [source-snapshot.json](reports/benchmark-v7-final/source-snapshot.json) — авторитетный машиночитаемый источник результатов.

## Дизайн 3 × 4 × 3

### Сценарии

1. **Новый проект:** создать локальный веб-сервис списка чтения с тремя статусами, русским интерфейсом и сохранением данных после перезапуска.
2. **Небольшой существующий проект:** добавить редактирование и удаление сообщений Telegram, сохранив авторизацию, очередь, повторы, защиту от дублей, удобные для интеграции ошибки и документацию.
3. **Большой существующий проект:** добавить поиск последних записей по названию встречи или приложению, обновление по мере ввода, сброс, пустое состояние и русский/английский интерфейс.

Точные пользовательские запросы сохранены на русском языке в [protocol prompts](protocol/benchmark-v7-luna-xhigh-n3-2026-09-01/prompts/) и замороженном evidence.

### Методы

- **Plain:** исходный репозиторий и обычное поведение Codex без установки сравниваемой методологии.
- **BMAD:** BMAD Method 6.11.0, модуль `bmm`, интеграция Codex.
- **Classic:** repository-based процесс со спецификациями, Work Items, трассировкой и проверками в репозитории.
- **Prist:** hosted Prist, project-local connection kit и управляемый сервисом spec-driven workflow.

В условии Classic использовалась **русскоязычная edition `classic-2026.08`**. Планируемая англоязычная edition является переводом этого процесса. Эта когорта не запускала и не оценивала английскую edition, поэтому результаты её не измеряют.

### Условия выполнения

- Три независимых запуска в каждой ячейке «сценарий × метод» (`n=3/cell`), 12 ячеек и 36 measured tasks.
- Единый профиль модели и reasoning: `gpt-5.6-luna`, reasoning `xhigh`.
- Подготовленные замороженные baselines. Plain в новом проекте начинал с пустого baseline; условия существующих проектов получали назначенный замороженный продуктовый baseline и подготовленное состояние метода/канона.
- Один first pass, зафиксированный при первом финальном ответе, без repair turns. Допускалось до двух уточняющих вопросов; медиана равна нулю во всех ячейках.
- Measured agents не использовали браузер/UI и видели только назначенный корень продукта/метода.
- Objective checks выполнялись три раза на неизменяемом first-pass состоянии. Качество объединяло замороженные автоматические проверки, blind review и severity caps.

Вес функциональности составлял 50 баллов, regression/build/smoke — 20, архитектуры и соответствия проекту — 20, scope/UX/security — 10. Critical finding ограничивал официальный результат 49 баллами, major finding — 69.

## Границы измерений

Столбец стоимости охватывает provider usage измеряемой задачи разработки. Подготовка baseline, историческое внедрение метода, историческое создание канона, ожидание человека и оценка находятся за границами этой метрики. В наблюдаемом цикле новые provider-затраты на setup/canon равны нулю благодаря подготовленным baselines. Бенчмарк поддерживает выводы о **measured task cost и elapsed time** этой когорты. Total lifecycle cost этим экспериментом не установлен.

External evaluation девяти строк Prist потребовала 29,710,054 токена и стоила $1.14781888. Она учтена отдельно и исключена из межметодных отношений. Сопоставимая external-evaluation cost для всех четырёх методов не собиралась, поэтому сравнение evaluator cost не входит в выводы бенчмарка.

## Provenance и известные ограничения evidence

Авторитетная когорта объединяет **27 задач V7 для Plain/BMAD/Classic** и **9 permissions-corrected задач V7C для Prist**. Выбранная реплика Classic small-project r3 — разрешённая инфраструктурная замена V7. Для всех 12 результатов large-project применён единый supplemental evaluator V7C; реализации, usage и timing сравнительных методов остаются из V7. Детали выбора и hash conventions описаны в [PROVENANCE.md](PROVENANCE.md).

В двух унаследованных evaluations V7 отсутствует явное поле raw score. Отчёт содержит capped official value в `quality.rawBeforeSeverityCap` для `v7-new-bmad-r3` (69 в источнике, 85 восстановлено по checks) и `v7-new-plain-r2` (69 в источнике, 81 восстановлено). Оба official score остаются равными 69 из-за major-finding cap. Re-evaluation сообщает эти два известных расхождения и отклоняет любые дополнительные.

Prompts, scenario inputs, evaluations, JSON, reports и evidence сохранены на исходном языке и без содержательных изменений. Исторические абсолютные локальные пути остаются только в неизменённых evidence и locks. Публичная документация и исполняемые инструкции используют пути относительно репозитория.

## Уровни воспроизводимости

### 1. Verify

Проверка полного Git payload, структуры когорты, task identities, lineage, ссылок на evidence, pricing, timing, scores и агрегированных медиан. Требуется Python 3.12+.

```text
npm run verify
```

Проверка assets требует девять побайтово сохранённых локальных raw ZIP и девять sanitized packages в Git-ignored каталоге `release-assets/`. Команда сверяет каждый package member с его raw source:

```text
python scripts/verify.py --assets
```

Подробности: [VERIFY.md](VERIFY.md).

### 2. Re-evaluate

Повторный расчёт scores по замороженным objective outcomes, blind reviews, weights и severity caps:

```text
npm run reevaluate
```

Команда пересчитывает 36 scores и воспроизводит каждый official score. Подробности: [REEVALUATE.md](REEVALUATE.md).

### 3. Rerun

Материализация проверенного baseline и сборка нового launch prompt для новой экспериментальной когорты:

```text
python scripts/prepare.py --run v7-new-bmad-r1 --kind baselines --destination work/rerun-new-bmad-r1 --prompt-output work/rerun-new-bmad-r1.txt
```

Rerun требует исходный профиль модели/reasoning, зависимости сценариев, sanitized release packages и доступный pinned Prist environment. Локальный identity-файл создаётся из `specs/.me.template` после материализации и остаётся вне публичного evidence. Новые запуски формируют новый provenance. Подробности: [RERUN.md](RERUN.md).

CI-equivalent Git-only suite:

```text
npm run check
```

## Карта репозитория

| Каталог | Содержимое |
|---|---|
| `data/cohort.json`, `data/rows/` | Авторитетная выборка из 36 строк и точные проекции результатов |
| `reports/benchmark-v7-final/` | Исходный русский Markdown/HTML отчёт и source JSON |
| `protocol/`, `inputs/` | Замороженные prompts, rubric, contracts, baselines, launch components и method locks |
| `evidence/`, `manifests/` | Выбранные first-pass, usage, evaluation, review, checks, freeze и source-manifest records |
| `evaluator/`, `scripts/`, `schemas/` | Замороженные check harnesses и переносимые инструменты verify/replay/materialization |
| `provenance/`, `verification/`, `hashes/` | Source lineage, acceptance evidence, payload locks и raw SHA-256 inventory |
| `assets/` | Raw provenance, описания sanitized packages, member inventories, Classic license scope, checksums и upload manifest |

Числа собраны в [INVENTORY.md](INVENTORY.md), работа с архивами описана в [RELEASE-ASSETS.md](RELEASE-ASSETS.md).

## Ограничения

- `n=3/cell` представляет первый сравнительный снимок. Он не оценивает долгосрочную дисперсию и поведение на других задачах, моделях, reasoning profiles или версиях инструментов.
- Три сценария охватывают три размера проекта и конкретные изменения. В других доменах соотношение может измениться.
- Подготовленные baselines задают сравнение measured tasks. Исторические затраты на внедрение и создание канона не измерялись.
- First-pass и browser-free условия описывают протокол бенчмарка. Интерактивные процессы и repair turns могут давать другие результаты.
- Медианы сжимают разброс внутри ячейки. Все 36 строк доступны в финальном отчёте и машиночитаемом snapshot.
- Evaluation cost Prist собрана отдельно; сравнение evaluator cost четырёх методов отсутствует.
- Английская edition Classic не входила в когорту.
- Два описанных расхождения `rawBeforeSeverityCap` остаются ограничениями источника.

## Лицензия и статус публикации

Apache-2.0 применяется к созданной издателем обвязке репозитория, публичной документации, verification tooling, package metadata и Isty-owned Classic methodology files, совпавшим с hash-scope из [LICENSE-NOTES.md](LICENSE-NOTES.md). Остальные замороженные inputs, evidence, reports, материалы методов, продуктовые baselines, созданные реализации, зависимости, названия сервисов и товарные знаки сохраняют существующие условия; подробности находятся в [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

[Upload manifest](assets/release-upload-manifest.json) для `v1.0.0` разрешает публикацию девяти детерминированных sanitized evidence packages. В них 32 096 source members сохранены с побайтовым совпадением; 27 локальных `specs/.me` и один generated `.pyc` исключены с hash accounting. Девять raw ZIP остаются неизменными локальными provenance inputs и не загружаются напрямую. Hashes packages перечислены в [assets/PACKAGE-SHA256SUMS](assets/PACKAGE-SHA256SUMS).
