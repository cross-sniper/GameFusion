import os
from typing import Callable, Union
import simplexml
import zcore
from lupa import LuaRuntime, LuaError, lua_type

assets: dict


def fill_rect(x: int, y: int, w: int, h: int, color: zcore.draw.ColorType):
    """Draw a rectangle on the game window."""
    zcore.draw.fillRect(GameWindow, x, y, w, h, color)


def fill_circ(x: int, y: int, r: int, color: zcore.draw.ColorType):
    """Draw a circle on the game window."""
    zcore.draw.fillCircle(GameWindow, color, (x, y), r)


def draw_rect(x: int, y: int, w: int, h: int, color: zcore.draw.ColorType):
    """Draw a rectangle on the game window."""
    zcore.draw.drawRect(GameWindow, x, y, w, h, color)


def draw_circ(x: int, y: int, r: int, color: zcore.draw.ColorType):
    """Draw a circle on the game window."""
    zcore.draw.drawCircle(GameWindow, color, (x, y), r)


def draw_sprite(name: str, x: int, y: int, scaleX: int, scaleY: int):
    sprite: zcore.obj.SpriteObject = assets.get(name)
    if not sprite:
        simplexml.panic("you dont have a sprite named", name)
    sprite.draw(GameWindow, x, y, scaleX, scaleY)


# def drawText(window: pygame.Surface,text: str, x: int, y: int, size: int, color: ColorType) -> None
def draw_text(text: str, x: int, y: int, fontSize: int, color: zcore.draw.ColorType):
    zcore.draw.drawText(GameWindow, text, x, y, fontSize, color)


# Initialize Lua Runtime
lua = LuaRuntime(unpack_returned_tuples=True)


def add_lua_func(name: str, function: Callable):
    """Add a Python function to the Lua global environment."""
    lua.globals()[name] = function


def add_lua_value(name: str, value: Union[str, int, bool]):
    """Add a Python value to the Lua global environment."""
    lua.globals()[name] = value


def load_lua_script(script_path: str):
    """Load and execute a Lua script."""
    if not os.path.isfile(script_path):
        simplexml.panic("Main script not found:", script_path)
    with open(script_path) as f:
        content = f.read()
    try:
        lua.execute(content)
        add_lua_func("fillRect", fill_rect)
        add_lua_func("fillRound", fill_circ)

        add_lua_func("fillRect", fill_rect)
        add_lua_func("fillRound", fill_circ)

        add_lua_func("keyDown", zcore.window.isKeyDown)
        add_lua_func("keyPressed", zcore.window.isKeyPressed)

        add_lua_func("drawSprite", draw_sprite)
        add_lua_func("drawText", draw_text)

        add_lua_value("KEY_ESC", zcore.keys.KEY_ESC)

    except LuaError as e:
        simplexml.panic("Lua script error:", e)


def load_assets(file_list, projectXml):
    """Load asset files and return a dictionary of SpriteObjects."""
    assets = {}
    for file in file_list:
        if not os.path.isfile(file):
            simplexml.panic("File not found:", file)
        print(f"Loading: {file}")
        assets[file] = zcore.obj.SpriteObject(file)
    return assets


def configure_game_window(config: dict) -> zcore.window.pygame.Surface:
    """Configure and create the game window based on the project config."""
    width = int(config.get("dimensions", {}).get("width", 800))
    height = int(config.get("dimensions", {}).get("height", 600))
    title = config.get("title", "Untitled Project")
    return zcore.window.createWindow(width, height, title)


def call_lua_function(func_name: str, *args):
    """Call a Lua function and handle potential errors."""
    func = lua.globals()[func_name]
    if callable(func):
        try:
            func(*args)
        except LuaError as e:
            simplexml.panic(f"Error calling Lua function '{func_name}':", e)
    else:
        simplexml.panic(f"Lua function '{func_name}' not found")


def main_process(dt: float) -> None:
    """Main game loop process."""
    zcore.draw.clearBackground(GameWindow, "black")
    call_lua_function("update", dt)
    call_lua_function("draw")


def handle_nonexistent_functions():
    """Check for the existence of required Lua functions."""
    required_functions = ["setup", "draw", "update"]
    for func_name in required_functions:
        func = lua.globals()[func_name]
        if lua_type(func) != "function":
            simplexml.panic(f"You need '{func_name}' to be a function.")


if __name__ == "__main__":
    projectXml = simplexml.loadFile("project.xml")
    print(f"project data:\n{projectXml}")

    mainScript = projectXml.get("project", {}).get("main", "scripts/main.lua")
    load_lua_script(mainScript)

    files = projectXml.get("project", {}).get("files", [])
    assets = load_assets(files, projectXml)

    GameWindow = configure_game_window(projectXml.get("project", {}))
    handle_nonexistent_functions()
    call_lua_function("setup")

    zcore.window.mainLoop(main_process)
