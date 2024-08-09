#!/usr/bin/env python

import os
from typing import Callable, Union
import simplexml, json
import zcore
from lupa import LuaRuntime, LuaError, lua_type


import map_parser as mp
import argparse

# Global variables to store assets and maps
assets: dict = {}
maps: dict = {}
GameWindow: zcore.window.pygame.Surface
# Initialize Lua Runtime
lua: LuaRuntime = LuaRuntime(unpack_returned_tuples=True)


# Drawing functions
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


def draw_map(name: str):
    f = maps.get(name)
    if f:
        for data in f:
            cell_type = data["type"]
            properties = data["properties"]

            # Extract common properties
            pos = properties["pos"]["values"]
            x, y = int(pos[0]), int(pos[1])
            display_color = properties.get("displayColor", {}).get("values", ["black"])[
                0
            ]

            if cell_type == "rect":
                size = properties["size"]["values"]
                w, h = int(size[0]), int(size[1])
                fill_rect(x, y, w, h, display_color)

            elif cell_type == "circle":
                rad = int(properties["rad"]["values"][0])
                fill_circ(x, y, rad, display_color)
    else:
        simplexml.panic("no map found")


def draw_sprite(name: str, x: int, y: int, scaleX: int, scaleY: int):
    sprite: zcore.obj.SpriteObject | None = assets.get(name)
    if sprite == None:
        simplexml.panic("You don't have a sprite named", name)
    else:
        sprite.draw(GameWindow, x, y, scaleX, scaleY)


def draw_text(text: str, x: int, y: int, fontSize: int, color: zcore.draw.ColorType):
    zcore.draw.drawText(GameWindow, text, x, y, fontSize, color)


def clear_screen(color: zcore.draw.ColorType = "black"):
    zcore.draw.clearBackground(GameWindow, color)


def add_lua_func(name: str, function: Callable):
    """Add a Python function to the Lua global environment."""
    lua.globals()[name] = function


def add_lua_value(name: str, value: Union[str, int, bool]):
    """Add a Python value to the Lua global environment."""
    lua.globals()[name] = value


def add_lua_func_to_table(tableName: str, name: str, function: Callable):
    """Add a Python function to a Lua table."""
    lua.globals()[tableName][name] = function


def add_lua_value_to_table(tableName: str, name: str, value: Union[str, int, bool]):
    """Add a Python value to a Lua table."""
    lua.globals()[tableName][name] = value


def push_keys_to_lua_keyboard():
    for key in dir(zcore.keys):
        if key.startswith("KEY_"):
            value = getattr(zcore.keys, key)
            add_lua_value_to_table("keyboard", key[len("KEY_") :], value)


def load_lua_script(script_path: str):
    """Load and execute a Lua script."""
    if not os.path.isfile(script_path):
        simplexml.panic("Main script not found:", script_path)
    with open(script_path) as f:
        content = f.read()
    try:
        lua.execute(content)
        lua.execute("screen = {}")
        lua.execute("keyboard = {}")
        add_lua_func_to_table("screen", "fillRect", fill_rect)
        add_lua_func_to_table("screen", "fillRound", fill_circ)
        add_lua_func_to_table("screen", "drawRect", draw_rect)
        add_lua_func_to_table("screen", "drawRound", draw_circ)
        add_lua_func_to_table("screen", "drawSprite", draw_sprite)
        add_lua_func_to_table("screen", "drawText", draw_text)
        add_lua_func_to_table("screen", "drawMap", draw_map)
        add_lua_func_to_table("screen", "clear", clear_screen)

        add_lua_func_to_table("keyboard", "keyDown", zcore.window.isKeyDown)
        add_lua_func_to_table("keyboard", "keyPressed", zcore.window.isKeyPressed)
        push_keys_to_lua_keyboard()
    except LuaError as e:
        simplexml.panic("Lua script error:", e)


def load_asset_sprites(file_list: list[str]):
    """Load asset files and return a dictionary of SpriteObjects."""
    global assets
    for file in file_list:
        filepath = os.path.join("sprites", file)
        filename = os.path.splitext(file)[0]  # Get filename without extension

        if not os.path.isfile(filepath):
            simplexml.panic("File not found:", filepath)
        print(f"Loading: {file}")
        assets[filename] = zcore.obj.SpriteObject(filepath)
    return assets


def load_asset_maps(file_list: list[str]):
    global maps
    for file in file_list:
        filepath = os.path.join("maps", file)
        filename = os.path.splitext(file)[0]  # Get filename without extension
        if not os.path.isfile(filepath):
            simplexml.panic("File not found:", filepath)
        print(f"Loading: {file}")
        maps[filename] = mp.parse(filepath)
    print(maps)
    return maps


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
    call_lua_function("update", dt)
    call_lua_function("draw")


def handle_nonexistent_functions():
    """Check for the existence of required Lua functions."""
    required_functions = ["setup", "draw", "update"]
    for func_name in required_functions:
        func = lua.globals()[func_name]
        if lua_type(func) != "function":
            simplexml.panic(f"You need '{func_name}' to be a function.")


def main():
    global GameWindow, assets, maps

    argsparser = argparse.ArgumentParser()
    argsparser.add_argument("-pf", help="This is the project source file to run")

    args = argsparser.parse_args()
    if not args.pf:
        argsparser.print_help()
        exit(1)
    projectXml = simplexml.load_file(args.pf)
    print(f"Project data:\n{projectXml}")

    mainScript = projectXml.get("project", {}).get("main", {})
    lang = mainScript.get("lang", "lua")
    mainScriptPath = mainScript.get("path", "scripts/main.lua")
    if lang == "lua":
        load_lua_script(mainScriptPath)

    else:
        simplexml.panic("language not supported: ", lang)
    handle_nonexistent_functions()

    sprites = projectXml.get("project", {}).get("files", {}).get("sprites", [])
    assets = load_asset_sprites(sprites)
    mapPaths = projectXml.get("project", {}).get("files", {}).get("maps", [])
    maps = load_asset_maps(mapPaths)

    GameWindow = configure_game_window(projectXml.get("project", {}))
    call_lua_function("setup")

    zcore.window.mainLoop(main_process)


if __name__ == "__main__":
    main()
