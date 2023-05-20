bl_info = {
    "name": "Fulcrum",
    "author": "Vladislav Macíček (Aeraglyx)",
    "description": "All kinds of tools",
    "blender": (3, 4, 0),
    "version": (0, 1, 27),
    "location": "Everywhere. Mostly in node editor and 3D viewport.",
    "doc_url": "https://github.com/aeraglyx/fulcrum",
    "category": "User Interface",
    "support": "COMMUNITY",
}

import bpy
from bpy.app.handlers import persistent

from .functions import *
from .handlers import register_handlers, unregister_handlers
from .keymap import register_keymap, unregister_keymap
from .ops.camera import (
    FULCRUM_OT_center_render_region,
    FULCRUM_OT_dof_setup,
    FULCRUM_OT_frame_range_from_cam,
    FULCRUM_OT_isometric_setup,
    FULCRUM_OT_passepartout,
    FULCRUM_OT_projection_setup,
    FULCRUM_OT_set_aspect_ratio,
    FULCRUM_OT_set_resolution,
)
from .ops.compare import FULCRUM_OT_benchmark, FULCRUM_OT_compare
from .ops.copy_pasta import FULCRUM_OT_copy_nodes, FULCRUM_OT_paste_nodes
from .ops.file_stuff import (
    FULCRUM_OT_go_to_latest_version,
    FULCRUM_OT_open_addon_preferences,
    FULCRUM_OT_open_blend_dir,
    FULCRUM_OT_open_script_dir,
    FULCRUM_OT_save_as_new_version,
    FULCRUM_OT_update_fulcrum,
)
from .ops.node_versioning import FULCRUM_OT_version_decode, FULCRUM_OT_version_encode
from .ops.nodes import (
    FULCRUM_OT_add_todo_note,
    FULCRUM_OT_align_nodes,
    FULCRUM_OT_align_nodes_v2,
    FULCRUM_OT_center_nodes,
    FULCRUM_OT_color_node_flow,
    FULCRUM_OT_hide_group_inputs,
    FULCRUM_OT_nodes_to_grid,
    FULCRUM_OT_randomize_node_color,
    FULCRUM_OT_remove_unused_group_inputs,
    FULCRUM_OT_reset_gn_defaults,
    FULCRUM_OT_reset_node_color,
    FULCRUM_OT_select_group_inputs,
    FULCRUM_OT_select_node_dependencies,
    FULCRUM_OT_select_node_inputs,
    FULCRUM_OT_select_unused_nodes,
    FULCRUM_OT_set_gn_defaults,
    FULCRUM_OT_set_node_color,
    FULCRUM_OT_set_node_size,
    FULCRUM_OT_tex_to_name,
)
from .ops.paint import FULCRUM_OT_set_paint_brush, FULCRUM_OT_set_weight_brush
from .ops.render import (
    FULCRUM_OT_anim_time_limit,
    FULCRUM_OT_compositor_increment_version,
    FULCRUM_OT_copy_passes,
    FULCRUM_OT_prepare_for_render,
    FULCRUM_OT_remove_unused_output_sockets,
    FULCRUM_OT_render_to_new_slot,
    FULCRUM_OT_set_output_directory,
    FULCRUM_OT_set_render_passes,
    FULCRUM_OT_view_layers_to_muted_nodes,
)
from .ops.three_d import (
    FULCRUM_OT_duplicates_to_instances,
    FULCRUM_OT_edit_light_power,
    FULCRUM_OT_locate_vertex,
    FULCRUM_OT_locate_vertices,
    FULCRUM_OT_mirror,
    FULCRUM_OT_obj_backup,
    FULCRUM_OT_reduce_materials,
    FULCRUM_OT_vert_group_2_col,
    FULCRUM_OT_zoom,
)
from .ops.tracking import (
    FULCRUM_OT_auto_marker_weight,
    FULCRUM_OT_clip_to_scene_resolution,
)
from .prefs import FulcrumPreferences
from .props import fulcrum_props
from .ui import (
    FULCRUM_PT_3d_axis_selection,
    FULCRUM_PT_3d_stuff,
    FULCRUM_PT_camera,
    FULCRUM_PT_camera_sub,
    FULCRUM_PT_compositor,
    FULCRUM_PT_data,
    FULCRUM_PT_find_nodes,
    FULCRUM_PT_fulcrum_3d,
    FULCRUM_PT_fulcrum_node,
    FULCRUM_PT_node_group,
    FULCRUM_PT_node_tools,
    FULCRUM_PT_optimization,
    FULCRUM_PT_paint,
    FULCRUM_PT_render,
    FULCRUM_PT_utility_3d,
    FULCRUM_PT_utility_node,
    register_menus_and_headers,
    unregister_menus_and_headers,
)

