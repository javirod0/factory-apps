# Esquema de eventos — observabilidad de la fábrica

**Capa:** plataforma. Sin conocimiento de producto.

---

## Por qué esto va antes que el dashboard

Un cockpit no se construye sobre una herramienta, se construye sobre datos. Ninguna de las preguntas del PO —qué agente pasó qué a quién, cuánto costó, cuánto lleva bloqueado, quién está esperando a quién— tiene respuesta hoy porque **los agentes no emiten esa información**.

La instrumentación es lo caro de acertar y lo barato de hacer. La vista es lo contrario. Por eso el esquema primero.

**Regla:** ningún agente se considera terminado si no emite sus eventos. Es parte de la definición de "hecho" para la plataforma, igual que los tests lo son para el producto.

---

## Formato

Un evento por línea, JSON, append-only. `factory/observability/events.jsonl` en `tovu`, commiteado al repo.

Por qué JSONL en git y no una base de datos: con dos personas, cero infraestructura que mantener, historial versionado gratis, y `grep` funciona. Cuando duela, se migra a SQLite. No antes.

## Campos comunes

Todo evento lleva:

```json
{
  "ts": "2026-08-24T09:14:03Z",
  "event": "<tipo>",
  "run_id": "r_01H...",
  "task_id": "T-142",
  "slice": "save-for-myself",
  "phase": "implement",
  "actor": "implementer",
  "actor_type": "agent"
}
```

| Campo | Valores |
|---|---|
| `run_id` | Identificador de una ejecución de agente. Agrupa todos sus eventos. |
| `task_id` | Tarea del board. Enlaza con GitHub Projects. |
| `phase` | `brainstorm` · `specify` · `plan` · `tasks` · `analyze` · `implement` · `review` · `uat` · `release` |
| `actor` | Nombre del agente, o `po` / `designer` |
| `actor_type` | `agent` · `human` |

---

## Tipos de evento

### `run.started` / `run.finished`

Delimitan una ejecución. `run.finished` es el que trae coste.

```json
{"event":"run.started","run_id":"r_01H","task_id":"T-142","actor":"implementer",
 "model":"claude-opus-5","input":"tasks.md#T-142"}

{"event":"run.finished","run_id":"r_01H","task_id":"T-142","actor":"implementer",
 "outcome":"success",
 "duration_s":412,
 "tokens":{"input":184300,"output":12400,"cache_read":920000},
 "cost_usd":2.87,
 "files_changed":7}
```

`outcome`: `success` · `failed` · `blocked` · `abandoned`

**Coste por agente sale de aquí.** Ver "Pendiente de verificar" al final.

### `task.state_changed`

La base del kanban y de los tiempos por estado.

```json
{"event":"task.state_changed","task_id":"T-142","from":"in_progress","to":"in_review",
 "actor":"implementer","time_in_previous_s":3840}
```

Estados: los del blueprint §52. `time_in_previous_s` se calcula al emitir, para que el dashboard no tenga que reconstruirlo.

### `handoff`

**El evento que responde a "flujo de tareas entre agentes".**

```json
{"event":"handoff","task_id":"T-142","from_actor":"implementer","to_actor":"reviewer",
 "reason":"implementation complete, tests green","artifact":"PR #38"}
```

Un handoff a un humano (`to_actor: "po"`) es también un `waiting.started`. Emítelos ambos.

### `waiting.started` / `waiting.ended`

**El evento más valioso del esquema.** Responde a "cuándo esperan mi respuesta y cuándo la del designer".

```json
{"event":"waiting.started","task_id":"T-142","waiting_on":"po",
 "question":"¿Aceptamos el riesgo de S3 o rehacemos la policy?",
 "gate":"risk_acceptance","blocking":true}

{"event":"waiting.ended","task_id":"T-142","waiting_on":"po",
 "waited_s":68400,"resolution":"rehacer"}
```

`waiting_on`: `po` · `designer` · `agent:<nombre>` · `external`

