# Registro de herramientas evaluadas

**Capa:** plataforma. Este registro es reutilizable: la evaluación de una herramienta no caduca al cambiar de producto.

*Nota: la elección concreta de stack para un producto se declara en su `product.manifest.yaml`, no aquí. Aquí está el porqué de cada veredicto.*

**Regla:** todo repo evaluado deja rastro escrito de *por qué* se descartó. Un repo rechazado sin razón se vuelve a proponer en dos meses.

Complementa la tabla de evaluación de herramientas del blueprint del producto correspondiente.

---

## Parte A — Evaluados fuera del registro original

Registro vivo. Cada entrada lleva veredicto, razón y fecha de reevaluación.

## `block/buzz` — investigación, no adoptar

**URL:** https://github.com/block/buzz · **Licencia:** Apache 2.0 · **Autor:** Block (los de Goose) · **Evaluado:** 21 ago 2026

**Qué es:** workspace autoalojable donde humanos y agentes comparten las mismas salas. Relay Nostr en Rust: cada mensaje, reacción, paso de workflow, aprobación de review y evento de git es un evento firmado en un único log. Los agentes son miembros con claves propias, membresías propias y audit trail propio.

**Por qué se evaluó:** es esencialmente el Project Cockpit de `BLUEPRINT §54` ya construido, con gates de aprobación y trazabilidad de agentes.

**Veredicto: no adoptar ahora.**

| Razón | Detalle |
|---|---|
| Duplica el control plane | Mismo motivo por el que se rechazaron Hermes y LobeHub. Buzz aspira a sustituir chat, forge, bots, dashboards de CI, release y búsqueda. GitHub Projects ya es el board canónico (§5). |
| Coste de operación | Rust + Postgres + Redis + S3/MinIO autoalojado. Con dos personas, es un segundo producto que operar. |
| Lo que más interesaría no está listo | Gates de aprobación de workflow "en proceso"; push notifications en la columna de código pendiente. |
| No es mobile | No aporta nada a Expo, share extensions, EAS ni App Store. |

**Reevaluar:** iteración 2, si se decide construir el Cockpit o si el equipo crece.

**Lo que sí se adopta hoy, sin adoptar el producto:**

1. **Su estructura de documentación como referencia.** `AGENTS.md`, `ARCHITECTURE.md`, `CLAUDE.md`, `TESTING.md`, `GOVERNANCE.md`, `SECURITY.md`, `RELEASING.md` + docs de visión separados. Es el set canónico de §1.2 en un repo real y mantenido. Apache 2.0 permite copiar los patrones.
2. **Skills multi-harness.** Mantienen `.claude/skills`, `.codex/skills`, `.goose/skills` y `.agents/skills` en paralelo. Si `factory` va a servir a más de un harness — y Superpowers y ACP apuntan a que sí — este patrón resuelve una decisión que había que tomar igualmente.

→ Ver tarea 13 en §8.

---

## Parte B — Repos del §27, verificados

Revisión directa de los cuatro que bloquean la estructura de `factory`.

## `agentskills/agentskills` — ✅ confirmado, con matiz

**Licencia:** Apache 2.0 (código) / CC-BY-4.0 (docs). Origen Anthropic, estándar abierto.

Formato: carpeta + `SKILL.md` con frontmatter (nombre y descripción mínimo), más `scripts/`, `references/`, `assets/` opcionales.

**Matiz:** no es una herramienta, es una especificación. "Adoptar" = adoptar el formato, no instalar el repo.

**Restricción de diseño que afecta a todas las skills de `factory`:** revelación progresiva en tres niveles. Solo nombre y descripción cargan al arrancar (~30-50 tokens por skill); el cuerpo carga al dispararse; las referencias solo si hacen falta.

→ **Regla para `factory/skills`:** el "cuándo usar" va SIEMPRE en la descripción, nunca en el cuerpo. Una descripción vaga = skill que no se activa jamás.

## `expo/skills` — ⚠️ adoptar, pero no "intacto"

