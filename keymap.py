import bpy

from .ops.three_d import FULCRUM_OT_zoom


def register_keymap(addon_keymaps):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(
            FULCRUM_OT_zoom.bl_idname,
            type="MIDDLEMOUSE",
            value="PRESS",
            ctrl=True,
            alt=True,
            shift=-1,
        )
        addon_keymaps.append((km, kmi))


def unregister_keymap(addon_keymaps):
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
