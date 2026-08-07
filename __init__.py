import bpy

from . import ops, ui, prefs, props

from .keymap import register_keymaps, unregister_keymaps
from .ui.menus_and_headers import (
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


modules = [prefs, props, ops, ui]
addon_keymaps = []


def register():
    register_unregister_modules(modules, register=True)
    bpy.types.Scene.fulcrum = bpy.props.PointerProperty(type=props.FulcrumProps)
    register_menus_and_headers()
    register_keymaps(addon_keymaps)
    print("FULCRUM registered")


def unregister():
    unregister_keymaps(addon_keymaps)
    unregister_menus_and_headers()
    del bpy.types.Scene.fulcrum
    register_unregister_modules(modules, register=False)
    print("FULCRUM unregistered")


if __name__ == "__main__":
    register()