Oficiales del equipo Expo. Cubren Router, estilos y animaciones, API routes, CI/CD, deployment, dev clients con TestFlight, NativeWind, SwiftUI, Jetpack Compose, data fetching.

**Dos correcciones al plan original:**

1. **No se copian a `factory`.** Se distribuyen vía marketplace de plugin (Claude Code, Codex) o `npx skills add`, instaladas por agente. `factory` documenta cuáles se usan y con qué versión; no las versiona.
2. **Hay frontera gratis/pago.** Las descripciones llevan prefijo de categoría: skills OSS de framework vs. skills de EAS de pago. Verificar de qué lado cae cada una antes de depender de ella.

**Hallazgo importante: no existe skill de share extension.** El mayor riesgo técnico del MVP no tiene cobertura oficial. Refuerza que el Spike A vaya primero y sin asumir ayuda.

## `supabase/agent-skills` — ✅ confirmado sin reservas

Dos skills: `supabase` (general) y `supabase-postgres-best-practices` (query performance, conexiones, esquema, concurrencia, seguridad y RLS, patrones de acceso, monitorización, avanzado).

**Por qué encaja especialmente aquí:** trae checklist de seguridad siempre cargado, no bajo demanda:
- Nunca usar `user_metadata` para autorización — es editable por el usuario. Usar `app_metadata`.
- Nunca exponer `service_role` key en frontend.
- Las vistas saltan RLS por defecto → `security_invoker = true`.
- **UPDATE requiere política de SELECT; sin ella devuelve 0 filas en silencio.**

El último es exactamente el tipo de fallo que `RLS_PRIVACY_SPEC` no puede permitirse.

## `github/spec-kit` — ⚠️ adoptar con preset propio obligatorio

Flujo: `/speckit.constitution` → `specify` → `plan` → `tasks` → `implement`. Más `/speckit.analyze` (consistencia entre artefactos, correr antes de implement) y checklists de calidad de requisitos.

**Conflicto detectado.** La constitución de Spec Kit trae artículos prescritos que chocan con un stack basado en Expo y un monolito modular:

| Artículo prescrito | Problema |
|---|---|
| Toda feature debe empezar como librería independiente, sin excepciones | Sin sentido para una app Expo o un monolito modular FastAPI. Aplicado literalmente por un agente, fragmenta la arquitectura. |
| Toda librería debe exponer CLI texto-entra/texto-sale | Igual. |

**Resolución:** los artículos IV, V y VI están diseñados para que los defina cada proyecto, y existen extensiones, presets y overrides en `.specify/templates/overrides/`.

→ **Decisión: `factory` incluye un preset propio de Spec Kit** que sustituye los artículos incompatibles. Ese preset ES la mitad de plataforma de la costura de §1. Sin él, Spec Kit impone una arquitectura que no es la nuestra.

**Límite conocido:** Spec Kit lleva de idea a código, pero no verifica que la implementación satisfaga la spec, ni dice nada sobre probar la UI. → El gate de UAT humano no es opcional; es lo que tapa ese hueco.



## `manufosela/karajan-code` — ⚠️ spike sí, pero degradar a "acelerador"

**Licencia/autor:** un solo mantenedor (@manufosela). JavaScript vanilla por convicción.

**Qué aporta de valor real:**
- Rol de arbitraje **"Solomon"**: valida los rechazos del reviewer contra las restricciones del proyecto, evitando que bloqueos de estilo detengan el desarrollo. Resuelve un problema real del review independiente obligatorio.
- **Plantillas de rol con override de proyecto** en `.karajan/roles/<role>.md`, más variantes `reviewer-strict` / `reviewer-relaxed` / `reviewer-paranoid`. → Mismo mecanismo que la costura de §1: plantillas en `factory`, overrides en el repo de producto.
- Sin coste de API: usa las suscripciones existentes. Servidor MCP incluido.

**Datos de madurez (duros):**

