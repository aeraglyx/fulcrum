import bpy


class FulcrumPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    experimental: bpy.props.BoolProperty(
        name="Experimental",
        default=False,
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "experimental")
        layout.operator("fulcrum.update_fulcrum", text="Update", icon="FILE_REFRESH")


registry = [FulcrumPreferences]
