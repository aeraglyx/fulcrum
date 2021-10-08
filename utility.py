import bpy
import bmesh
import re

class AX_OT_locate_vertex(bpy.types.Operator):

	bl_idname = "ax.locate_vertex"
	bl_label = "Locate Vertex"
	bl_description = "Select a vertex based on its ID"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object
	
	index: bpy.props.IntProperty(
		name = "Index",
		min = 0, default = 0
	)

	def execute(self, context):

		mode_prev = context.object.mode
		bpy.ops.object.mode_set(mode = 'EDIT')

		statistics_str = context.scene.statistics(context.view_layer)
		total_verts = int(re.search("Verts:\d+/(\d+)", statistics_str).groups()[0])
		
		if self.index < total_verts:  # len(verts)
			
			obj = context.active_object
			bm = bmesh.from_edit_mesh(obj.data)

			for vert in bm.verts:
				if vert.index == self.index:
					vert_found = vert
					vert_found.select_set(True)
				else:
					vert.select_set(False)
			
			bm.select_flush_mode()
			bmesh.update_edit_mesh(obj.data)
			
			location = obj.matrix_world @ vert_found.co
			context.scene.cursor.location = location

			pos = [round(x, 2) for x in list(location)]
			self.report({'INFO'}, f"Found vertex {self.index} at {pos}.")
			
		else:
			self.report({'WARNING'}, f"Index out of range.")
			return {'CANCELLED'}
		
		bpy.ops.object.mode_set(mode = mode_prev)

		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "index")


class AX_OT_locate_vertices(bpy.types.Operator):

	bl_idname = "ax.locate_vertices"
	bl_label = "Locate Vertices"
	bl_description = "Select vertices based on a list of IDs"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return context.active_object
	
	indices_str: bpy.props.StringProperty(
		name = "Indices",
		default = ""
	)

	def execute(self, context):

		mode_prev = context.object.mode
		bpy.ops.object.mode_set(mode = 'EDIT')

		obj = context.active_object
		bm = bmesh.from_edit_mesh(obj.data)
		verts = bm.verts

		indices = re.findall(r"\d+", self.indices_str)
		indices = [int(i) for i in indices]
		indices = list(set(indices))

		found = 0
		for vert in verts:
			if vert.index in indices:
				vert.select_set(True)
				found += 1
			else:
				vert.select_set(False)
		
		bm.select_flush_mode()
		bmesh.update_edit_mesh(obj.data)

		self.report({'INFO'}, f"Found {found} out of {len(indices)} vertices.")
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "indices_str")