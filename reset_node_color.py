import bpy

class AX_OT_reset_node_color(bpy.types.Operator):
    
    """ Reset custom node color """
    
    bl_idname = "ax.reset_node_color"
    bl_label = "Reset Node Color"
    bl_description = "Reset custom node color"
    
    @classmethod
    def poll(cls, context):
        selected = bpy.context.selected_nodes
        return selected

    def execute(self, context):

        selected = bpy.context.selected_nodes
        for node in selected:
            node.use_custom_color = False
        
        return {'FINISHED'}