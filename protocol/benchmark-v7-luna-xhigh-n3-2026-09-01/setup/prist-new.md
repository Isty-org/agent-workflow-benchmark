# Browser-free Prist setup — empty product baseline

Работай только в папке `<ABSOLUTE_CELL_PATH>` и сначала перейди в неё. Не открывай соседние benchmark-ячейки, управляющий репозиторий, measured prompts, evaluator или evidence прежних серий.

Это подготовка метода до продуктовой задачи. Hosted project и repository connection уже созданы организатором. Используй только project-local инструкции, файлы и MCP. Browser/UI, создание hosted project, перевыпуск connection, owner-release через UI и просьбы человеку открыть UI запрещены. Если project-local MCP не готов, остановись и точно опиши setup defect.

Проверь authenticated identity, `connection_ready`, правильный project context, отсутствие pending sync и запрещённых legacy project IDs. Установи или доведи до переносимого состояния project-local Prist workflow и `spec-driven-work`, если connection kit оставил допустимые локальные шаги.

Сохрани пустой продуктовый baseline: не создавай product specs, PRD, архитектуру, WorkItems, ChangeStreams, source code или tests. Будущую продуктовую задачу не пытайся угадывать. Допустимы только method/workflow/configuration files и безопасные setup receipts без credentials.

Проверь, что Git remote отсутствует, credentials не tracked, repository clean после setup commit и тот же commit работает в отдельном clean worktree через project-local MCP без browser/UI. В финале перечисли readiness, hosted project ID, HEAD/tree, состав method files, число product specs, diagnostics, pending sync, проверки и любые ограничения. Не копируй credential или полные tool payloads в ответ.
