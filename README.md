# factory-apps

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
git submodule add https://github.com/javirod0/factory-apps .factory
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

## Agentes

**Proceso — siempre activos:** orchestrator, implementer, reviewer (modelo
distinto al implementer), test.

**Especialistas de dominio:**

| Agente | Dominio |
|---|---|
| `mobile-platform` | Expo/RN, config plugins, share extensions, deep links, permisos, arranque |
| `database` | Postgres, migraciones, RLS, tests multi-usuario |
| `api` | Contratos, autorización, idempotencia, atomicidad de cupos, síncrono vs background |
| `security` | STRIDE, OWASP, SSRF, inyección de prompts, secretos. **Hallazgos no anulables** |
| `design` | Prototipos en Figma, design system, Code Connect. **Salida no válida sin aprobación humana** |
| `release` | Builds, firma, tiendas, versionado, rollout |

Las dos autoridades asimétricas son inversas a propósito: seguridad no se anula,
diseño no se acepta sin humano.

## Estado

Iteración 0. Listo para usar.

- [x] Seis agentes de dominio definidos
- [x] Skills: `security-review`, `figma-prototyping` (con `eval.md` y referencias)
- [x] Workflow de CI de seguridad
- [x] Esquema de eventos, emisor y cockpit
- [x] Preset de Spec Kit
- [x] Configuración de modelo y esfuerzo por agente
- [x] Decisiones de plataforma y registro de herramientas
- [ ] Plantillas de documentos canónicos
- [ ] Captura de coste por ejecución ← **verificar en el harness**
