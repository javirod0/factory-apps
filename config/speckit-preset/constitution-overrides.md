# Preset de Spec Kit — artículos sustituidos

**Sin este preset, no usar Spec Kit.**

## El problema

La constitución que trae Spec Kit incluye artículos prescritos que asumen una
arquitectura concreta:

| Artículo prescrito | Por qué no aplica |
|---|---|
| Toda feature empieza como librería independiente, sin excepciones | Sin sentido para una app móvil o un monolito modular. Aplicado literalmente por un agente, fragmenta la arquitectura en paquetes que nadie quería. |
| Toda librería expone una interfaz de línea de comandos texto-entra/texto-sale | Igual. Una pantalla no tiene CLI. |

Los artículos IV, V y VI están diseñados para que los defina cada proyecto. Los
dos de arriba no, y son los que hay que sustituir.

## Sustitución

### Artículo I — Cohesión antes que empaquetado

Una feature vive donde su cohesión es mayor. Se extrae a módulo o paquete
reutilizable **cuando exista un segundo consumidor real**, no antes.

Extraer sin segundo consumidor produce abstracciones con forma de su único caso
de uso, y con el coste de mantenerlas.

### Artículo II — Interfaz verificable, no interfaz de línea de comandos

Toda unidad de funcionalidad expone una interfaz **verificable por test
automatizado**. La forma la dicta la capa:

| Capa | Interfaz verificable |
|---|---|
| API | Endpoint con contrato y test |
| Datos | Migración con test multi-usuario |
| Móvil | Componente o módulo con test, y flujo E2E |
| Worker | Job con test de entrada y salida |

Lo que se exige es la verificabilidad, no el formato.

## Lo que se conserva de Spec Kit

Todo lo demás: el flujo `constitution → specify → plan → tasks`, el análisis de
consistencia entre artefactos antes de implementar, y las checklists de calidad
de requisitos.

## Reparto de fases

Spec Kit **especifica**. La ejecución (TDD, review, worktrees, verificación
antes de dar por terminado) pertenece a la capa de ejecución. Un dueño por fase,
sin solapes.

## Límite conocido

Spec Kit lleva de la idea al código, pero **no verifica que la implementación
satisfaga la especificación**, ni cubre la prueba de interfaz de usuario.

El gate de aceptación humano no es opcional: es lo que tapa ese hueco.
