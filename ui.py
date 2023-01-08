import bpy


# --- PROPERTIES ---

class AX_PT_render(bpy.types.Panel):
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "render"
	COMPAT_ENGINES = {'CYCLES'}
	bl_label = "Fulcrum"

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.operator("ax.anim_time_limit", icon='RENDER_ANIMATION')
		layout.operator("ax.benchmark", icon='NONE')
		layout.operator("ax.render_to_new_slot", icon='RENDER_RESULT')

class AX_PT_data(bpy.types.Panel):
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "data"
	bl_label = "Fulcrum"

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.operator("ax.vert_group_2_col", icon='COLOR')

class AX_PT_physics(bpy.types.Panel):
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "physics"
	bl_label = "Fulcrum"

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.operator("ax.cloth_vert_mass", icon='MOD_VERTEX_WEIGHT')


# --- NODE EDITOR ---

# class AX_PT_node_group(bpy.types.Panel):
	
# 	bl_space_type = "NODE_EDITOR"
# 	bl_region_type = "UI"
# 	bl_category = "Group"
# 	bl_label = "Fulcrum"

# 	def draw(self, context):

# 		layout = self.layout

# 		col = layout.column(align=True)
# 		col.label(text="GN Defaults:")
# 		row = col.row(align=True)
# 		row.operator("ax.set_gn_defaults", text="Set")
# 		row.operator("ax.reset_gn_defaults", text="Reset")
		
