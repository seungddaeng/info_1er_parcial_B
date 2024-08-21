import arcade
from typing import Protocol, Union


class Tool(Protocol):
    name: str
    def draw_traces(self, traces: list[list[int]]):
        pass

    def get_name(self):
        return self.name


class PencilTool(Tool):
    name = "PENCIL"

    def draw_traces(self, traces: list[dict[str]]):
        for trace in traces:
            if trace["tool"] == self.name:
                arcade.draw_line_strip(trace["trace"], trace["color"])
