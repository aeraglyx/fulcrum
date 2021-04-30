import bpy

class AX_OT_paint_color(bpy.types.Operator):
    
    bl_idname = "ax.paint_color"
    bl_label = "Set Brush Color"
    bl_description = ""
    
    @classmethod
    def poll(cls, context):
        paint = bpy.context.mode == 'PAINT_VERTEX'
        return True

    color: bpy.props.FloatVectorProperty(
        name = "Color", 
        subtype = 'COLOR', 
        default = (0.0, 0.0, 0.0)
    )

    def execute(self, context):

        bpy.context.scene.tool_settings.unified_paint_settings.use_unified_color = True
        bpy.context.scene.tool_settings.unified_paint_settings.color = self.color

        return {'FINISHED'}