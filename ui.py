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
		row.operator("ax.anim_time_limit", icon = 'RENDER_ANIMATION')

		layout.operator("ax.benchmark", icon = 'NONE')
		layout.operator("ax.render_to_new_slot", icon = 'RENDER_RESULT')

class AX_PT_data(bpy.types.Panel):
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "data"
	bl_label = "Fulcrum"

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.operator("ax.vert_group_2_col", icon = 'COLOR')

class AX_PT_physics(bpy.types.Panel):
	
	bl_space_type = "PROPERTIES"
	bl_region_type = "WINDOW"
	bl_context = "physics"
	bl_label = "Fulcrum"

	def draw(self, context):
		layout = self.layout
		row = layout.row()
		row.operator("ax.cloth_vert_mass", icon = 'MOD_VERTEX_WEIGHT')


# --- NODE EDITOR ---
		
class AX_PT_node_tools(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Node Tools"

	def draw(self, context):
		layout = self.layout

		col = layout.column(align = True)
		selected = col.operator("ax.reset_node_color", text = "Reset Selected", icon = 'COLOR')  # FILE_REFRESH  COLOR  RESTRICT_COLOR_OFF
		selected.all = False
		all = col.operator("ax.reset_node_color", text = "Reset All", icon = 'GROUP_VCOL')
		all.all = True

		col = layout.column(align = True)
		col.operator("ax.find_inputs", icon = 'COLLECTION_COLOR_04')  # icon = 'NODE'
		col.operator("ax.node_flow", icon = 'COLLECTION_COLOR_05')  # icon = 'NODETREE'  # STROKE  ANIM_DATA  TRACKING
		col.operator("ax.unused_nodes", icon = 'COLLECTION_COLOR_01')  # icon = 'PLUGIN'
		
		col = layout.column(align = True)
		col.operator("ax.center_nodes", icon = 'ANCHOR_CENTER')
		col.operator("ax.nodes_to_grid", icon = 'SNAP_GRID')

		col = layout.column(align = True)
		row = col.row(align = True)
		row.operator("ax.version_encode", text = "Encode", icon = 'SYSTEM')
		row.operator("ax.version_decode", text = "Decode", icon = 'ZOOM_ALL')
		
		col = layout.column(align = True)
		row = col.row(align = True)
		row.operator("ax.copy_nodes", text = "Copy", icon = 'COPYDOWN')
		row.operator("ax.paste_nodes", text = "Pasta", icon = 'PASTEDOWN')

		layout.operator("ax.set_render_passes", icon = 'NODE_COMPOSITING')  # XXX
		
class AX_PT_optimization(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Optimization"
	
	@classmethod
	def poll(cls, context):
		in_shader_editor = context.space_data.tree_type == 'ShaderNodeTree'
		return in_shader_editor

	def draw(self, context):
		
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

class AX_PT_utility_node(bpy.types.Panel):
	
	bl_space_type = "NODE_EDITOR"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Utility"

	def draw(self, context):
		layout = self.layout

		layout.operator("wm.console_toggle", icon = 'CONSOLE')


# --- VIEW 3D ---

class AX_PT_ease_of_access(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Ease of Access"

	def draw(self, context):
		
		layout = self.layout

		col = layout.column(align = True)
		col.prop(context.scene.render, "use_motion_blur")
		col.prop(context.scene.render, "film_transparent")
		layout.prop(context.scene.view_settings, "view_transform", text = "")
		layout.prop(context.scene.tool_settings, "use_keyframe_insert_auto")

		layout.label(text = "DON'T PANIC!")

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

class AX_PT_3d_stuff(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "3D Stuff"

	def draw(self, context):
		
		layout = self.layout
		
		col = layout.column(align = True)
		col.operator("ax.hybrid_subdiv", icon = 'MOD_SUBSURF')
		col.operator("ax.set_auto_smooth", icon = 'MATSHADERBALL')
		
		col = layout.column(align = True)
		col.operator("ax.locate_vertex", icon = 'VERTEXSEL')
		col.operator("ax.locate_vertices", icon = 'SNAP_VERTEX')

class AX_PT_camera_stuff(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Camera Stuff"

	def draw(self, context):
		
		layout = self.layout
		
		col = layout.column(align = True)
		col.operator("ax.isometric_setup", icon = 'FILE_3D')  # VIEW_ORTHO  FILE_3D
		# maybe 2 buttons, one with "alignment" 0.0, one with 1.0
		col.operator("ax.dof_setup", icon = 'CAMERA_DATA')
		col.operator("ax.projection_setup", icon = 'MOD_UVPROJECT')  # STICKY_UVS_LOC  UV  MOD_UVPROJECT  IMAGE_PLANE
		
		# ARROW_LEFTRIGHT
		col = layout.column(align = True)
		col.label(text = "Set Passepartout:")
		row = col.row(align = True)
		passepartout_none = row.operator("ax.passepartout", text = "None")
		passepartout_none.alpha = 0.0
		passepartout_normal = row.operator("ax.passepartout", text = "0.75")
		passepartout_normal.alpha = 0.75
		passepartout_full = row.operator("ax.passepartout", text = "Full")
		passepartout_full.alpha = 1.0

		col = layout.column(align = True)
		col.label(text = "Set Resolution:")
		row = col.row(align = True)
		half = row.operator("ax.set_resolution", text = "Half")
		half.width = 960
		full_hd = row.operator("ax.set_resolution", text = "FHD")
		full_hd.width = 1920
		ultra_hd = row.operator("ax.set_resolution", text = "UHD")
		ultra_hd.width = 3840

		col = layout.column(align = True)
		col.label(text = "Set Aspect Ratio:")
		row = col.row(align = True)
		square = row.operator("ax.set_aspect_ratio", text = "1.00")
		square.aspect_ratio = 1.0
		sixteen_by_nine = row.operator("ax.set_aspect_ratio", text = "1.78")
		sixteen_by_nine.aspect_ratio = 1.777777
		two_to_one = row.operator("ax.set_aspect_ratio", text = "2.00")
		two_to_one.aspect_ratio = 2.0
		cinemascope = row.operator("ax.set_aspect_ratio", text = "2.40")
		cinemascope.aspect_ratio = 2.4


		
		layout.prop(context.area.spaces.active, "lock_camera")

		layout.operator("ax.frame_range_from_cam", icon = 'ARROW_LEFTRIGHT')

class AX_PT_utility_3d(bpy.types.Panel):
	
	bl_space_type = "VIEW_3D"
	bl_region_type = "UI"
	bl_category = "Fulcrum"
	bl_label = "Utility"

	def draw (self, context):
		
		layout = self.layout
		layout.operator("wm.console_toggle", icon = 'CONSOLE')
		
		col = layout.column(align = True)
		col.operator("ax.open_script_dir", icon = 'SCRIPT')  # FOLDER_REDIRECT  SCRIPT
		col.operator("ax.open_blend_dir", icon = 'FILE_BLEND')  # FILE_BLEND  BLENDER