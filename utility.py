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

		obj = context.active_object
		bm = bmesh.new()
		bm.from_mesh(obj.data)
		bm.transform(obj.matrix_world)
		verts = bm.verts  # TODO select just like AX_OT_locate_vertices ?

		vert_found = None
		if self.index < len(verts):

			for vert in verts:
				if vert.index == self.index:
					vert_found = vert
					break
		
		if not vert_found:
			self.report({'WARNING'}, f"Index out of range.")
			return {'CANCELLED'}
		
		context.scene.cursor.location = vert_found.co

		pos = [round(x, 2) for x in list(vert_found.co)]
		self.report({'INFO'}, f"Found vertex {self.index} at {pos}.")
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

		obj = context.active_object
		verts = obj.data.vertices

		indices = re.findall(r"\d+", self.indices_str)
		indices = [int(i) for i in indices]

		mode_prev = context.object.mode
		bpy.ops.object.mode_set(mode = 'OBJECT')

		found = 0
		for vert in verts:
			if vert.index in indices:
				vert.select = True
				found += 1
			else:
				vert.select = False
		
		bpy.ops.object.mode_set(mode = mode_prev)

		self.report({'INFO'}, f"Found {found} out of {len(indices)} vertices.")
		return {'FINISHED'}
	
	def invoke(self, context, event):
		wm = context.window_manager
		return wm.invoke_props_dialog(self)

	def draw(self, context):
		layout = self.layout
		layout.prop(self, "indices_str")