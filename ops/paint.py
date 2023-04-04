import bpy


class FULCRUM_OT_set_paint_brush(bpy.types.Operator):
    """Set color for vertex paint brush"""  # todo check if this is the tooltip

    bl_idname = "fulcrum.set_paint_brush"
    bl_label = "Set Brush Color"
    bl_description = "Set color for vertex paint brush"

    @classmethod
    def poll(cls, context):
        return context.mode == "PAINT_VERTEX"

    color: bpy.props.FloatVectorProperty(
        name="Color", subtype="COLOR", default=(0.0, 0.0, 0.0)
    )

    def execute(self, context):

        context.scene.tool_settings.unified_paint_settings.use_unified_color = True
        context.scene.tool_settings.unified_paint_settings.color = self.color

        return {"FINISHED"}


class FULCRUM_OT_set_weight_brush(bpy.types.Operator):
    """Set weight for weight paint brush"""

    bl_idname = "fulcrum.set_weight_brush"
    bl_label = "Set Brush Weight"
    bl_description = "Set weight for weight paint brush"

    @classmethod
    def poll(cls, context):
        return context.mode == "PAINT_WEIGHT"

    weight: bpy.props.FloatProperty(name="Weight", subtype="FACTOR", default=0.0)

    def execute(self, context):

        context.scene.tool_settings.unified_paint_settings.use_unified_weight = True
        context.scene.tool_settings.unified_paint_settings.weight = self.weight

        return {"FINISHED"}