classes = (
    FulcrumPreferences,
    fulcrum_props,
    FULCRUM_OT_mirror,
    FULCRUM_OT_benchmark,
    FULCRUM_OT_anim_time_limit,
    FULCRUM_OT_vert_group_2_col,
    FULCRUM_OT_set_paint_brush,
    FULCRUM_OT_set_weight_brush,
    FULCRUM_OT_update_fulcrum,
    FULCRUM_OT_open_script_dir,
    FULCRUM_OT_open_blend_dir,
    FULCRUM_OT_save_as_new_version,
    FULCRUM_OT_go_to_latest_version,
    FULCRUM_OT_open_addon_preferences,
    FULCRUM_OT_select_node_inputs,
    FULCRUM_OT_select_node_dependencies,
    FULCRUM_OT_select_group_inputs,
    FULCRUM_OT_select_unused_nodes,
    FULCRUM_OT_set_node_color,
    FULCRUM_OT_reset_node_color,
    FULCRUM_OT_compare,
    FULCRUM_OT_center_nodes,
    FULCRUM_OT_nodes_to_grid,
    FULCRUM_OT_hide_group_inputs,
    FULCRUM_OT_remove_unused_group_inputs,
    FULCRUM_OT_set_gn_defaults,
    FULCRUM_OT_reset_gn_defaults,
    FULCRUM_OT_add_todo_note,
    FULCRUM_OT_version_encode,
    FULCRUM_OT_version_decode,
    FULCRUM_OT_copy_nodes,
    FULCRUM_OT_paste_nodes,
    FULCRUM_OT_align_nodes,
    FULCRUM_OT_align_nodes_v2,
    FULCRUM_OT_randomize_node_color,
    FULCRUM_OT_color_node_flow,
    FULCRUM_OT_tex_to_name,
    FULCRUM_OT_set_node_size,
    FULCRUM_OT_render_to_new_slot,
    FULCRUM_OT_set_render_passes,
    FULCRUM_OT_set_output_directory,
    FULCRUM_OT_prepare_for_render,
    FULCRUM_OT_compositor_increment_version,
    FULCRUM_OT_view_layers_to_muted_nodes,
    FULCRUM_OT_remove_unused_output_sockets,
    FULCRUM_OT_copy_passes,
    FULCRUM_OT_dof_setup,
    FULCRUM_OT_isometric_setup,
    FULCRUM_OT_projection_setup,
    FULCRUM_OT_frame_range_from_cam,
    FULCRUM_OT_passepartout,
    FULCRUM_OT_center_render_region,
    FULCRUM_OT_set_aspect_ratio,
    FULCRUM_OT_set_resolution,
    FULCRUM_OT_locate_vertex,
    FULCRUM_OT_locate_vertices,
    FULCRUM_OT_duplicates_to_instances,
    FULCRUM_OT_obj_backup,
    FULCRUM_OT_edit_light_power,
    FULCRUM_OT_reduce_materials,
    FULCRUM_OT_zoom,
    FULCRUM_OT_clip_to_scene_resolution,
    FULCRUM_OT_auto_marker_weight,
    # FULCRUM_PT_versioning,
    FULCRUM_PT_fulcrum_3d,
    FULCRUM_PT_3d_stuff,
    FULCRUM_PT_camera,
    FULCRUM_PT_camera_sub,
    FULCRUM_PT_3d_axis_selection,
    FULCRUM_PT_paint,
    FULCRUM_PT_utility_3d,
    FULCRUM_PT_fulcrum_node,
    FULCRUM_PT_node_tools,
    FULCRUM_PT_node_group,
    FULCRUM_PT_compositor,
    FULCRUM_PT_find_nodes,
    # FULCRUM_PT_node_group,
    FULCRUM_PT_optimization,
    FULCRUM_PT_utility_node,
    FULCRUM_PT_render,
    FULCRUM_PT_data,
    FULCRUM_PT_fulcrum_3d,
)

addon_keymaps = []


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.fulcrum = bpy.props.PointerProperty(type=fulcrum_props)
    register_menus_and_headers()
    register_handlers()
    register_keymap(addon_keymaps)
    print("FULCRUM registered")


def unregister():
    unregister_keymap(addon_keymaps)
    unregister_handlers()
    unregister_menus_and_headers()
    del bpy.types.Scene.fulcrum
    for cls in classes:
        bpy.utils.unregister_class(cls)
    print("FULCRUM unregistered")


if __name__ == "__main__":
    register()
