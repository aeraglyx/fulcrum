import bpy
import bmesh

class AX_OT_locate_vertex(bpy.types.Operator):

	bl_idname = "ax.locate_vertex"
	bl_label = "Locate Vertex"
	bl_description = "Select a vertex based on its ID"
	bl_options = {'REGISTER', 'UNDO'}
	
	@classmethod
	def poll(cls, context):
		return True
	
	index: bpy.props.IntProperty(
		name = "Index",
		min = 0, default = 0
	)

	def execute(self, context):

		obj = context.active_object
		bm = bmesh.new()
		bm.from_mesh(obj.data)
		bm.transform(obj.matrix_world)
		verts = bm.verts

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