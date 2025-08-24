import arcade
import json
from typing import Callable, Optional
from tool import PencilTool, MarkerTool, SprayTool, EraserTool, LineTool, RectTool, CircleTool, CellTool

WIDTH = 980
HEIGHT = 640
TITLE = "paint :]"
MARGIN = 14
TOOLBAR_H = 170
TOOL_BTN_W = 140
TOOL_BTN_H = 36
GAP = 10

UI_BG = (245, 245, 245)
UI_SHADOW = (220, 220, 220)
UI_BORDER = arcade.color.DARK_SLATE_GRAY
UI_TEXT = arcade.color.BLACK
UI_MUTED = (70, 70, 70)
CANVAS_BORDER = arcade.color.LIGHT_STEEL_BLUE

PALETTE = [
    ("Negro (Q)", arcade.color.BLACK, arcade.key.Q),
    ("Rojo (A)", arcade.color.RED, arcade.key.A),
    ("Verde (S)", arcade.color.GREEN, arcade.key.S),
    ("Azul (D)", arcade.color.BLUE, arcade.key.D),
    ("Amarillo (F)", arcade.color.YELLOW, arcade.key.F),
    ("Morado (G)", arcade.color.PURPLE, arcade.key.G),
    ("Naranja (H)", arcade.color.ORANGE, arcade.key.H),
    ("Cian (J)", arcade.color.CYAN, arcade.key.J),
    ("Rosa (K)", arcade.color.PINK, arcade.key.K),
    ("Gris (L)", arcade.color.GRAY, arcade.key.L),
]


class Button:
    def __init__(self, x: float, y: float, w: float, h: float, text: str, on_click: Callable[[], None]):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.text = text
        self.on_click = on_click
        self.hover = False
        self.active = False

    def contains(self, px: float, py: float) -> bool:
        return self.x <= px <= self.x + self.w and self.y <= py <= self.y + self.h

    def draw_base(self):
        arcade.draw_lrbt_rectangle_filled(self.x + 2, self.x + self.w + 2, self.y, self.y + self.h, UI_SHADOW)
        fill = (232, 236, 239) if self.active else (230, 230, 230) if self.hover else (224, 224, 224)
        arcade.draw_lrbt_rectangle_filled(self.x, self.x + self.w, self.y, self.y + self.h, fill)
        thick = 3 if self.active else 2
        arcade.draw_lrbt_rectangle_outline(self.x, self.x + self.w, self.y, self.y + self.h, UI_BORDER, thick)

    def draw(self):
        self.draw_base()
        arcade.draw_text(self.text, self.x + 12, self.y + self.h/2 - 8, UI_TEXT, 12)


