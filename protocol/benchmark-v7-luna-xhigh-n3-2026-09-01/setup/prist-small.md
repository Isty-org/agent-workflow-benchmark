# Browser-free Prist setup — existing small product

Работай только в папке `<ABSOLUTE_CELL_PATH>` и сначала перейди в неё. Не открывай соседние benchmark-ячейки, управляющий репозиторий, measured prompts, evaluator или evidence прежних серий.

Это подготовка метода и исходного канона существующего продукта до позднего изменения. Hosted project и repository connection уже созданы организатором. Используй только project-local инструкции, файлы и MCP. Browser/UI, создание hosted project, перевыпуск connection, owner-release через UI и просьбы человеку открыть UI запрещены. Если project-local MCP не готов, остановись и точно опиши setup defect.

Проверь authenticated identity, `connection_ready`, правильный project context, отсутствие pending sync и запрещённых legacy project IDs. Изучи только фактический код, tests и исходную документацию этой папки. Подготовь полный и непротиворечивый Prist canon существующего продукта, достаточный для обычной поздней разработки. Не создавай требований будущего изменения и не пытайся его угадать.

Не меняй product source code и tests. Допустимы method/workflow/configuration files, specs и canonical documents о текущем продукте, а также безопасные setup receipts без credentials. Доведи snapshot до `current` и diagnostics до нуля через project-local MCP. Не оставляй active WorkItem, active run или pending sync.

Проверь, что Git remote отсутствует, credentials не tracked, repository clean после setup commit и тот же commit работает в отдельном clean worktree через project-local MCP без browser/UI. В финале перечисли readiness, hosted project ID, HEAD/tree, canon inventory, diagnostics, pending sync, проверки и любые ограничения. Не копируй credential или полные tool payloads в ответ.
