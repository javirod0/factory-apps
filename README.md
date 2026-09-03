# factory

Plataforma reutilizable para construir productos móviles con agentes.

Contiene agentes, skills, plantillas, workflows de CI y observabilidad. **No contiene conocimiento de ningún producto concreto.**

---

## La regla

> La plataforma nunca importa nada de producto. El producto configura la plataforma mediante contratos declarativos.

**Test:** si abres cualquier archivo de este repo y encuentras el nombre de un producto, está mal.

El conocimiento de producto vive en el repo del producto, bajo `product/`, y llega aquí en tiempo de ejecución a través de `product.manifest.yaml`.

---

## Método

La reutilización no se diseña, se extrae.

No creamos abstracciones para casos que no existen. Construimos un producto real con separación estricta, y lo que sobreviva intacto cuando llegue el segundo es plataforma por demostración, no por decreto.

---

## Estructura

```
agents/         Definiciones de agentes. Rol y dominio, sin producto.
skills/         Skills propias, formato Agent Skills.
templates/      Plantillas de documentos canónicos.
workflows/      GitHub Actions reutilizables.
observability/  Esquema de eventos y cockpit.
config/         Configuración de herramientas de terceros.
scripts/        Bootstrap de un producto nuevo.
INTERVENTION_LOG.md
```

---

## Reglas para escribir skills

**1. La descripción es el disparador.**
El "cuándo usar" va siempre en la descripción del `SKILL.md`, nunca en el cuerpo. El estándar solo carga nombre y descripción al arrancar; el cuerpo no existe hasta que la skill ya se ha disparado. Una descripción vaga es una skill que no se activa jamás.

**2. Autoverificación obligatoria.**
Toda skill que produzca contenido incluye `eval.md` con checks pass/fail que la propia skill aplica a su salida antes de devolverla.

**3. Revelación progresiva.**
`SKILL.md` corto. El detalle va en `references/`, que se carga solo cuando hace falta.

---

## Pipeline

Un dueño por fase.

```
brainstorm             Superpowers    fase de idea
constitution           Spec Kit       una vez
specify → plan → tasks Spec Kit       artefactos revisables
analyze                Spec Kit       puente antes de implementar
implementar            Superpowers    TDD, review, worktrees, verification
UAT humano → release
```

**Descartado de Superpowers:** `/write-plan` y `/execute-plan` — duplican `plan` y `tasks`, y el plan debe ser artefacto revisable en el repo.

**Descartado de Spec Kit:** sus artículos I y II (toda feature como librería, toda librería con CLI). Incompatibles con Expo y con un monolito modular. Los sustituye el preset de `config/`.

---

## Observabilidad

Todo agente emite eventos. **Ningún agente se considera terminado si no los emite** — es parte de la definición de "hecho" para la plataforma, igual que los tests lo son para el producto.

Ver `observability/EVENT_SCHEMA.md`. El cockpit es un archivo HTML sin servidor.

---

## Cómo se consume

Desde el repo de un producto, versionado:

```bash
git submodule add https://github.com/javirod0/factory .factory
git -C .factory checkout v0.1.0
```

El producto fija una versión. Una mejora de plataforma no rompe el producto a mitad de slice.

---

## Cómo aprende

Dos bucles, ambos obligatorios:

1. **Cada bug encontrado a mano que una regla podría haber cazado se convierte en regla.**
2. **Cada fallo que pilla un humano genera entrada en `INTERVENTION_LOG.md`.**

Sin estos bucles, la plataforma se queda en fuerza de día uno mientras el código crece.

---

## Estado

Iteración 0. Lo que hay:

- [x] Agente de seguridad, con skill y workflow de CI
- [x] Agente de diseño, con skill de prototipado en Figma
- [x] Esquema de eventos y cockpit
- [x] Decisiones de plataforma y registro de herramientas en `docs/`
- [ ] Emisor de eventos ← siguiente
- [ ] Agentes: mobile-platform, database, api, release
- [ ] Preset de Spec Kit
- [ ] Plantillas de documentos
