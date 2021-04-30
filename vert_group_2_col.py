import bpy

class AX_OT_vert_group_2_col(bpy.types.Operator):
    
    bl_idname = "ax.vert_group_2_col"
    bl_label = "Groups to Colors"
    bl_description = ""
    
    @classmethod
    def poll(cls, context):
        return len(bpy.context.active_object.vertex_groups) # todo idk

    def execute(self, context):

        groups = bpy.context.active_object.vertex_groups
        colors = bpy.context.active_object.data.vertex_colors

        if bpy.context.mode != 'PAINT_VERTEX':
            bpy.ops.paint.vertex_paint_toggle()

        for group in groups:
            
            col = colors.new()
            col.name = group.name

            groups.active = group
            colors.active = col

            bpy.ops.paint.vertex_color_from_weight()
        
        # maybe go back to obj mode?

        self.report({'INFO'}, f"Done.")

        return {'FINISHED'}