| Señal | Valor |
|---|---|
| Estrellas | 5 |
| Puntuación de calidad externa | 34/100 — "emergente" |
| Mantenedores | 1 |
| Releases | 57 en 45 días → API inestable |
| Consistencia de docs | Nº de roles varía entre fuentes (22 / 15 / 11) |

**Detalles operativos:**
- SonarQube requiere Docker instalado y corriendo.
- **Telemetría activada por defecto** (versión, SO, comando, duración y tasa de éxito; nunca código). → Desactivar desde el minuto uno con `telemetry: false` en `~/.karajan/kj.config.yml`. La constitución de privacidad lo exige.
- Fijar versión es obligatorio, no recomendable.

**Decisión FINAL (revisada en §9.5): Karajan queda DESCARTADO.** Superpowers cubre la misma propuesta con licencia MIT, 38 contribuidores y distribución oficial. Lo de abajo se conserva como registro del razonamiento.

**Plan B, ya definido (esto faltaba en el blueprint):** los tres conceptos que aporta — plantillas de rol, reviewer con variantes, árbitro de rechazos — son replicables a mano en `factory` en aproximadamente un día. Si el spike falla, se implementan directamente y no se bloquea nada.

## `Graphify-Labs/graphify` — ✅ buena herramienta, timing equivocado

**Licencia:** Apache 2.0. On-device.

Grafo de conocimiento sin embeddings ni vector store. Parseo AST con tree-sitter: determinista, sin LLM, nada sale de la máquina. Cada arista etiquetada `EXTRACTED` (explícita en la fuente) o `INFERRED` (resuelta por graphify). Hook que reconstruye el grafo en cada commit. Detección de "god nodes" y comunidades (Leiden).

**Matiz de privacidad:** solo el **código** es local y gratis. Docs, PDFs, imágenes y vídeo pasan por el modelo del asistente o una API key configurada. → Grafizar los 25 documentos canónicos tiene coste y sale de la máquina. Decidir explícitamente si se grafiza `product/`.

**Corrección de timing:** Graphify da valor sobre una base de código que ya existe. El lunes el repo de producto está vacío; instalarlo entonces es ceremonia.

→ **Mover a slice 3-4**, cuando haya app, API, migraciones y specs que relacionar.

**Nota de método:** las estrellas reportadas varían entre 76k y 108k según el directorio. La popularidad no es criterio verificable aquí; el argumento a favor es técnico.

## `rtk-ai/rtk` — ✅ adoptar, corrigiendo la descripción

Proxy CLI en binario Rust único. 100+ comandos, <10ms de overhead. Filtra y comprime la salida de comandos antes de que llegue al contexto.

Barato, reversible, riesgo cero. Señal de confianza: son honestos con sus propias cifras — advierten de que recortar 90% de salida de bash no equivale a recortar la factura un 90%, y que sus conteos son estimados (bytes/4, sin tokenizador).

**Corrección a §27 del blueprint:** lo describe como "compresión de output/**contexto** para agentes". Sobrevende. RTK comprime **salida de comandos**, no contexto en general.

→ Los 25 documentos canónicos, los specs y el historial de conversación siguen pesando igual. **Si el problema de contexto es documental — y con esta cantidad de specs lo será — RTK no lo resuelve.** Ese problema sigue abierto y necesita otra respuesta (revelación progresiva de skills, specs más cortos, o Graphify más adelante).

---

## Parte C — Diseño y copy

**Hallazgo transversal:** las tres son herramientas **web y anglocéntricas**. El producto es **móvil**. §27 las presentaba como cobertura completa de diseño y copy, y no lo son.

## `pbakaus/impeccable` — ⚠️ solo web, y con colisión de nombres

Premisa idéntica a la del brand brief: los modelos entrenados con las mismas plantillas SaaS producen los mismos tics (Inter para todo, degradados morado-azul, tarjetas anidadas, el icono en cuadrado redondeado sobre cada encabezado).

