import bpy


# PROPERTIES

class AX_PT_render(bpy.types.Panel):
    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "render"
    COMPAT_ENGINES = {'CYCLES'}
    bl_label = "Fulcrum"

    def draw (self, context):
        layout = self.layout
        row = layout.row()
        row.operator("ax.render_in_time", icon = 'RENDER_STILL')
        layout.operator("ax.benchmark", icon = 'NONE')

class AX_PT_data(bpy.types.Panel):
    
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"
    bl_label = "Fulcrum"

    def draw (self, context):
        layout = self.layout
        row = layout.row()
        row.operator("ax.vert_group_2_col", icon = 'COLOR')


# NODE EDITOR
        
class AX_PT_node_tools(bpy.types.Panel):
    
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Fulcrum"
    bl_label = "Node Tools"

    def draw (self, context):
        layout = self.layout

        col = layout.column(align = True)
        selected = col.operator("ax.reset_node_color", text = "Reset Selected")  # FILE_REFRESH
        selected.all = False
        all = col.operator("ax.reset_node_color", text = "Reset All")
        all.all = True

        col = layout.column(align = True)
        col.operator("ax.node_flow")
        col.operator("ax.unused_nodes")
        col.operator("ax.find_inputs")

class AX_PT_optimization(bpy.types.Panel):
    
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Fulcrum"
    bl_label = "Optimization"
    
    @classmethod
    def poll(cls, context):
        in_shader_editor = context.space_data.tree_type == 'ShaderNodeTree'
        return in_shader_editor

    def draw (self, context):
        
        layout = self.layout
        props = context.scene.ax_compare

        # layout.prop(props, "engine")
        
        # col = layout.column(align = True)
        # col.prop(props, "frames")
        # col.prop(props, "resolution")
        # col.prop(props, "samples")
        
        # layout.prop(props, "use_base")
        
        # row_thicc = layout.row()
        # row_thicc.scale_y = 1.4
        row = layout.row()
        row.operator("ax.compare", icon = 'NONE')  # SORTTIME TIME TEMP
        
        col = layout.column(align = True)
        col.label(text = f"Ratio: {props.result:.3f}", icon = 'SETTINGS')  # UV_SYNC_SELECT CONSTRAINT SETTINGS
        col.label(text = f"Confidence: {props.confidence*100:.0f}%", icon = 'RNDCURVE')  # INDIRECT_ONLY_ON RNDCURVE


# VIEW 3D

class AX_PT_paint(bpy.types.Panel):
    
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Fulcrum"
    bl_label = "Paint"

    @classmethod
    def poll(cls, context):
        weight = context.mode == 'PAINT_WEIGHT'
        paint = context.mode == 'PAINT_VERTEX'
        return weight or paint

    def draw (self, context):
        
        layout = self.layout
        
        if bpy.context.mode == 'PAINT_VERTEX':
            
            col = layout.column(align = True)
            row = col.row(align = True)
            props = row.operator("ax.set_paint_brush", text = "R", icon = 'NONE')
            props.color = (1.0, 0.0, 0.0)
            props = row.operator("ax.set_paint_brush", text = "G", icon = 'NONE')
            props.color = (0.0, 1.0, 0.0)
            props = row.operator("ax.set_paint_brush", text = "B", icon = 'NONE')
            props.color = (0.0, 0.0, 1.0)

            row = col.row(align = True)
            props = row.operator("ax.set_paint_brush", text = "Blegh", icon = 'NONE')
            props.color = (0.0, 0.0, 0.0)
            props = row.operator("ax.set_paint_brush", text = "Grey", icon = 'NONE')
            props.color = (0.5, 0.5, 0.5)
            props = row.operator("ax.set_paint_brush", text = "White", icon = 'NONE')
            props.color = (1.0, 1.0, 1.0)

        if bpy.context.mode == 'PAINT_WEIGHT':

            row = layout.row(align = True)
            props = row.operator("ax.set_weight_brush", text = "0.0", icon = 'NONE')
            props.weight = 0.0
            props = row.operator("ax.set_weight_brush", text = "0.5", icon = 'NONE')
            props.weight = 0.5
            props = row.operator("ax.set_weight_brush", text = "1.0", icon = 'NONE')
            props.weight = 1.0