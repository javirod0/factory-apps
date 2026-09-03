# eval.md — antes de pedir aprobación

Cualquier FAIL se corrige antes de enviar.

## Fuentes de verdad
- [ ] Leí el design system, la marca y la spec del flujo antes de tocar el fichero.
- [ ] Si algo faltaba o se contradecía, paré y pregunté en vez de asumir.
- [ ] El design system se actualizó **antes** de construir pantallas, no después.

## Scripting
- [ ] Ningún `throw` dentro de un script de Figma.
- [ ] Ningún `fontName` mutado sobre un TextStyle con instancias vinculadas.
- [ ] Fuentes probadas con `loadFontAsync` en try/catch antes de usarse.
- [ ] Verifiqué leyendo del documento, no confiando en la escritura.

## Construcción
- [ ] Auto layout en todo lo que contiene contenido variable.
- [ ] Nada duplicado que debiera ser componente.
- [ ] Nombres con forma de código, sin "Frame 47".
- [ ] Estados vacío, de carga y de error diseñados, no solo el camino feliz.
- [ ] Ninguna altura fija sobre contenedor de contenido variable.

## Auditoría — ejecutada y reportada
- [ ] Sin solapamientos no intencionados
- [ ] Sin roturas de margen ni de safe area
- [ ] Sin texto recortado por padre de altura fija
- [ ] Sin colores ni tipografías hardcodeadas donde existe estilo de sistema
- [ ] Sin pantallas accidentalmente duplicadas

## Copy
- [ ] Sin redundancia dentro de la pantalla
- [ ] Sin explicaciones dobladas entre pantallas adyacentes
- [ ] Sin glifos decorativos sin significado
- [ ] Nada que se lea como relleno generado

## La petición de aprobación
- [ ] Digo qué construí, pantalla por pantalla.
- [ ] Digo qué decisiones tomé que la spec no dictaba, y por qué.
- [ ] **Hago una pregunta concreta**, no "¿qué te parece?".
- [ ] Incluyo el resultado de la auditoría.
- [ ] Digo qué no hice y por qué.
- [ ] Emití `waiting.started` con `waiting_on: po`.

## Límites
- [ ] No decidí dirección de producto por mi cuenta.
- [ ] No di nada por terminado sin aprobación humana.
- [ ] Si detecté que la spec lleva a un mal resultado, lo dije en vez de
      construirlo en silencio.