Aporta 23 comandos con vocabulario compartido (`polish`, `audit`, `critique`, `distill`, `bolder`, `quieter`…) y 59 reglas detectoras deterministas que corren sin LLM ni API key.

**Tres problemas:**

| Problema | Detalle | Acción |
|---|---|---|
| **Colisión de ficheros** | `/impeccable init` escribe `PRODUCT.md` y ofrece `DESIGN.md` — los dos nombres reservados en `<producto>/product/` | Decidir por escrito quién manda **antes** de instalarlo, o sobrescribe la spec |
| **Es herramienta web** | Cobertura: webs, landings, dashboards, componentes, formularios. Reglas deterministas vía CLI y extensión de navegador → en React Native no hay DOM | Usar solo en `apps/web` |
| **Tensión de tono** | Su SKILL.md instruye a actuar como "director de diseño premiado, sin titubeos, soñando a lo grande y audaz" | El brand brief pide contención. La skill empuja al maximalismo por diseño. |

**Veredicto: adoptar solo para web/landing**, con el conflicto de nombres resuelto.

## `nextlevelbuilder/ui-ux-pro-max-skill` — ✅ confirmado; la única que cubre móvil

Detecta el stack y soporta **react-native**, swiftui, flutter y jetpack-compose además de los web. Búsqueda local sobre CSV con Python: sin coste de API.

Cubre estilos, paletas, tipografías, guidelines de UX, iconos, presets de movimiento y tipos de gráfico across 22 stacks.

**Dos avisos:**
- **Tier premium de pago** (uupm.cc): identidad de marca, logo, CIP, arquitectura de tokens ampliada. Verificar que lo necesario está en el lado gratuito antes de depender de ello.
- Las cifras publicadas varían mucho entre fuentes (84 vs 79 estilos, 98 vs 119 guidelines, 97 vs 192 paletas) → churn rápido, **fijar versión**.

**Veredicto de §27 confirmado.** Es el único de los tres que entiende React Native → cubre el hueco que deja Impeccable.

## `petergyang/no-ai-slop` — ✅ útil, con pregunta abierta

Skill estrecha y bien construida. Más allá de quitar patrones, refuerza fundamentos: liderar con el punto, voz activa, desenredar frases, números concretos sobre abstracciones. Devuelve el borrador editado más un "qué cambió".

**Patrón a robar para `factory`:** incluye `eval.md` con checks pass/fail que la skill aplica **a su propia salida**. Autoverificación dentro de la skill.

→ **Regla propuesta:** toda skill de `factory` que produzca contenido lleva su `eval.md`.

**Pregunta abierta — bloqueante para uso en marca:** los patrones son de inglés (contrastes binarios, aperturas de carraspeo, finales de falsa profundidad). La landing y el producto son en español. Algunos traducen, otros no, y no hay evidencia de funcionamiento fuera del inglés.

→ **Probar en español antes de confiarle la voz de marca.**

**Uso correcto según el propio autor:** primer borrador a mano, iteración con IA en las ediciones, pasada manual final. No es un botón de generar copy.



## `obra/superpowers` — ✅ ADOPTAR. Sustituye a Karajan.

**Licencia:** MIT. Marketplace oficial de Claude. 38 contribuidores, activo.

No es una colección de skills: es una metodología. Skills componibles que se activan solas sin invocarlas por nombre.

| Skill | Qué hace |
|---|---|
| `brainstorming` | Refina ideas en bruto mediante preguntas **antes** de escribir código |
| `test-driven-development` | Fuerza RED-GREEN-REFACTOR |
| `using-git-worktrees` | Espacio aislado en rama nueva antes de implementar |
| `requesting-code-review` | Se activa entre tareas, revisa contra el plan, reporta por severidad. **Los críticos bloquean.** |
| `verification-before-completion` | Antes de declarar trabajo terminado |
| `finishing-a-development-branch` | Al completar tareas |

Comandos: `/brainstorm`, `/write-plan`, `/execute-plan`.

**Decisión: Superpowers ocupa el lugar reservado a Karajan.**

