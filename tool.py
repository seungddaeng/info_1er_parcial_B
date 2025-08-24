import arcade
import random
from typing import Protocol


class Tool(Protocol):
    name: str
    def draw_traces(self, traces: list[dict]): ...
    def get_name(self) -> str: ...


class PencilTool(Tool):
    name = "PENCIL"

    def draw_traces(self, traces: list[dict]):
        for trace in traces:
            if trace["tool"] == self.name and len(trace["trace"]) >= 2:
                arcade.draw_line_strip(trace["trace"], trace["color"])

    def get_name(self) -> str:
        return self.name


class MarkerTool(Tool):
    name = "MARKER"

    def __init__(self, width: int = 8):
        self.width = width

    def draw_traces(self, traces: list[dict]):
        for trace in traces:
            if trace["tool"] == self.name and len(trace["trace"]) >= 2:
                w = trace.get("width", self.width)
                arcade.draw_line_strip(trace["trace"], trace["color"], w)

    def get_name(self) -> str:
        return self.name


class SprayTool(Tool):
    name = "SPRAY"

    def __init__(self, radius: int = 10, density: int = 20):
        self.radius = radius
        self.density = density

    def make_spray(self, x: int, y: int) -> list[tuple[int, int]]:
        pts: list[tuple[int, int]] = []
        for _ in range(self.density):
            rx = random.uniform(-self.radius, self.radius)
            ry = random.uniform(-self.radius, self.radius)
            if rx * rx + ry * ry <= self.radius * self.radius:
                pts.append((int(x + rx), int(y + ry)))
        return pts

    def draw_traces(self, traces: list[dict]):
        for trace in traces:
            if trace["tool"] == self.name and trace.get("points"):
                arcade.draw_points(trace["points"], trace["color"], 1)

    def get_name(self) -> str:
        return self.name


class EraserTool(Tool):
    name = "ERASER"

    def __init__(self, radius: int = 10):
        self.radius = radius

    def _dist_point_to_segment(self, px: int, py: int, x1: int, y1: int, x2: int, y2: int) -> float:
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            return ((px - x1) ** 2 + (py - y1) ** 2) ** 0.5
        t = ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)
        if t < 0:
            ex, ey = x1, y1
        elif t > 1:
            ex, ey = x2, y2
        else:
            ex, ey = x1 + t * dx, y1 + t * dy
        return ((px - ex) ** 2 + (py - ey) ** 2) ** 0.5

    def _overlaps_rect(self, px: int, py: int, left: int, right: int, bottom: int, top: int) -> bool:
        cx = min(max(px, left), right)
        cy = min(max(py, bottom), top)
        return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5 <= self.radius

    def erase_at(self, traces: list[dict], x: int, y: int) -> None:
        keep: list[dict] = []
        for tr in traces:
            t = tr["tool"]
            hit = False
            if t in ("PENCIL", "MARKER") and tr.get("trace"):
                seq = tr["trace"]
                w = tr.get("width", 1 if t == "PENCIL" else 8)
                for i in range(len(seq) - 1):
                    x1, y1 = seq[i]
                    x2, y2 = seq[i + 1]
                    if self._dist_point_to_segment(x, y, x1, y1, x2, y2) <= self.radius + w / 2:
                        hit = True
                        break
            elif t == "SPRAY":
                for (px, py) in tr.get("points", []):
                    if ((px - x) ** 2 + (py - y) ** 2) ** 0.5 <= self.radius:
                        hit = True
                        break
            elif t == "LINE":
                (x1, y1) = tr["start"]; (x2, y2) = tr["end"]
                w = tr.get("width", 2)
                if self._dist_point_to_segment(x, y, x1, y1, x2, y2) <= self.radius + w / 2:
                    hit = True
            elif t == "RECT":
                (x1, y1) = tr["start"]; (x2, y2) = tr["end"]
                left, right = min(x1, x2), max(x1, x2)
                bottom, top = min(y1, y2), max(y1, y2)
                w = tr.get("width", 2)
                if self._overlaps_rect(x, y, left - w, right + w, bottom - w, top + w):
                    if not self._overlaps_rect(x, y, left + w, right - w, bottom + w, top - w):
                        hit = True
            elif t == "CIRCLE":
                (cx, cy) = tr["start"]; (ex, ey) = tr["end"]
                r = ((ex - cx) ** 2 + (ey - cy) ** 2) ** 0.5
                w = tr.get("width", 2)
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if abs(dist - r) <= self.radius + w / 2:
                    hit = True
            elif t == "CELL":
                (rx, ry) = tr["xy"]; s = tr["size"]
                if self._overlaps_rect(x, y, rx, rx + s, ry, ry + s):
                    hit = True
            if not hit:
                keep.append(tr)
        traces[:] = keep

    def draw_traces(self, traces: list[dict]):
        return

    def get_name(self) -> str:
        return self.name


class LineTool(Tool):
    name = "LINE"

    def __init__(self, width: int = 2):
        self.width = width

    def draw_traces(self, traces: list[dict]):
        for tr in traces:
            if tr["tool"] == self.name:
                (x1, y1) = tr["start"]
                (x2, y2) = tr["end"]
                w = tr.get("width", self.width)
                arcade.draw_line(x1, y1, x2, y2, tr["color"], w)

    def get_name(self) -> str:
        return self.name


class RectTool(Tool):
    name = "RECT"

    def __init__(self, width: int = 2):
        self.width = width

    def draw_traces(self, traces: list[dict]):
        for tr in traces:
            if tr["tool"] == self.name:
                (x1, y1) = tr["start"]
                (x2, y2) = tr["end"]
                left = min(x1, x2)
                right = max(x1, x2)
                bottom = min(y1, y2)
                top = max(y1, y2)
                w = tr.get("width", self.width)
                arcade.draw_lrbt_rectangle_outline(left, right, bottom, top, tr["color"], w)

    def get_name(self) -> str:
        return self.name


class CircleTool(Tool):
    name = "CIRCLE"

    def __init__(self, width: int = 2):
        self.width = width

    def draw_traces(self, traces: list[dict]):
        for tr in traces:
            if tr["tool"] == self.name:
                (cx, cy) = tr["start"]
                (ex, ey) = tr["end"]
                r = int(((ex - cx) ** 2 + (ey - cy) ** 2) ** 0.5)
                w = tr.get("width", self.width)
                arcade.draw_circle_outline(cx, cy, r, tr["color"], w)

    def get_name(self) -> str:
        return self.name


class CellTool(Tool):
    name = "CELL"

    def __init__(self, cell: int = 20):
        self.cell = cell

    def _snap(self, x: int, y: int) -> tuple[int, int]:
        gx = (x // self.cell) * self.cell
        gy = (y // self.cell) * self.cell
        return int(gx), int(gy)

    def draw_traces(self, traces: list[dict]):
        for tr in traces:
            if tr["tool"] == self.name:
                (x, y) = tr["xy"]
                s = tr["size"]
                arcade.draw_lrbt_rectangle_filled(x, x + s, y, y + s, tr["color"])
                arcade.draw_lrbt_rectangle_outline(x, x + s, y, y + s, arcade.color.DARK_SLATE_GRAY, 1)

    def get_name(self) -> str:
        return self.name
