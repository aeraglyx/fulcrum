import bpy

from ..ops.file_stuff import is_current_file_version


def draw_topbar(self, context):
    if context.region.alignment != "RIGHT":
        layout = self.layout
        if bpy.data.is_saved:
            if is_current_file_version():
                if bpy.data.is_dirty:
                    layout.label(text="Latest but not saved.", icon="STRIP_COLOR_07")
                else:
                    layout.label(text="DON'T PANIC!", icon="STRIP_COLOR_05")
            else:
                layout.label(text="Not the latest version!", icon="STRIP_COLOR_01")
                layout.operator(
                    "fulcrum.go_to_latest_version",
                    text="Go to Latest",
                    icon="LOOP_FORWARDS",
                )
        else:
            layout.label(text="File not saved!", icon="STRIP_COLOR_01")


def draw_outliner(self, context):
    if context.space_data.display_mode == "SCENES":
        self.layout.operator(
            "fulcrum.view_layers_to_muted_nodes", text="", icon="TRIA_LEFT"
        )


def draw_timeline(self, context):
    if context.area.ui_type == "TIMELINE":
        scene = context.scene
        if scene.use_preview_range:
            frame_start = scene.frame_preview_start
            frame_end = scene.frame_preview_end
        else:
            frame_start = scene.frame_start
            frame_end = scene.frame_end
        frame_count = frame_end - frame_start + 1
        seconds = frame_count / scene.render.fps
        self.layout.label(text=f"{frame_count} | {seconds:.2f}s")


def draw_material(self, context):
    self.layout.operator("fulcrum.reduce_materials", icon="TRASH")


def register_menus_and_headers():
    # bpy.types.TOPBAR_HT_upper_bar.append(draw_topbar)
    bpy.types.OUTLINER_HT_header.append(draw_outliner)
    bpy.types.DOPESHEET_HT_header.append(draw_timeline)
    bpy.types.MATERIAL_MT_context_menu.append(draw_material)


def unregister_menus_and_headers():
    # bpy.types.TOPBAR_HT_upper_bar.remove(draw_topbar)
    bpy.types.OUTLINER_HT_header.remove(draw_outliner)
    bpy.types.DOPESHEET_HT_header.remove(draw_timeline)
    bpy.types.MATERIAL_MT_context_menu.remove(draw_material)