| | Karajan | Superpowers |
|---|---|---|
| Propuesta | TDD, review, worktrees, roles | La misma |
| Licencia | — | MIT |
| Mantenedores | 1 | 38 |
| Distribución | git clone | Marketplace oficial |
| Calidad externa | 34/100 "emergente" | Repo de skills más usado |

→ **Cancelar el spike de Karajan.** Se recupera medio día. Lo único distintivo que aportaba era el árbitro "Solomon" (validar rechazos de reviewer contra restricciones del proyecto); si hace falta, se implementa como skill propia en `factory`.

**Telemetría:** opcional (logo del compañero visual de brainstorming carga desde su web con la versión en uso; sin datos de proyecto ni prompt). Desactivar con `SUPERPOWERS_DISABLE_TELEMETRY`. Respeta también los opt-out de Claude Code.

**⚠️ CONFLICTO ABIERTO — necesita ADR antes del lunes:**

Superpowers y Spec Kit traen pipelines que solapan:

```
Spec Kit:     constitution → specify → plan → tasks → implement
Superpowers:  brainstorm → write-plan → execute-plan
```

No puede haber dos dueños del flujo.

**Propuesta a validar:**
- **Spec Kit gobierna la especificación** — `constitution`, `specify`. Artefactos revisables.
- **Superpowers gobierna la ejecución** — `brainstorm` (fase de idea), TDD, review, worktrees, verification.
- **`/speckit.analyze` es el puente** — consistencia entre artefactos antes de implementar.

## `multica-ai/andrej-karpathy-skills` — ✅ "absorber principios" confirmado

Un único CLAUDE.md con cuatro principios derivados de las observaciones de Karpathy sobre fallos de LLM al programar:

- Hacen suposiciones erróneas y siguen sin comprobarlas.
- No gestionan su confusión, no piden aclaraciones, no sacan inconsistencias, no presentan tradeoffs, no llevan la contraria cuando deberían.
- Sobrecomplican, inflan abstracciones, no limpian código muerto.
- Cambian o eliminan código que no entienden suficientemente.

**El cuarto principio es el más útil para el diseño de agentes:** los LLM son excepcionalmente buenos iterando hasta cumplir objetivos concretos. **No le digas qué hacer: dale criterios de éxito.** Transformar instrucciones imperativas en objetivos declarativos con bucles de verificación.

→ Va en `factory/AGENTS.md` como principio escrito, **no como plugin instalado**. Cuatro principios no justifican una dependencia.

---

---

## Parte E — Pendientes

| Repo | Prioridad | Por qué |
|---|---|---|
| Vercel skills, gstack | Cuando toque | "Selectivo" ya implica revisión caso a caso |
| Columna investigación (§27 blueprint) | No urgente | — |
| **ECC** | — | **URL aún sin registrar en §27.** Último pendiente del registro. |

Registro cerrado salvo ECC. `obra/superpowers` (§9.5) y Karpathy skills (§9.5) ya verificados.

**Hueco sin cubrir tras las tres tandas:** no hay ninguna herramienta del registro especializada en **diseño de interfaz nativa móvil** (patrones iOS/Android, HIG, Material). UI UX Pro Max es lo más cercano, pero es multi-stack, no especialista. Si el diseñador lo necesita, se cubre con conocimiento humano, no con skill.


---

## Parte F — Herramientas añadidas fuera del registro §27

Verificadas 21 ago 2026. Detalle completo de la decisión en `docs/DECISIONS.md`.

