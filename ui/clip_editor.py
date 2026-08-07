import bpy


class FULCRUM_PT_tracker(bpy.types.Panel):
    bl_space_type = "CLIP_EDITOR"
    bl_region_type = "TOOLS"
    bl_category = "Solve"
    bl_label = "Fulcrum"

    def draw(self, context):
        layout = self.layout
        layout.operator("fulcrum.auto_marker_weight", icon="TRACKER")


registry = [
    FULCRUM_PT_tracker,
]