class ToolButton(Button):
    def __init__(self, x, y, w, h, text, on_click, kind: str):
        super().__init__(x, y, w, h, text, on_click)
        self.kind = kind

    def draw(self):
        self.draw_base()
        arcade.draw_text(self.text, self.x + 12, self.y + self.h/2 - 8, UI_TEXT, 12)
        pad = 6
        icon_w = 40
        left = self.x + self.w - icon_w - pad
        right = self.x + self.w - pad
        mid_y = self.y + self.h / 2
        if self.kind == "pencil":
            arcade.draw_line(left + 6, mid_y, right - 6, mid_y, UI_MUTED, 2)
        elif self.kind == "marker":
            arcade.draw_line(left + 6, mid_y, right - 6, mid_y, UI_MUTED, 8)
        elif self.kind == "spray":
            cx = (left + right) / 2
            cy = mid_y
            sx, sy = cx - 8, cy - 6
            for i in range(12):
                dx = (i % 4) * 4
                dy = (i // 4) * 4
                arcade.draw_point(sx + dx, sy + dy, UI_MUTED, 2)
        elif self.kind == "eraser":
            l = left + 8
            r = right - 8
            t = mid_y + 9
            b = mid_y - 9
            arcade.draw_lrbt_rectangle_filled(l, r, b, t, arcade.color.LIGHT_GRAY)
            arcade.draw_lrbt_rectangle_outline(l, r, b, t, UI_BORDER, 2)


class CircleButton:
    def __init__(self, cx: float, cy: float, r: float, color, name: str, on_click: Callable[[], None]):
        self.cx, self.cy, self.r = cx, cy, r
        self.color = color
        self.name = name
        self.on_click = on_click
        self.hover = False
        self.active = False

    def contains(self, px: float, py: float) -> bool:
        return (px - self.cx) ** 2 + (py - self.cy) ** 2 <= self.r ** 2

    def draw(self):
        ring = 3 if self.active else (2 if self.hover else 1)
        arcade.draw_circle_filled(self.cx, self.cy, self.r, self.color)
        arcade.draw_circle_outline(self.cx, self.cy, self.r, UI_BORDER, ring)
        arcade.draw_text(self.name, self.cx - self.r, self.cy - self.r - 16, UI_MUTED, 11)


class Paint(arcade.View):
    def __init__(self, load_path: Optional[str] = None):
        super().__init__()
        self.background_color = arcade.color.WHITE
        self.tool = PencilTool()
        self.used_tools = {self.tool.name: self.tool}
        self.color = arcade.color.BLUE
        self.traces: list[dict] = []
        self.redo_stack: list[dict] = []
        self.active_shape_index: Optional[int] = None
        self.show_grid = False
        self.grid_cell = 20
        if load_path:
            try:
                with open(load_path, "r", encoding="utf-8") as f:
                    self.traces = json.load(f)
                names = {t.get("tool") for t in self.traces}
                for nm in names:
                    if nm == "PENCIL":
                        self.used_tools[nm] = PencilTool()
                    elif nm == "MARKER":
                        self.used_tools[nm] = MarkerTool()
                    elif nm == "SPRAY":
                        self.used_tools[nm] = SprayTool()
                    elif nm == "ERASER":
                        self.used_tools[nm] = EraserTool()
                    elif nm == "LINE":
                        self.used_tools[nm] = LineTool()
                    elif nm == "RECT":
                        self.used_tools[nm] = RectTool()
                    elif nm == "CIRCLE":
                        self.used_tools[nm] = CircleTool()
                    elif nm == "CELL":
                        self.used_tools[nm] = CellTool()
            except Exception as e:
                print("No se pudo cargar el archivo:", e)
        self.buttons: list[Button] = []
        self.color_buttons: list[CircleButton] = []
        self._build_ui()
        self._sync_active_states()

    def _build_ui(self):
        tools = [
            ("Lápiz (1)", lambda: PencilTool(), "pencil"),
            ("Marcador (2)", lambda: MarkerTool(), "marker"),
            ("Spray (3)", lambda: SprayTool(), "spray"),
            ("Borrador (4)", lambda: EraserTool(), "eraser"),
            ("Línea (5)", lambda: LineTool(), "pencil"),
            ("Rectángulo (6)", lambda: RectTool(), "pencil"),
            ("Círculo (7)", lambda: CircleTool(), "pencil"),
            ("Celdas (8)", lambda: CellTool(cell=20), "pencil"),
        ]
        self.buttons.clear()
        cols = 4
        for i, (label, ctor, kind) in enumerate(tools):
            col = i % cols
            row = i // cols
            x = MARGIN + col * (TOOL_BTN_W + GAP)
            y = HEIGHT - (row + 1) * (TOOL_BTN_H + 8) - 8
            btn = ToolButton(x, y, TOOL_BTN_W, TOOL_BTN_H, label, on_click=lambda c=ctor: self._set_tool(c()), kind=kind)
            self.buttons.append(btn)
        start_x = MARGIN + cols * (TOOL_BTN_W + GAP) + 18
        r = 12
        gap_x = 62
        gap_y = 44
        row_start_y = HEIGHT - TOOLBAR_H + 118
        right_x = WIDTH - MARGIN - 108
        available = (right_x - 16) - start_x
        color_cols = max(1, min(len(PALETTE), int(available // gap_x) + 1))
        self.color_buttons.clear()
        for i, (label, color, _key) in enumerate(PALETTE):
            col = i % color_cols
            row = i // color_cols
            cx = start_x + col * gap_x
            cy = row_start_y - row * gap_y
            cb = CircleButton(cx, cy, r, color, label, on_click=lambda c=color: self._set_color(c))
            self.color_buttons.append(cb)
        ctrl_x = WIDTH - MARGIN - 108
        save_btn = Button(ctrl_x, HEIGHT - TOOLBAR_H + 122, 100, 30, "Guardar (O)", on_click=self._save)
        clear_btn = Button(ctrl_x, HEIGHT - TOOLBAR_H + 86, 100, 30, "Limpiar", on_click=self._clear_canvas)
        undo_btn = Button(ctrl_x, HEIGHT - TOOLBAR_H + 50, 100, 28, "Deshacer (Z)", on_click=self._undo)
        redo_btn = Button(ctrl_x, HEIGHT - TOOLBAR_H + 20, 100, 28, "Rehacer (Y)", on_click=self._redo)
        size_minus = Button(MARGIN + 260, HEIGHT - TOOLBAR_H + 10, 34, 28, "−", on_click=self._size_down)
        size_plus = Button(MARGIN + 298, HEIGHT - TOOLBAR_H + 10, 34, 28, "+", on_click=self._size_up)
        grid_btn = Button(MARGIN + 338, HEIGHT - TOOLBAR_H + 10, 110, 28, "Cuadrícula (G)", on_click=self._toggle_grid)
        self.buttons += [save_btn, clear_btn, undo_btn, redo_btn, size_minus, size_plus, grid_btn]

    def _sync_active_states(self):
        for b in self.buttons:
            if isinstance(b, ToolButton):
                n = self.tool.name
                if "Lápiz" in b.text:
                    b.active = (n == "PENCIL")
                elif "Marcador" in b.text:
                    b.active = (n == "MARKER")
                elif "Spray" in b.text:
                    b.active = (n == "SPRAY")
                elif "Borrador" in b.text:
                    b.active = (n == "ERASER")
                elif "Línea" in b.text:
                    b.active = (n == "LINE")
                elif "Rectángulo" in b.text:
                    b.active = (n == "RECT")
                elif "Círculo" in b.text:
                    b.active = (n == "CIRCLE")
                elif "Celdas" in b.text:
                    b.active = (n == "CELL")
            else:
                b.active = False
        for cb in self.color_buttons:
            cb.active = (cb.color == self.color)

    def _set_tool(self, tool_obj):
        self.tool = tool_obj
        self.used_tools[self.tool.name] = self.tool
        self._sync_active_states()

    def _set_color(self, color):
        self.color = color
        self._sync_active_states()

    def _save(self):
        try:
            with open("dibujo.txt", "w", encoding="utf-8") as f:
                json.dump(self.traces, f)
            print("Guardado en dibujo.txt")
        except Exception as e:
            print("Error al guardar:", e)

    def _clear_canvas(self):
        self.traces = []
        self.redo_stack = []
        self.active_shape_index = None

    def _undo(self):
        if self.traces:
            self.redo_stack.append(self.traces.pop())
            self.active_shape_index = None

    def _redo(self):
        if self.redo_stack:
            self.traces.append(self.redo_stack.pop())

    def _size_down(self):
        if self.tool.name == "MARKER":
            self.tool.width = max(2, self.tool.width - 1)
        elif self.tool.name in ("SPRAY", "ERASER"):
            self.tool.radius = max(2, self.tool.radius - 1)
        elif self.tool.name in ("LINE", "RECT", "CIRCLE"):
            self.tool.width = max(1, self.tool.width - 1)
        elif self.tool.name == "CELL":
            self.tool.cell = max(5, self.tool.cell - 1)

    def _size_up(self):
        if self.tool.name == "MARKER":
            self.tool.width += 1
        elif self.tool.name in ("SPRAY", "ERASER"):
            self.tool.radius += 1
        elif self.tool.name in ("LINE", "RECT", "CIRCLE"):
            self.tool.width += 1
        elif self.tool.name == "CELL":
            self.tool.cell += 1

    def _toggle_grid(self):
        self.show_grid = not self.show_grid

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.KEY_1:
            self._set_tool(PencilTool())
        elif symbol == arcade.key.KEY_2:
            self._set_tool(MarkerTool())
        elif symbol == arcade.key.KEY_3:
            self._set_tool(SprayTool())
        elif symbol == arcade.key.KEY_4:
            self._set_tool(EraserTool())
        elif symbol == arcade.key.KEY_5:
            self._set_tool(LineTool())
        elif symbol == arcade.key.KEY_6:
            self._set_tool(RectTool())
        elif symbol == arcade.key.KEY_7:
            self._set_tool(CircleTool())
        elif symbol == arcade.key.KEY_8:
            self._set_tool(CellTool(cell=20))
        for _label, color, keyc in PALETTE:
            if symbol == keyc:
                self._set_color(color)
        if symbol == arcade.key.O:
            self._save()
        if symbol == arcade.key.Z:
            self._undo()
        if symbol == arcade.key.Y:
            self._redo()
        if symbol == arcade.key.G:
            self._toggle_grid()
        if symbol == arcade.key.MINUS:
            self._size_down()
        if symbol == arcade.key.EQUAL:
            self._size_up()

    def _in_canvas(self, x: int, y: int) -> bool:
        return y < HEIGHT - TOOLBAR_H

    def _snap(self, x: int, y: int) -> tuple[int, int]:
        if self.tool.name != "CELL":
            return x, y
        c = getattr(self.tool, "cell", 20)
        return int((x // c) * c), int((y // c) * c)

    def on_mouse_motion(self, x: int, y: int, dx: int, dy: int):
        for b in self.buttons:
            b.hover = b.contains(x, y)
        for cb in self.color_buttons:
            cb.hover = cb.contains(x, y)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        for cb in self.color_buttons:
            if cb.contains(x, y):
                cb.on_click()
                return
        for b in self.buttons:
            if b.contains(x, y):
                b.on_click()
                return
        if not self._in_canvas(x, y):
            return
        if self.tool.name == "ERASER":
            self.tool.erase_at(self.traces, x, y)
            self.redo_stack.clear()
            return
        if self.tool.name == "SPRAY":
            px, py = self._snap(x, y)
            points = self.tool.make_spray(px, py)
            self.traces.append({"tool": "SPRAY", "color": self.color, "points": points})
            self.redo_stack.clear()
            return
        if self.tool.name in ("LINE", "RECT", "CIRCLE"):
            sx, sy = self._snap(x, y)
            entry = {"tool": self.tool.name, "color": self.color, "start": (sx, sy), "end": (sx, sy), "width": getattr(self.tool, "width", 2)}
            self.traces.append(entry)
            self.active_shape_index = len(self.traces) - 1
            self.redo_stack.clear()
            return
        if self.tool.name == "CELL":
            sx, sy = self._snap(x, y)
            s = self.tool.cell
            self.traces.append({"tool": "CELL", "color": self.color, "xy": (sx, sy), "size": s})
            self.redo_stack.clear()
            return
        sx, sy = self._snap(x, y)
        if self.tool.name == "MARKER":
            self.traces.append({"tool": self.tool.name, "color": self.color, "trace": [(sx, sy)], "width": self.tool.width})
        else:
            self.traces.append({"tool": self.tool.name, "color": self.color, "trace": [(sx, sy)]})
        self.redo_stack.clear()

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if not (buttons & arcade.MOUSE_BUTTON_LEFT):
            return
        if not self._in_canvas(x, y):
            return
        if not self.traces:
            return
        if self.tool.name == "ERASER":
            self.tool.erase_at(self.traces, x, y)
            return
        if self.tool.name == "SPRAY":
            last = self.traces[-1]
            if "points" in last:
                px, py = self._snap(x, y)
                last["points"].extend(self.tool.make_spray(px, py))
            return
        if self.tool.name in ("LINE", "RECT", "CIRCLE"):
            if self.active_shape_index is not None and 0 <= self.active_shape_index < len(self.traces):
                ex, ey = self._snap(x, y)
                self.traces[self.active_shape_index]["end"] = (ex, ey)
            return
        last = self.traces[-1]
        if "trace" in last:
            px, py = self._snap(x, y)
            last["trace"].append((px, py))

    def on_mouse_release(self, x: int, y: int, button: int, modifiers: int):
        if button != arcade.MOUSE_BUTTON_LEFT:
            return
        if self.tool.name in ("LINE", "RECT", "CIRCLE"):
            self.active_shape_index = None

    def on_draw(self):
        self.clear()
        arcade.draw_lrbt_rectangle_filled(0, WIDTH, HEIGHT - TOOLBAR_H + 4, HEIGHT + 4, UI_SHADOW)
        arcade.draw_lrbt_rectangle_filled(0, WIDTH, HEIGHT - TOOLBAR_H, HEIGHT, UI_BG)
        arcade.draw_lrbt_rectangle_outline(0, WIDTH, HEIGHT - TOOLBAR_H, HEIGHT, UI_BORDER, 2)
        for b in self.buttons:
            b.draw()
        for cb in self.color_buttons:
            cb.draw()
        arcade.draw_text("Actual:", MARGIN, HEIGHT - TOOLBAR_H + 12, UI_TEXT, 14)
        arcade.draw_lrbt_rectangle_filled(MARGIN + 60, MARGIN + 94, HEIGHT - TOOLBAR_H + 10, HEIGHT - TOOLBAR_H + 44, self.color)
        arcade.draw_lrbt_rectangle_outline(MARGIN + 60, MARGIN + 94, HEIGHT - TOOLBAR_H + 10, HEIGHT - TOOLBAR_H + 44, UI_BORDER, 2)
        arcade.draw_text(self.tool.name.title(), MARGIN + 102, HEIGHT - TOOLBAR_H + 16, UI_MUTED, 14)
        arcade.draw_lrbt_rectangle_outline(0, WIDTH, 0, HEIGHT - TOOLBAR_H, CANVAS_BORDER, 2)
        if self.show_grid or self.tool.name == "CELL":
            c = self.grid_cell if self.tool.name != "CELL" else getattr(self.tool, "cell", 20)
            for gx in range(0, WIDTH, c):
                arcade.draw_line(gx, 0, gx, HEIGHT - TOOLBAR_H, arcade.color.LIGHT_GRAY, 1)
            for gy in range(0, HEIGHT - TOOLBAR_H, c):
                arcade.draw_line(0, gy, WIDTH, gy, arcade.color.LIGHT_GRAY, 1)
        for tool in self.used_tools.values():
            tool.draw_traces(self.traces)


def main():
    import sys
    window = arcade.Window(WIDTH, HEIGHT, TITLE)
    # Invocación del programa en la forma: python main.py ruta/a/mi/archivo
    if len(sys.argv) > 1:
        app = Paint(sys.argv[1])
    else:
        app = Paint()
    window.show_view(app)
    arcade.run()


if __name__ == "__main__":
    main()

