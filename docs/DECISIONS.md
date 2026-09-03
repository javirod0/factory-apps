# Decisiones de plataforma

**Capa:** plataforma. Sin conocimiento de producto.
**Fecha:** 21 de agosto de 2026

Decisiones que aplican a cualquier producto construido con esta fábrica. Las decisiones específicas de un producto viven en el repo de ese producto.

---

## Método

La segunda app es hipotética. Por tanto: **la reutilización no se diseña, se extrae.**

Construimos un producto real con separación estricta. Lo que sobreviva intacto cuando llegue el segundo es plataforma por demostración, no por decreto. No se crean abstracciones para casos que no existen.

---

## Costura plataforma ↔ producto

**Regla:** la plataforma nunca importa nada de producto; el producto configura la plataforma mediante contratos declarativos.

### 1.1 Los agentes no conocen el producto
Test: si abres un agente y encuentras "el producto", está mal.

### 1.2 Reglas de escritura de skills
- **Descripción = disparador.** El "cuándo usar" va siempre en la descripción del `SKILL.md`, nunca en el cuerpo. El estándar solo carga nombre y descripción al arrancar.
- **Autoverificación.** Toda skill que produzca contenido lleva `eval.md` con checks pass/fail sobre su propia salida.

### 1.3 Reparto de documentos

**Plataforma (`factory/templates/`):** `CONSTITUTION.template.md` (proceso), `AGENTS.md`, `AI_IMPLEMENTATION_GUIDE.md`, `TEST_STRATEGY.md`, `CI_CD_SPEC.md`, `SECURITY_SPEC.md`, `OBSERVABILITY_SPEC.md`

**Producto (`<producto>/product/`):** `PRODUCT.md`, `PRODUCT_SPEC.md`, `BRAND.md`, `DESIGN.md`, `VOICE.md`, `DATABASE_SPEC.md`, `API_SPEC.md`, `RLS_PRIVACY_SPEC.md`, `SCORING_SPEC.md`, `STATE_MACHINES.md`, `UX_FLOWS.md`, `ANALYTICS_SPEC.md`, `TEST_CASES.md`, `THREAT_MODEL.md`, `LEGAL_SPEC.md`, `CONSTITUTION.md` (producto)

La CONSTITUTION se parte:

| Proceso (plataforma) | Producto (el producto) |
|---|---|
| Tests obligatorios | |
| RLS desde primera migración | Permisos a nivel de item |
| ADR para decisiones materiales | Feedback negativo privado |
| Agentes sin secretos de producción | No leaderboard |
| No features sin spec | No monetización en MVP |
| Gates humanos para UX/UAT | URL de origen siempre preservada |
| Review independiente obligatorio | Organización IA ≠ consentimiento de personalización |
| Hallazgos de seguridad no anulables | Enrichment no bloquea el share |

### 1.4 El manifiesto
`product.manifest.yaml` — único archivo que la plataforma lee del producto. Declara nombre, stack, rutas a docs, gates activos, quién aprueba qué, entornos.

---

## Repositorios

**Dos repos.**

```
factory/                      <producto>/
  agents/                       product.manifest.yaml
  skills/                       product/
  templates/                    apps/mobile/     (Expo)
  workflows/                    apps/web/        (Next.js)
  config/                       services/api/    (FastAPI)
  scripts/                      services/worker/ (ARQ)
  INTERVENTION_LOG.md           supabase/migrations/
                                adr/
```

`factory` se consume versionado. `<producto>` fija una versión.

**Por qué:** la separación física *es* el mecanismo de disciplina. En un monorepo aparece un import cruzado en tres semanas y nadie lo nota.

---

## Pipeline — decisión cerrada

Spec Kit y Superpowers se combinan. Un dueño por fase.

```
brainstorm            (Superpowers)  fase de idea
constitution          (Spec Kit)     una vez
specify → plan → tasks (Spec Kit)    artefactos revisables
analyze               (Spec Kit)     puente antes de implementar
implementar           (Superpowers)  TDD + review + worktrees + verification
UAT humano → release
```

