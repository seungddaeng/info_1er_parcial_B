# Paint (1er Parcial B)

Aplicación que replica **Paint** desarrollada en **Python** con **Arcade 3.3.2**.
Incluye herramientas de dibujo (lápiz, marcador, spray, borrador, línea, rectángulo, círculo y celdas), paleta de colores con atajos, barra superior con botones, **guardado/carga** del dibujo y utilidades como cuadrícula, deshacer/rehacer y cambio de tamaño de herramienta.

---

## Requisitos

* Windows 10/11
* Python **3.12**
* **uv** (gestor rápido de entornos/paquetes)
* Visual Studio Code (recomendado)

> Versión de Arcade utilizada: **3.3.2**

---

## Instalación y ejecución (desde cero)

1. **Clonar o forkar** el repositorio y abrir la carpeta del proyecto en VS Code.

   ```bash
   git clone https://github.com/seungddaeng/info_1er_parcial_B
   cd info_1er_parcial_B
   ```

2. **Crear** el entorno virtual con **uv** usando Python 3.12:

   ```bash
   uv venv --seed -p 3.12
   ```

3. **Activar** el entorno virtual (Windows):

   ```bash
   .venv\Scripts\activate
   ```

4. **Instalar Arcade 3.3.2**:

   ```bash
   uv pip install arcade==3.3.2
   ```

5. **Ejecutar** la aplicación:

   ```bash
   python main.py
   ```

   * Para **cargar** un dibujo guardado (archivo JSON de trazos):

     ```bash
     python main.py ruta\a\mi\dibujo.txt
     ```

---

## Qué incluye la app

### Barra superior 

* **Izquierda:** botones de herramientas.
* **Centro:** paleta de colores (se organiza en 1, 2 o más filas automáticamente según el espacio disponible).
* **Derecha:** botones de **Guardar (O)**, **Limpiar**, **Deshacer (Z)**, **Rehacer (Y)**, tamaño **− / +**, y **Cuadrícula (G)**.
* La zona de dibujo es **todo el área debajo** de la barra.

### Herramientas implementadas

> Cada herramienta guarda su información en `self.traces` (lista de diccionarios) y se dibuja con primitivas de Arcade.

* **Lápiz (1) – `PencilTool`**
  Trazo continuo fino.
  Dibujo: `arcade.draw_line_strip(puntos, color)`

* **Marcador (2) – `MarkerTool`**
  Igual que lápiz pero con **mayor grosor** (ancho configurable).
  Dibujo: `arcade.draw_line_strip(puntos, color, width)`

* **Spray (3) – `SprayTool`**
  Genera puntos aleatorios alrededor del cursor mientras arrastras.
  Dibujo: `arcade.draw_points(lista_de_puntos, color, size)`

* **Borrador (4) – `EraserTool`**
  **Elimina** trazos que “toca” alrededor del cursor (usa distancia punto–segmento y solapes simples).
  No dibuja un trazo propio; actúa sobre `self.traces`.

* **Línea (5) – `LineTool`**
  Clic para fijar el inicio, arrastra para ver el extremo; suelta para fijar.
  Dibujo: `arcade.draw_line(x1, y1, x2, y2, color, width)`

* **Rectángulo (6) – `RectTool`**
  Clic para esquina inicial, arrastra, suelta para fijar.
  Dibujo: `arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, color, width)`

* **Círculo (7) – `CircleTool`**
  Clic para centro, arrastra para definir el radio, suelta para fijar.
  Dibujo: `arcade.draw_circle_outline(cx, cy, r, color, width)`

* **Celdas (8) – `CellTool`**
  Pinta **cuadrados llenos** “encajados” a una grilla (tamaño de celda configurable).
  Dibujo: `arcade.draw_lrbt_rectangle_filled(...)` + contorno fino.

---

## Controles y atajos

### Herramientas

* **1** Lápiz | **2** Marcador | **3** Spray | **4** Borrador
* **5** Línea | **6** Rectángulo | **7** Círculo | **8** Celdas

### Colores (paleta con atajos)

* **Q** Negro | **A** Rojo | **S** Verde | **D** Azul | **F** Amarillo
* **G** Morado | **H** Naranja | **J** Cian | **K** Rosa | **L** Gris
  *(También puedes seleccionar con clic en los círculos de color de la barra.)*

### Archivo / edición / utilidades

