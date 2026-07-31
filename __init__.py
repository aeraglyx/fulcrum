import bpy

from . import ops, ui

from .keymap import register_keymaps, unregister_keymaps
from .prefs import FulcrumPreferences
from .props import fulcrum_props
from .ui import (
    register_menus_and_headers,
    unregister_menus_and_headers,
)


def register_unregister_modules(modules, register: bool):
    register_func = bpy.utils.register_class if register else bpy.utils.unregister_class
    for module in modules:
        if hasattr(module, "registry"):
            for cls in module.registry:
                    register_func(cls)
        if hasattr(module, "modules"):
            register_unregister_modules(module.modules, register)


modules = [ops, ui]
classes = (
    FulcrumPreferences,
    fulcrum_props,
)

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    register_unregister_modules(modules, register=True)
    bpy.types.Scene.fulcrum = bpy.props.PointerProperty(type=fulcrum_props)
    register_menus_and_headers()
    register_keymaps(addon_keymaps)
    print("FULCRUM registered")


def unregister():
    unregister_keymaps(addon_keymaps)
    unregister_menus_and_headers()
    del bpy.types.Scene.fulcrum
    for cls in classes:
        bpy.utils.unregister_class(cls)
    register_unregister_modules(modules, register=False)
    print("FULCRUM unregistered")


if __name__ == "__main__":
    register()
