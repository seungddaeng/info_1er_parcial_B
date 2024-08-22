import arcade
from tool import PencilTool

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
SCREEN_TITLE = "Paint"

COLORS = {
    "black": arcade.color.BLACK,
    "red": arcade.color.RED,
    "blue": arcade.color.BLUE,
    "yellow": arcade.color.YELLOW,
    "green": arcade.color.GREEN,
}


class Paint(arcade.Window):
    def __init__(self, load_path: str = None):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        arcade.set_background_color(arcade.color.WHITE)
        self.tool = PencilTool()
        self.used_tools = {self.tool.name: self.tool}
        self.color = arcade.color.BLUE
        if load_path is not None:
            ### IMPLEMENTAR CARGA DE DIBUJO ###
            self.traces = []
        else:
            self.traces = []

    def on_key_press(self, symbol: int, modifiers: int):
        # Selección de herramientas con las teclas numéricas
        if symbol == arcade.key.KEY_1:
            self.tool = PencilTool()
        elif symbol == arcade.key.KEY_2:
            # other tool
            pass
        # Selección de color con teclas asd
        elif symbol == arcade.key.A:
            self.color = arcade.color.RED
        elif symbol == arcade.key.S:
            self.color = arcade.color.GREEN
        elif symbol == arcade.key.D:
            self.color = arcade.color.BLUE
        
        # Guardado del dibujo con la tecla O
        ### IMPLEMENTAR ###
        ####-----------####
        self.used_tools[self.tool.name] = self.tool
        print(self.used_tools, self.tool)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        print(x, y)
        if button == arcade.MOUSE_BUTTON_LEFT:
            self.traces.append({"tool": self.tool.name, "color": self.color, "trace":[(x, y)]})

    def on_mouse_drag(self, x: int, y: int, dx: int, dy: int, buttons: int, modifiers: int):
        if self.traces:
            self.traces[-1]["trace"].append((x, y))

    def on_draw(self):
        arcade.start_render()
        for tool in self.used_tools.values():
            tool.draw_traces(self.traces)


if __name__ == "__main__":
    import sys
    # Invocación del programa en la forma: python main.py ruta/a/mi/archivo
    if len(sys.argv) > 1:
        app = Paint(sys.argv[1])
    else:
        app = Paint()
    arcade.run()