* **O** Guardar dibujo en `dibujo.txt` (JSON).
* **Z** Deshacer (quita el último trazo y lo guarda en pila de rehacer).
* **Y** Rehacer (restaura el último deshecho).
* **G** Mostrar/Ocultar cuadrícula de guía.
* **−** y **=** (teclas menos/igual) para cambiar el **tamaño** de la herramienta activa:

  * **Marcador:** grosor de línea.
  * **Spray y Borrador:** **radio**.
  * **Línea/Rectángulo/Círculo:** grosor del contorno.
  * **Celdas:** tamaño de la **celda** (mínimo 5 px).

### Mouse

* **Clic** en la barra: activa herramientas, colores o botones.
* **Clic** en el lienzo: inicia el trazo/figura o borra (según herramienta).
* **Arrastrar**: continúa el trazo, acumula spray, ajusta la figura.
* **Soltar**: confirma la figura (línea/rectángulo/círculo).

---

## Guardado y carga

* **Guardar** (`O`): serializa `self.traces` a `dibujo.txt` como **JSON**.
* **Cargar** (línea de comandos):

  ```bash
  python main.py ruta\a\mi\dibujo.txt
  ```

  Reconstruye `self.traces` y re-crea instancias de herramientas usadas para poder dibujar todos los trazos.

---

## Estructura del proyecto

```
.
├─ main.py   # Ventana, barra superior (UI), eventos de teclado/mouse, guardado/carga, grid, undo/redo, tamaño de herramienta
└─ tool.py   # Herramientas (Pencil, Marker, Spray, Eraser, Line, Rect, Circle, Cell) y su lógica de dibujado
```

* **Constantes** (arriba de `main.py`): `WIDTH`, `HEIGHT`, `TITLE`, etc.
* **Vista principal**: `class Paint(arcade.View)` con los eventos:

  * `on_draw`, `on_key_press`, `on_mouse_press`, `on_mouse_drag`, `on_mouse_release`, `on_mouse_motion`.
* **UI**: botones y paleta dibujados con primitivas aprendidas en clase:

  * `arcade.draw_lrbt_rectangle_filled/outline`, `arcade.draw_text`, `arcade.draw_circle_filled/outline`, etc.
* **Datos**: `self.traces` es una **lista de diccionarios**. Ejemplos de formato:

  **Lápiz / Marcador**

  ```python
  {"tool": "PENCIL" | "MARKER",
   "color": [R, G, B],
   "trace": [(x0, y0), (x1, y1), ...],
   # en MARKER puede venir "width": entero
  }
  ```

  **Spray**

  ```python
  {"tool": "SPRAY",
   "color": [R, G, B],
   "points": [(x0, y0), (x1, y1), ...]}
  ```

  **Borrador**

  ```python
  # No agrega entradas: elimina elementos de self.traces que colisionan con el radio.
  ```

  **Línea / Rectángulo / Círculo**

  ```python
  {"tool": "LINE" | "RECT" | "CIRCLE",
   "color": [R, G, B],
   "start": (x1, y1),
   "end": (x2, y2),
   "width": entero}
  ```

  **Celdas**

  ```python
  {"tool": "CELL",
   "color": [R, G, B],
   "xy": (x, y),     # esquina inferior izquierda, alineada a la grilla
   "size": entero}   # tamaño de celda
  ```

---

## Detalles de implementación

* **Barra superior adaptable**: los **botones de color** se distribuyen automáticamente en varias columnas/filas según el espacio disponible entre las herramientas (izquierda) y los controles (derecha).
* **Grid**: se dibuja como líneas finas claras cuando está activo (`G`) o si la herramienta **Celdas** está seleccionada.
* **Snap**: la herramienta **Celdas** “imanta” todos los clics y arrastres a la grilla de su tamaño de celda.
* **Undo/Redo**: `self.redo_stack` almacena los elementos removidos por deshacer; cualquier acción nueva limpia el redo.
* **Tamaños**: las teclas **− / =** cambian el parámetro relevante de la herramienta activa (grosor/radio/celda).
---

## Ejecución rápida

```bash
uv venv --seed -p 3.12
.venv\Scripts\activate
uv pip install arcade==3.3.2
python main.py (o Run Python File en VS Code)
# o con carga de un dibujo anterior:
python main.py dibujo.txt
```


---
