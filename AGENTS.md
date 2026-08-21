# AGENTS.md

Contrato de comportamiento para todo agente que opere en esta plataforma. Aplica a cualquier harness.

---

## 1. Objetivos, no instrucciones

Los LLM son excepcionalmente buenos iterando hasta cumplir un criterio concreto. **No le digas a un agente qué hacer: dale criterios de éxito y un bucle de verificación.**

Toda tarea se define con:
- Qué debe ser cierto al terminar.
- Cómo se comprueba, de forma que el agente pueda ejecutarlo él mismo.
- Qué está fuera de alcance.

Una tarea sin criterio verificable no está lista para asignarse.

## 2. Gestiona tu confusión

El fallo más caro no es equivocarse, es **suponer y seguir adelante sin comprobar**.

- Si falta información, pídela. No inventes la suposición más plausible.
- Si la spec se contradice, dilo y para. No elijas una rama en silencio.
- Si hay un tradeoff, preséntalo en vez de resolverlo por tu cuenta.
- Si crees que la instrucción es incorrecta, dilo. Llevar la contraria es parte del trabajo.

Cuando pares por cualquiera de estas razones, emite `blocked` con `kind: spec_gap` o `unclear_requirement`. Ese evento es señal de que la spec falló, no de que tú fallaste.

## 3. Lo mínimo que funcione

- 100 líneas antes que 1000.
- No introduzcas una abstracción hasta el tercer caso real.
- No refactorices lo que no te han pedido tocar.
- Borra el código muerto que dejes tú; no el que te encuentres.

## 4. Cambios quirúrgicos

**No modifiques ni elimines código o comentarios que no entiendas lo suficiente**, aunque parezcan ajenos a la tarea. Si algo estorba y no sabes por qué está ahí, dilo en vez de quitarlo.

El diff debe ser explicable línea a línea.

## 5. Verifica antes de declarar terminado

"Terminado" significa comprobado, no escrito. Ejecuta los tests, mira la salida real, comprueba el criterio de éxito.

Si no pudiste verificar, dilo explícitamente. Nunca presentes como verificado algo que no lo está.

## 6. Emite tus eventos

Ningún trabajo se considera hecho sin sus eventos. Ver `observability/EVENT_SCHEMA.md`.

Como mínimo: `run.started`, `run.finished` con coste, `task.state_changed` en cada transición, `handoff` al pasar trabajo, `blocked` al atascarte, `waiting.started` al necesitar a un humano.

## 7. Nunca secretos de producción

Ningún agente recibe, pide ni almacena credenciales de producción. Trabajas contra staging y contra código fuente.

## 8. Seguridad no es negociable

Los hallazgos del agente de seguridad no son anulables por ningún otro agente ni por presión de calendario. Solo un humano con rol de security-owner puede aceptar un riesgo, por escrito y con fecha.

## 9. Revisión independiente

Quien implementa no revisa. El reviewer corre en un modelo distinto al implementer.

## 10. Nada de producto en la plataforma

Si estás escribiendo un agente, una skill o una plantilla en este repo y necesitas nombrar un producto, para. Ese conocimiento va en el repo del producto y llega por manifiesto.

---

## Definición de "hecho"

- [ ] Criterio de éxito cumplido y verificado ejecutando algo
- [ ] Tests escritos antes, en verde ahora
- [ ] Gates aplicables pasados
- [ ] Eventos emitidos
- [ ] Diff explicable línea a línea
- [ ] Sin secretos, sin código muerto propio, sin TODOs sin dueño
