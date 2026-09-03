# Modelos y esfuerzo

Capa de plataforma. Aplica a cualquier producto de la fábrica.

## Modelo por defecto

`claude-fable-5-1`. Mismo modelo base que Mythos 5.1, distinto nivel de
salvaguardas.

## Enrutado por salvaguardas — qué esperar

Fable 5.1 **permite identificar vulnerabilidades de software**, que es trabajo
defensivo, con alrededor de un 60% menos de intervenciones por sesión que su
predecesor.

Pero sigue redirigiendo a Opus tres categorías: **pentesting, generación de
exploits y escaneo de vulnerabilidades basado en binarios**.

| Trabajo | Dónde corre |
|---|---|
| Revisión de seguridad, triaje de escáneres estáticos | Fable nativo |
| Revisión de políticas de acceso a datos | Fable nativo |
| Pentesting dinámico, exploits con prueba de concepto | → Opus |
| Análisis de binario de aplicación | → Opus |

**No es un error y no degrada el trabajo.** Está documentado aquí para que el
enrutado no sorprenda cuando aparezca.

## Coste — dónde está la palanca

Precios por millón de tokens: entrada 10 $, salida 50 $, **lectura de caché
0,25 $** (un 75% menos que la generación anterior).

Para trabajo altamente agéntico —que es el de esta fábrica— la reducción total
ronda el 45%, porque las lecturas de caché dominan el gasto.

**Consecuencia de diseño: premia el contexto estable entre ejecuciones.**
Reescribir el contexto cada vez desperdicia la parte barata. El esquema de
eventos captura `cache_read` por separado; esa es la cifra a vigilar, no el
total de tokens.

## Esfuerzo por agente

Con esfuerzo bajo o medio, el modelo iguala o supera a la generación anterior a
coste mucho menor. En herramientas de codificación va en alto por defecto.

**No todos los agentes necesitan el mismo esfuerzo.** Propuesta de partida, a
ajustar con datos reales del cockpit:

| Agente | Esfuerzo | Por qué |
|---|---|---|
| Implementer | Alto | Es donde se decide la calidad del código |
| Security | Alto | El coste de un falso negativo es datos de usuarios |
| Reviewer | Alto | Un review superficial es peor que ninguno |
| Mobile platform | Alto | Restricciones no obvias, fallos caros |
| Database | Alto | Las trampas de RLS fallan en silencio |
| API | Medio-alto | |
| Design | Medio | El gate humano corrige |
| Release | Medio | Trabajo de checklist |
| Test | Medio | |
| Orchestrator | Bajo-medio | Descomponer y enrutar, no resolver |
| Documentación, clasificación de tareas | Bajo | |

Registrar `effort` en `run.started` para poder correlacionar esfuerzo, coste y
tasa de fallo. Sin ese dato, ajustar esto es adivinar.

## Retención de datos

Los clientes elegibles pueden operar con **retención cero** hasta que estén
disponibles las salvaguardas empresariales, que guardan los datos en
infraestructura del propio cliente.

Cualquier producto cuya spec de privacidad exija exclusión de entrenamiento
**debe confirmar elegibilidad antes de enviar datos reales**. La exclusión se
verifica en la ruta de código, no solo se documenta.

## Notas

- Es el modelo más robusto a inyección de prompts en benchmark externo hasta la
  fecha. Las defensas del pipeline siguen siendo necesarias; el suelo es más alto.
- Las salidas llevan marca de agua invisible por cumplimiento normativo europeo.
  Sin impacto práctico.
- Las cuentas de API creadas a partir del lanzamiento **no pueden editar el
  contexto previo preservando el transcript de razonamiento**. No afecta a la
  emisión de eventos; sí afectaría a orquestación propia que reconstruya
  conversaciones multi-turno.