**Descartado de Superpowers:** `/write-plan` y `/execute-plan`. Duplican `plan` y `tasks`. El plan debe ser artefacto revisable en el repo — requisito de visibilidad del PO. Las skills de Superpowers se activan solas independientemente de quién generó el plan.

**Descartado de Spec Kit:** artículos I y II de su constitución (toda feature como librería, toda librería con CLI). Incompatibles con Expo y con un monolito modular. Se sustituyen por el preset propio en `factory`.

**Sin preset, no usar Spec Kit.**

---

## Roster de agentes

### Proceso — siempre activos
Orchestrator · Implementer · Reviewer (modelo distinto al implementer) · Test

### Especialistas

| Especialista | ¿Lunes? |
|---|---|
| Mobile platform | Sí |
| Database & RLS | Sí |
| API | Sí |
| **Security** | Sí — **ya construido**, ver `factory/` |
| Release | Sí — "entregable" es app publicada |
| Infra | Después |
| Design QA | Después |
| Analytics | Después |

### Principios de Karpathy — en `factory/AGENTS.md`, no como plugin
Los LLM hacen suposiciones erróneas sin comprobarlas, no gestionan su confusión, no piden aclaraciones, no presentan tradeoffs, no llevan la contraria. Sobrecomplican e inflan abstracciones.

**El principio operativo:** no le digas qué hacer, dale criterios de éxito. Instrucciones imperativas → objetivos declarativos con bucles de verificación.

### INTERVENTION_LOG
```
| Fecha | Qué falló | Quién intervino | Agente que debía cubrirlo | ¿Skill o roster? |
```

---

## Visibilidad de PO

**Requisito del PO, no negociable:** flujo de tareas entre agentes, estado de tareas, bloqueos, tiempos, consumo por agente, kanban, fases, y qué espera respuesta del PO frente al designer.

### El orden correcto es instrumentación → vista

Nada de eso existe como dato hoy. GitHub Projects no sabe qué agente pasó una tarea a otro, ni cuánto costó, ni cuánto lleva bloqueada — no es limitación de la herramienta, es que **los agentes no emiten esa información**.

La instrumentación es lo caro de acertar y lo barato de hacer. La vista es lo contrario.

→ **`factory/observability/EVENT_SCHEMA.md`** define nueve tipos de evento en JSONL append-only, commiteado al repo. Cero infraestructura.

→ **`factory/observability/cockpit.html`** — archivo único, sin servidor, lee `events.jsonl`.

### Regla de plataforma

**Ningún agente se considera terminado si no emite sus eventos.** Es parte de la definición de "hecho" para la plataforma, igual que los tests lo son para el producto.

### El evento que más importa

`waiting.started` / `waiting.ended` con `waiting_on: po | designer`. En un equipo de dos personas, el tiempo agregado esperando al PO suele ser la mayor fuente de retraso del proyecto, y casi nadie lo mide. Si esa cifra sube, el cuello de botella no son los agentes.

### Capas complementarias

- **GitHub Projects** como board canónico — enlazado por `task_id`.
- **Pestaña Security de GitHub** vía SARIF, sin licencia de Advanced Security.
- **Session replay de PostHog** — uso real del producto.

**Regla dura:** nada llega a "Done" sin build en staging que el PO abra en su móvil.

### ⚠️ Pendiente que bloquea "coste por agente"

No está confirmado cómo obtener tokens y coste por ejecución del harness. Es el único campo del esquema que depende de algo que no controlamos. Cuatro opciones en el esquema; **si ninguna funciona limpiamente, una clave de API por agente garantiza el dato** a costa de gestionar varias claves. Decidir antes de escribir el emisor.


---

## Seguridad — herramientas

El stack de escáneres, el agente y sus fronteras están en `../skills/security-review/` y `../agents/security.md`.

La decisión de plataforma es una: **los hallazgos de seguridad no son anulables por ningún otro agente**, y solo un humano con rol security-owner puede aceptar un riesgo, por escrito y con fecha.

---

## ADRs de plataforma

- Dos repos, `factory` versionado
- Dueño del pipeline: Spec Kit especifica, Superpowers ejecuta
- Esquema de eventos y atribución de coste por agente
- Estrategia de contexto documental
- Karajan descartado en favor de Superpowers