| Herramienta | Categoría | Veredicto |
|---|---|---|
| **Figma Dev Mode MCP** (oficial) | Diseño → código | **Adoptar.** Code Connect es la costura. Requiere asiento de pago. |
| `GLips/Figma-Context-MCP` (Framelink) | Diseño → código | **Plan B.** Sin Code Connect. |
| `bernaferrari/FigmaToCode` | Diseño → código | **Solo web.** No genera React Native. |
| `VoltAgent/awesome-design-md` | Formato de diseño | **Solo el formato** (9 secciones). Ninguno de los 55 archivos. |
| `mobile-dev-inc/Maestro` | E2E móvil | **Adoptar.** Capa de accesibilidad → la accesibilidad pasa a ser subproducto de la testabilidad. Java 17. |
| `fastlane/fastlane` | Publicación | **Adoptar.** `deliver`, `supply`, `precheck`. Ruby; iOS requiere Mac. |
| `PostHog/skills` + `PostHog/context-mill` | Analytics | **Adoptar.** Primera parte por ambos lados: skill oficial de PostHog + integración EAS CLI oficial de Expo. |
| `expo-localization` + `react-i18next` | i18n | **Adoptar.** De facto estándar. Ojo al polyfill de `Intl`. |
| Semgrep CE · Gitleaks · TruffleHog · Trivy · mobsfscan · `NVIDIA/garak` | Seguridad estática | **Adoptar.** Ver `docs/DECISIONS.md` y `factory/`. |
| `usestrix/strix` | Seguridad dinámica (DAST) | **Adoptar.** Agentes autónomos de pentesting que validan con PoC real. Cubre IDOR, SSRF, lógica de negocio y API — lo que ningún estático alcanza. Web/API, no móvil. Open-core; el CLI es local. Solo staging. |
| `microsoft/SkillOpt` | Evolución de skills | **Solo SkillOpt-Sleep, iteración 2.** Ver abajo. |

### `microsoft/SkillOpt` — veredicto revisado

Hay dos productos dentro del repo.

**El motor de investigación no sirve.** Entrena skills con épocas, learning rates y gates de validación sobre splits de benchmark. Requiere benchmark con verdad de referencia. Para "¿construyó bien el agente la share extension?" no existe ni se va a fabricar.

**SkillOpt-Sleep sí encaja.** Motor de auto-evolución nocturna offline (harvest → mine → replay → consolidate) tras un gate de validación reservado, que revisa sesiones de agentes de codificación y **prepara actualizaciones propuestas de skill para adopción humana**.

Es exactamente lo que le falta al `INTERVENTION_LOG`: convertir sesiones reales en mejoras propuestas, con humano aprobando.

→ **Iteración 2**, cuando haya historial. Cautelas: v0.2.0 muy nuevo; alimenta datos reales de sesión, así que aplica la decisión de proveedor y retención.

### Nota de método

Para categorías con opción oficial, **primera parte gana a estrellas**. Una skill oficial de PostHog o Expo con pocas estrellas se actualiza cuando cambia el producto; una comunitaria con muchas, no necesariamente.

Y las estrellas reportadas por directorios de terceros son poco fiables — para el mismo repo hemos visto cifras que varían entre 76k y 108k. Verificar en GitHub directamente.

---

## Parte G — Quinta tanda

### `trailhq/Graft` — ✅ ADOPTAR. Sustituye a Graphify.

**MIT · 5,1k estrellas · 465 forks · 435 commits · Nanonets**

Capa de contexto: construye un grafo de conocimiento del código como ficheros
markdown enlazados, uno por sistema/API/concepto.

**Por qué gana a Graphify:**

| | Graft | Graphify |
|---|---|---|
| Wiring nativo por harness | Sí, escribe el fichero de instrucción de cada agente | No |
| TS/JSX/TSX + Python full-fidelity | Sí — el stack exacto | Parcial |
| Submódulos | `--follow-submodules` — **es la estructura factory↔producto** | No |
| Benchmark externo | SWE-bench Verified, grader oficial: 33/50 vs 27/50 | No publicado |
| Radio de impacto de un diff | `graft blast`, con markdown para PR y responsables por historial de git | No |

El tier estructural es tree-sitter puro: determinista, sin modelo, sin red, `$0`.
`graft build` no necesita clave. Solo `--deep` llama a un proveedor.

**Cautelas:**
- `graft init` escribe **fuera del repo** (config de Codex a nivel de usuario,
  aplica a todos tus repos) → usar `--no-global`.
