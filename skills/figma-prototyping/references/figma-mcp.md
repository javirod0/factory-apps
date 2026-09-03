# Figma MCP — herramientas y uso

## Qué hace cada herramienta

| Herramienta | Para qué |
|---|---|
| `use_figma` | Crear y editar. Es la que construye. |
| `get_metadata` | Estructura del documento o de un subárbol. Empieza aquí siempre. |
| `get_design_context` | Contexto de un nodo para generar código |
| `get_screenshot` | Ver lo construido. Verificación visual. |
| `get_variable_defs` | Variables y estilos de la selección: color, espaciado, tipografía |
| `get_code_connect_map` | Mapeo nodo Figma → componente de código |
| `create_new_file` | Fichero nuevo |
| `search_design_system` | Buscar componentes, variables y estilos existentes |

## Orden de trabajo

1. `get_metadata` sin nodeId → páginas del documento.
2. `get_metadata` con la página → estructura de esa página.
3. `search_design_system` → qué existe ya antes de crear nada nuevo.
4. `use_figma` → construir.
5. `get_screenshot` → **verificar visualmente**. No des por bueno lo que no has
   mirado.

El paso 5 no es opcional. Un script puede terminar sin error y producir algo
irreconocible.

## Code Connect — la dirección importa

Code Connect mapea nodos de Figma a componentes de código, y la dirección es
código → diseño, no al revés.

Consecuencia práctica: **los componentes deben existir primero en código.**
Cuando existan, nombra los componentes de Figma igual, para que el mapeo sea
obvio.

Si un agente de código solo recibe una captura, gastará tiempo buscando el
componente correcto y, si no lo encuentra, creará uno nuevo desde la imagen.
Nombres consistentes evitan eso.

## Límites conocidos

- El prompting por selección requiere la app de escritorio; el servidor remoto
  necesita enlace a un frame o capa.
- Dev Mode requiere asiento de pago.
- Los scripts corren en el sandbox de Figma: sin red, sin sistema de ficheros.
