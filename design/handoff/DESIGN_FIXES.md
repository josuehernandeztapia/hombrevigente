# DESIGN_FIXES — ronda 2 (aplicar en Claude design, luego re-exportar y reemplazar)

> Estos 6 fixes **faltan** en la fuente (Claude design). El export `.jsx` de esta carpeta lo confirma.
> Flujo: **(1)** aplicar en Claude design → **(2)** re-exportar → **(3)** sobrescribir los `.jsx`/HTML de esta carpeta → **NO** tocar los `.md` (COMPLIANCE, Inventario, este archivo).
> Find→replace literal. Verificado contra el export 2026-06-08.

---

## 1 · `hv-data.jsx` — Wolverine → nombre clínico (id + name + copy)
Líneas ~72–75. Cambia el objeto completo del stack:

**ANTES**
```js
  { id:'wolverine', name:'Wolverine Stack', focus:'Recuperación',
    tag:'Reparación estructural y nerviosa',
    items:['BPC-157','TB-500','Goralatide'],
    why:'Reparación de tejido y nervio — tu ciática es el objetivo #1.' },
```
**DESPUÉS**
```js
  { id:'reparacion', name:'Protocolo magistral de reparación', focus:'Recuperación',
    tag:'Reparación estructural y nerviosa',
    items:['BPC-157','TB-500','Goralatide'],
    why:'Reparación de tejido y nervio tras lesión o sobrecarga.' },
```
> Arregla 3 cosas: nombre "Wolverine" (posicionamiento), `id` de datos, y la fuga del Caso #1 ("tu ciática es el objetivo #1").

### 1b · `hv4-av2.jsx` — actualizar la referencia al id (línea 4)
**ANTES** `const RX = STACKS.find(s => s.id === 'wolverine');`
**DESPUÉS** `const RX = STACKS.find(s => s.id === 'reparacion');`
> Si no cambias esto, la pantalla Av.2 quedará en blanco (no encuentra el stack).

---

## 2 · `hv-data.jsx` — "ciática" → genérico (otras 2 ocurrencias)
**Línea ~48**
`meta:'Energía · piel · ciática · composición',` → `meta:'Energía · piel · recuperación · composición',`

**Línea ~104**
`meta:'Energía, ciática, ánimo, descanso',` → `meta:'Energía, recuperación, ánimo, descanso',`
> No nombrar condiciones específicas (COMPLIANCE §2). Con el fix #1, quedan 0 "ciática".

---

## 3 · `hv-data.jsx` — gatear stacks de péptidos a Av.2 (routing data-driven)
Los 3 stacks recomendados (`glow`, `reparacion`, `metabolic`) contienen péptidos Rx → **nunca** deben caer en el checkout Av.1 sin receta. Hazlo explícito en el dato para que el dev rutee por campo, no por suposición. Agrega `av:'av2'` a `reparacion` y `metabolic`:

```js
  { id:'reparacion', name:'Protocolo magistral de reparación', focus:'Recuperación', av:'av2',
    ... },
  { id:'metabolic', name:'Metabolic Longevity Stack', focus:'Longevidad', av:'av2',
    ... },
```
> El "Stack Vigente" de suplementos (NMN·Omega-3·Creatina·Vit D3+K2·Magnesio, ~línea 307+) sí es Av.1 — ese no se toca. Regla: cualquier stack con un item Av.2 → se muestra solo detrás del gate médico (teleconsulta), no en el checkout `av1`.

---

## 4 · `hv-data.jsx` — GHK-Cu tópico vs inyectable
En el `glow` stack (~línea 70), el GHK-Cu cosmético es tópico (Av.1); el inyectable es Av.2. Distínguelo:
`items:['GHK-Cu','NMN','Resveratrol'],` → `items:['GHK-Cu tópico','NMN','Resveratrol'],`
> El GHK-Cu **inyectable** solo aparece en listas Av.2.

---

## 5 · WhatsApp — "Juan" → `{nombre}` (merge field)
`hv-data.jsx`, líneas ~354, 373, 380. El brief pide merge field, no nombre hardcodeado:

- `'¡Listo, Juan! Tu Escaneo Vigente está hecho. 👇'` → `'¡Listo, {nombre}! Tu Escaneo Vigente está hecho. 👇'`
- `'Han pasado 12 semanas, Juan. Toca tu re-test trimestral. 🔬'` → `'Han pasado 12 semanas, {nombre}. Toca tu re-test trimestral. 🔬'`
- `'Te extrañamos, Juan. Llevas 2 semanas sin check-in...'` → `'Te extrañamos, {nombre}. Llevas 2 semanas sin check-in...'`
> Le comunica al dev que es plantilla con variable (alinea con KICKOFF M3).

---

## 6 · ™ — quitar de "Índice Vigente", reservar para "Hombre Vigente™"
`hv2-screens.jsx`:
- **Línea ~34** `Índice Vigente™` → `Índice Vigente`
- **Línea ~314** `title="Tu Índice Vigente™"` → `title="Tu Índice Vigente"`

> "Índice Vigente" **no** es la marca registrada y **el modelo aún no está construido/validado** (COMPLIANCE §0). El ™ va sobre **"Hombre Vigente™"**, y solo en el lockup de marca (logo/landing/footer), no dentro del header de chat ni en el nombre del producto.
> **Extra (recomendado):** mientras el modelo no exista, etiqueta los scores (68/100, 64/100) como **"ejemplo · modelo en validación"** en la UI del informe (pantalla 06).

---

## Después de aplicar (verificación)
Re-exporta y, sobre el export nuevo, debe dar **0** en todo:
```bash
grep -ciE 'wolverine'  hv-data.jsx hv4-av2.jsx   # → 0
grep -ciE 'ci.tica'    hv-data.jsx               # → 0
grep -oiE 'Índice Vigente™' hv2-screens.jsx | wc -l  # → 0
grep -ciE 'Juan'       hv-data.jsx               # → 0
```
Y confirma que `reparacion`/`metabolic` tienen `av:'av2'` y que la pantalla Av.2 (`hv4`) sigue renderizando con el nuevo id.