- Telemetría anónima opt-out → `DO_NOT_TRACK=1`.
- **Identidad confusa:** el repo es `trailhq/Graft`, los badges apuntan a
  `NanoNets/Graft`, la URL de desarrollo a `NanoNets/context-graph-engine`.
  Confirmar cuál es canónico antes de fijar dependencia.
- 50 instancias de SWE-bench es muestra pequeña y la eligieron ellos. El método
  es honesto (parche aplicado, tests de los mantenedores), la muestra no es
  grande.

**Momento:** final de la slice 1, no día uno. El tier estructural es gratis e
instantáneo, así que no hace falta esperar a la slice 3.

**Sigue sin resolver:** Graft indexa código, **no los 25 documentos canónicos**.
El problema de contexto documental permanece abierto.

### `Graphify-Labs/graphify` — ⬇️ SUSTITUIDO por Graft

Buena herramienta y misma filosofía (tree-sitter, local, sin embeddings), pero
Graft la supera en las cuatro dimensiones que importan aquí: wiring nativo,
submódulos, benchmark verificable y radio de impacto.

Se conserva en el registro por si Graft resulta problemático.

### `mattpocock/skills` — ✅ ADOPTAR SELECTIVAMENTE

**MIT.** Colección personal publicada. ~21 skills. El autor la construyó contra
modos de fallo reales, el más común la desalineación.

**Tomar:**

| Skill | Por qué |
|---|---|
| **`writing-for-agents`** | **La más valiosa.** Escribir skills, AGENTS.md y docs que un agente alcanza por puntero. Es la meta-herramienta de construir una fábrica de skills. Instalar **antes** de escribir los agentes restantes. |
| `diagnosing-bugs` | Bucle de depuración con fases controladas. Nada en el stack cubre diagnóstico. |
| `git-guardrails` | Seguridad de git para agentes. Worktrees no lo cubren. |
| Arquitectura (módulos profundos, lenguaje ubicuo) | Aplicable al monolito modular de FastAPI |

**Descartar por duplicación:** `tdd` (duplica Superpowers), `write-a-prd`
(duplica `specify` de Spec Kit), `grill-me` (solapa `/brainstorm`). Dos skills
compitiendo por el mismo momento es peor que una.

**Cautelas:** opinionado sobre TypeScript/Node — encaja con Expo, valor parcial
en FastAPI. El propio autor avisa de que no está pensada para copiarse en bloque.

**Uso extra:** es la referencia de facto del formato SKILL.md. Contrastar los
SKILL.md propios contra los suyos como control de calidad.

### `totalumlabs/ai-app-builder-open` — ❌ DESCARTADO

**5 estrellas · 3 watchers · 0 forks · sin releases**

Genera apps Next.js full-stack. Tres razones:

1. **Es web, no móvil.** Cero solape con Expo + extensión nativa.
2. **No es plataforma abierta.** El repo es un frontend; hosting, sandboxes, base
   de datos, agentes, dominios y GitHub viven tras la API de Totalum con su
   clave. Cambiaría el stack decidido por un proveedor único de pago.
3. **Dirección contraria.** Se define como no-code, prompt a app desplegada.
   Este proyecto es lo opuesto: specs versionadas, TDD forzado, gates de
   seguridad no anulables. El blueprint ya rechazaba el vibe-coding.

El README es marketing de Totalum tanto como documentación.

### `block/buzz` — criterio de reevaluación afinado

El criterio anterior era vago. El concreto: **revisar cuando se cumplan las dos
condiciones a la vez** —
1. Sus gates de aprobación de workflow estén terminados (hoy en "el pegamento
   aún secándose").
2. Haya más de dos humanos o agentes corriendo en paralelo de forma continua.

**Ventaja del orden actual:** `events.jsonl` es portable. Si Buzz madura, los
eventos migran. Al revés no: empezando en Buzz, el historial vive dentro de Buzz.
