import bpy

from .ops.three_d import FULCRUM_OT_zoom


def register_keymaps(addon_keymaps):
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if not kc:
        return
    km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
    kmi = km.keymap_items.new(
        FULCRUM_OT_zoom.bl_idname,
        type="MIDDLEMOUSE",
        value="PRESS",
        ctrl=1,
        alt=1,
        shift=-1,
    )
    addon_keymaps.append((km, kmi))


def unregister_keymaps(addon_keymaps):
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()
