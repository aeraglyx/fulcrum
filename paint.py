import bpy

class AX_OT_paint_color(bpy.types.Operator):
    """Set color for vertex paint brush""" # todo check if this is the tooltip
    # todo separate into two classes?
    # or actually this for vertex groups is kinda useless

    bl_idname = "ax.paint_color"
    bl_label = "Set Brush Color"
    bl_description = ""
    
    @classmethod
    def poll(cls, context):
        weight = bpy.context.mode == 'PAINT_WEIGHT'
        paint = bpy.context.mode == 'PAINT_VERTEX'
        return weight or paint

    weight: bpy.props.FloatProperty(
        name = "Weight", 
        subtype = 'FACTOR', 
        default = 0.0, min = 0.0, max = 1.0
    )
    color: bpy.props.FloatVectorProperty(
        name = "Color", 
        subtype = 'COLOR', 
        default = (0.0, 0.0, 0.0)
    )

    def execute(self, context):

        if bpy.context.mode == 'PAINT_WEIGHT':
            bpy.context.scene.tool_settings.unified_paint_settings.use_unified_weight = True
            bpy.context.scene.tool_settings.unified_paint_settings.weight = self.weight
        if bpy.context.mode == 'PAINT_VERTEX':
            bpy.context.scene.tool_settings.unified_paint_settings.use_unified_color = True
            bpy.context.scene.tool_settings.unified_paint_settings.color = self.color

        return {'FINISHED'}