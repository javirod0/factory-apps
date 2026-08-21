# INTERVENTION_LOG

Cada vez que un humano tiene que meter mano, se anota aquí.

**Este registro es el output principal del proyecto.** Cada entrada es un especialista que falta o una skill con un hueco. Sin él, la fábrica acumula parches sin aprender.

Se alimenta de los eventos `intervention` (ver `observability/EVENT_SCHEMA.md`), pero se puede escribir a mano cuando el evento no se emitió.

## Cómo clasificar el hueco

| `gap_type` | Significa | Acción |
|---|---|---|
| `skill` | El agente correcto existía pero no sabía hacerlo | Ampliar o crear la skill |
| `roster` | No existe agente para ese dominio | Crear el especialista |
| `spec` | La spec no cubría el caso | Corregir la spec del producto |
| `tooling` | Faltaba una herramienta o un permiso | Añadir al entorno |

## Registro

| Fecha | Tarea | Qué falló | Quién intervino | Debía cubrirlo | Hueco | Min | Resuelto |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## Revisión

Cuando una entrada genere un cambio en un agente o skill, anotar la fecha del cambio y revisar a las dos semanas si el mismo fallo reaparece. Un fallo que vuelve significa que el arreglo no funcionó.