**Si el producto no tiene diseñador humano**, las aprobaciones de diseño van a
`po` con `gate: design_approval`. Ese contador pasa a ser el más importante del
cockpit: el PO se convierte en el único humano del bucle de diseño, y si la
cifra sube, la fábrica está parada en una persona.

En un equipo de dos personas, el tiempo agregado en `waiting_on: po` es casi siempre la mayor fuente de retraso del proyecto, y casi nadie lo mide. Si esta cifra sube, el cuello de botella eres tú, y conviene saberlo antes de culpar a los agentes.

### `blocked` / `unblocked`

Distinto de `waiting`: waiting es esperar una decisión, blocked es no poder avanzar.

```json
{"event":"blocked","task_id":"T-142","actor":"implementer",
 "kind":"dependency","detail":"share extension spike sin resolver",
 "blocked_by_task":"T-101"}
```

`kind`: `dependency` · `spec_gap` · `tooling` · `external` · `unclear_requirement`

`spec_gap` y `unclear_requirement` son señal directa para el `INTERVENTION_LOG`: la spec no era suficiente.

### `gate.evaluated`

```json
{"event":"gate.evaluated","task_id":"T-142","gate":"security_review",
 "result":"blocked","severity":"HIGH","detail":"C1: policy UPDATE sin SELECT"}
```

`gate`: `tests` · `security_review` · `code_review` · `design_qa` · `design_approval` · `uat` · `analyze`

### `intervention`

Emitido cuando un humano tiene que meter mano. **Es el output principal del proyecto.**

```json
{"event":"intervention","task_id":"T-142","actor":"po",
 "what_failed":"agente de mobile no supo configurar el App Group",
 "should_have_been":"mobile-platform",
 "gap_type":"skill",
 "minutes_spent":45}
```

`gap_type`: `skill` · `roster` · `spec` · `tooling`

Esto alimenta `INTERVENTION_LOG.md` automáticamente en vez de depender de que alguien se acuerde de escribirlo.

---

## Preguntas del PO → datos

| Pregunta | Se responde con |
|---|---|
| Flujo de tareas entre agentes | `handoff` — grafo actor→actor |
| Estado de las tareas | último `task.state_changed` por tarea |
| Kanban | agrupación por estado actual |
| Bloqueos | `blocked` sin `unblocked` |
| Tiempos | `time_in_previous_s`, `duration_s`, `waited_s` |
| Consumo por agente | suma de `cost_usd` agrupada por `actor` |
| Fases | campo `phase` |
| **Qué espera mi respuesta** | `waiting.started` con `waiting_on: po` sin cerrar |
| **Qué espera al designer** | ídem con `waiting_on: designer` |
| Salud de la fábrica | ratio de `intervention` por slice, tendencia |

---

## Emisión

Un helper en `factory/observability/emit.py`, invocado por hooks del harness y por la CI. No debe ser trabajo manual del agente: lo que depende de que un agente se acuerde, no ocurre.

Puntos de emisión:
- Hook de inicio y fin de sesión del harness → `run.*`
- Comando de cambio de estado → `task.state_changed`, `handoff`
- CI → `gate.evaluated`
- Comando explícito del humano → `intervention`, `waiting.ended`

---

## Vista

`factory/observability/cockpit.html` — archivo único, sin servidor, lee `events.jsonl`.

Empieza aquí, no en cinco integraciones. Cuando el archivo se quede corto sabrás exactamente qué te falta, que es información que hoy no tienes.

---

## Pendiente de verificar — bloquea "coste por agente"

**No está confirmado cómo obtener tokens y coste por ejecución** desde el harness. Es el único campo del esquema que depende de algo que no controlamos.

Opciones a comprobar el lunes, por orden de preferencia:
1. El harness expone uso por sesión en un hook de fin.
2. Un log local de sesión con conteos de tokens.
3. La API del proveedor, con uso agregado por clave — permite separar por agente si cada agente usa su propia clave.
4. Estimación por conteo de caracteres. Último recurso: sirve para tendencias, no para cifras.

**Si ninguna funciona limpiamente, la opción 3 con una clave por agente es la que garantiza el dato**, a costa de gestionar varias claves. Decidirlo antes de escribir el emisor.