class AX_PT_node_tools(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Node Tools"

	def draw(self, context):

		layout = self.layout

		layout.prop(context.scene.fulcrum, 'dev')

		col = layout.column(align=True)
		col.label(text="Node Alignment:")
		row = col.row(align=True)
		row.operator("ax.align_nodes", text="Auto")
		row.operator("ax.center_nodes", text="Center")
		row.operator("ax.nodes_to_grid", text="Grid")
		if context.scene.fulcrum.dev:
			col.operator("ax.align_nodes_v2", icon='ALIGN_CENTER')
			col.operator("ax.color_node_flow", icon='COLOR')
			col.operator("ax.randomize_node_color", icon='COLOR')
		
		col = layout.column(align=True)
		col.operator("ax.hide_group_inputs", icon='HIDE_ON')

		if context.scene.fulcrum.dev:
			col = layout.column(align=True)
			col.label(text="GN Defaults:")
			row = col.row(align=True)
			row.operator("ax.set_gn_defaults", text="Set")
			row.operator("ax.reset_gn_defaults", text="Reset")

		col = layout.column(align=True)
		# col.label(text="Node Color:", icon='COLOR')  # COLOR  RESTRICT_COLOR_OFF  FILE_REFRESH
		row = col.row(align=True)
		row.operator("ax.reset_node_color", text="", icon='FILE_REFRESH')
		grey = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_09')
		grey.color = [0.25, 0.25, 0.25]
		red = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_01')
		red.color = [0.33, 0.18, 0.19]
		orange = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_02')
		orange.color = [0.40, 0.27, 0.19]
		yellow = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_03')
		yellow.color = [0.40, 0.40, 0.30]
		green = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_04')
		green.color = [0.24, 0.35, 0.26]
		blue = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_05')
		blue.color = [0.25, 0.34, 0.39]
		purple = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_06')
		purple.color = [0.28, 0.26, 0.40]
		pink = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_07')
		pink.color = [0.41, 0.30, 0.40]
		# brown = row.operator("ax.set_node_color", text="", icon='SEQUENCE_COLOR_08')
		# brown.color = [0.29, 0.25, 0.22]

		col = layout.column(align=True)
		col.label(text="Find:", icon='VIEWZOOM')  # COLOR
		row = col.row(align=True)
		row.operator("ax.select_node_inputs", text="Inputs")  # icon = 'NODE'
		row.operator("ax.select_node_dependencies", text="Deps")  # icon = 'NODETREE'  # STROKE  ANIM_DATA  TRACKING
		row = col.row(align=True)
		row.operator("ax.select_group_inputs", text="Group Inputs")
		row.operator("ax.select_unused_nodes", text="Unused")

		if context.scene.fulcrum.dev:
			col = layout.column(align=True)
			col.prop(context.scene.fulcrum, 'use_node_handler')
			if context.scene.fulcrum.use_node_handler:
				col.prop(context.scene.fulcrum, 'node_vis_type', text='')

		col = layout.column(align=True)
		col.label(text="Node Size:", icon='FIXED_SIZE')
		row = col.row(align=True)
		default = row.operator("ax.set_node_size", text="Def.")
		default.size = 1.0
		two = row.operator("ax.set_node_size", text="2x")
		two.size = 2.0
		four = row.operator("ax.set_node_size", text="4x")
		four.size = 4.0
		
		# col = layout.column(align=True)
		# row = col.row(align=True)
		# row.operator("ax.copy_nodes", text="Copy", icon='COPYDOWN')
		# row.operator("ax.paste_nodes", text="Pasta", icon='PASTEDOWN')

		if context.area.ui_type == 'ShaderNodeTree':
			if context.space_data.shader_type == 'OBJECT':
				col = layout.column(align=True)
				col.label(text="Texture Name to:", icon='TEXTURE')
				row = col.row(align=True)
				mat = row.operator("ax.tex_to_name", text="Mat")  # NODE_MATERIAL
				mat.mat = True
				mat.obj = False
				obj = row.operator("ax.tex_to_name", text="Obj")  # OBJECT_DATA
				obj.mat = False
				obj.obj = True
				both = row.operator("ax.tex_to_name", text="Both")
				both.mat = True
				both.obj = True

		if context.scene.fulcrum.dev:
			col = layout.column(align=True)
			row = col.row(align=True)
			row.operator("ax.version_encode", text="Encode", icon='SYSTEM')
			row.operator("ax.version_decode", text="Decode", icon='ZOOM_ALL')
		
class AX_PT_compositor(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Compositor"
	
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'CompositorNodeTree'

	def draw(self, context):
		layout = self.layout
		# props = context.scene.fulcrum
		col = layout.column(align=True)
		col.operator("ax.set_output_directory", icon='FILE_FOLDER')
		col.operator("ax.set_render_passes", icon='NODE_COMPOSITING')
		
class AX_PT_optimization(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Optimization"
	bl_options = {'DEFAULT_CLOSED'}
	
	@classmethod
	def poll(cls, context):
		return context.space_data.tree_type == 'ShaderNodeTree'

	def draw(self, context):
		layout = self.layout
		props = context.scene.fulcrum
		row = layout.row()
		row.operator("ax.compare", icon='NONE')  # SORTTIME TIME TEMP
		col = layout.column(align=True)
		col.label(text = f"Ratio: {props.result:.3f}", icon='SETTINGS')  # UV_SYNC_SELECT CONSTRAINT SETTINGS
		col.label(text = f"Confidence: {props.confidence*100:.0f}%", icon='RNDCURVE')  # INDIRECT_ONLY_ON RNDCURVE

class AX_PT_utility_node(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Utility"

	def draw(self, context):
		layout = self.layout

		col = layout.column(align=True)
		col.operator("ax.open_blend_dir", icon='FILE_BACKUP')
		col.operator("ax.open_script_dir", icon='SCRIPT')  # FOLDER_REDIRECT  SCRIPT
		
		layout.operator("wm.console_toggle", icon='CONSOLE')



# --- VIEW 3D ---

from .ops.file_stuff import is_current_file_version

def draw_topbar(self, context):

	# red - 	SEQUENCE_COLOR_01
	# orange - 	SEQUENCE_COLOR_02
	# yellow - 	SEQUENCE_COLOR_03
	# green - 	SEQUENCE_COLOR_04
	# blue - 	SEQUENCE_COLOR_05
	# purple - 	SEQUENCE_COLOR_06
	# pink - 	SEQUENCE_COLOR_07

	if context.region.alignment != 'RIGHT':
		layout = self.layout
		if bpy.data.is_saved:
			if is_current_file_version():
				if bpy.data.is_dirty:
					layout.label(text="Latest but not saved.", icon='SEQUENCE_COLOR_07')
				else:
					layout.label(text="DON'T PANIC!", icon='SEQUENCE_COLOR_05')
				# layout.operator("ax.go_to_latest_version", icon='SEQUENCE_COLOR_04')
			else:
				layout.label(text="Not the latest version!", icon='SEQUENCE_COLOR_01')
				layout.operator("ax.go_to_latest_version", text="Go to Latest", icon='LOOP_FORWARDS')
			layout.operator("ax.save_as_new_version", text="Save as New", icon='DUPLICATE')
		else:
			layout.label(text="File not saved!", icon='SEQUENCE_COLOR_01')

class AX_PT_ease_of_access(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Ease of Access"

	def draw(self, context):
		layout = self.layout
		col = layout.column(align=True)
		col.prop(context.scene.fulcrum, 'dev')
		col.prop(context.scene.render, "use_motion_blur")
		col.prop(context.scene.render, "film_transparent")

		# layout.prop(context.scene.view_settings, "view_transform", text="")
		# layout.prop(context.scene.tool_settings, "use_keyframe_insert_auto")

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

	def draw(self, context):
		layout = self.layout
		if bpy.context.mode == 'PAINT_VERTEX':
			
			col = layout.column(align=True)
			row = col.row(align=True)
			props = row.operator("ax.set_paint_brush", text="R", icon='NONE')
			props.color = (1.0, 0.0, 0.0)
			props = row.operator("ax.set_paint_brush", text="G", icon='NONE')
			props.color = (0.0, 1.0, 0.0)
			props = row.operator("ax.set_paint_brush", text="B", icon='NONE')
			props.color = (0.0, 0.0, 1.0)

			row = col.row(align=True)
			props = row.operator("ax.set_paint_brush", text="Blegh", icon='NONE')
			props.color = (0.0, 0.0, 0.0)
			props = row.operator("ax.set_paint_brush", text="Grey", icon='NONE')
			props.color = (0.5, 0.5, 0.5)
			props = row.operator("ax.set_paint_brush", text="White", icon='NONE')
			props.color = (1.0, 1.0, 1.0)

		if bpy.context.mode == 'PAINT_WEIGHT':

			row = layout.row(align=True)
			props = row.operator("ax.set_weight_brush", text="0.0", icon='NONE')
			props.weight = 0.0
			props = row.operator("ax.set_weight_brush", text="0.5", icon='NONE')
			props.weight = 0.5
			props = row.operator("ax.set_weight_brush", text="1.0", icon='NONE')
			props.weight = 1.0

class AX_PT_3d_stuff(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "3D"

	def draw(self, context):
		
		layout = self.layout
		
		col = layout.column(align=True)
		col.operator("ax.obj_backup", icon='DUPLICATE')
		col.operator("ax.duplicates_to_instances", icon='MOD_INSTANCE')
		# col.operator("ax.hybrid_subdiv", icon='MOD_SUBSURF')
		
		if context.scene.fulcrum.dev:
			col = layout.column(align=True)
			col.operator("ax.locate_vertex", icon='VERTEXSEL')
			col.operator("ax.locate_vertices", icon='SNAP_VERTEX')

class AX_PT_camera(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Camera"

	def draw(self, context):

		layout = self.layout
		layout.operator("ax.frame_range_from_cam", icon='ARROW_LEFTRIGHT')
		layout.prop(context.area.spaces.active, "lock_camera")
		
		col = layout.column(align=True)
		col.operator("ax.isometric_setup", icon='FILE_3D')  # VIEW_ORTHO  FILE_3D
		col.operator("ax.dof_setup", icon='CAMERA_DATA')
		col.operator("ax.projection_setup", icon='MOD_UVPROJECT')  # STICKY_UVS_LOC  UV  MOD_UVPROJECT  IMAGE_PLANE

		# ARROW_LEFTRIGHT
		col = layout.column(align=True)
		col.label(text = "Set Passepartout:")
		row = col.row(align=True)
		passepartout_none = row.operator("ax.passepartout", text="None")
		passepartout_none.alpha = 0.0
		passepartout_normal = row.operator("ax.passepartout", text="0.8")
		passepartout_normal.alpha = 0.8
		passepartout_full = row.operator("ax.passepartout", text="Full")
		passepartout_full.alpha = 1.0

class AX_PT_3d_axis_selection(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Axis Selection"
	bl_options = {'DEFAULT_CLOSED'}

	def draw(self, context):
		
		layout = self.layout

		keymap_items = bpy.data.window_managers["WinMan"].keyconfigs["Blender user"].keymaps['3D View'].keymap_items

		for item in keymap_items:
			if item.idname == 'transform.translate' and item.type == 'G':
				transform = item
				break
		col = layout.column(align=True)
		col.label(text="Translation:")  # CON_LOCLIKE
		row = col.row(align=True)
		row.prop(transform.properties, "constraint_axis", text="", toggle=True, slider=True)

		for item in keymap_items:
			if item.idname == 'transform.rotate' and item.type == 'R':
				transform = item
				break
		col = layout.column(align=True)
		col.label(text="Rotation:")  # CON_ROTLIKE
		row = col.row(align=True)
		row.prop(transform.properties, "constraint_axis", text="", toggle=True, slider=True)

class AX_PT_utility_3d(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Utility"

	def draw (self, context):
		layout = self.layout
		
		col = layout.column(align=True)
		col.operator("ax.open_blend_dir", icon='FILE_BACKUP')
		col.operator("ax.open_script_dir", icon='SCRIPT')  # FOLDER_REDIRECT  SCRIPT
		
		layout.operator("wm.console_toggle", icon='CONSOLE')