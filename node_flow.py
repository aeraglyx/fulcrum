import bpy

class AX_OT_node_flow(bpy.types.Operator):
    
    bl_idname = "ax.node_flow"
    bl_label = "Dependencies"
    bl_description = "Show all nodes used by the selected nodes"
    
    @classmethod
    def poll(cls, context):
        return bpy.context.active_node != None

    def execute(self, context):

        nodes = bpy.context.material.node_tree.nodes
        # links = bpy.context.material.node_tree.links
        selected = bpy.context.selected_nodes
        #active = bpy.context.active_node
        #output_node = nodes.get("Material Output")

        for node in nodes:
            node.use_custom_color = False

        def func(node_selected):  # TODO improve efficiency
            for input in node_selected.inputs:
                for link in input.links:
                    node = link.from_node
                    node.use_custom_color = True
                    node.color = [0.2,0.45,0.6]
                    func(node)
        
        for node in selected:
            func(node)

        return {'FINISHED'}




        # TODO interactive mode
        
        # owner = bpy.context.material.node_tree

        # def func(active):
        #     for input in active.inputs:
        #         for link in input.links:
        #             node = link.from_node
            
        #             node.use_custom_color = True
        #             node.color = [0.2,0.45,0.6]
        #             f(node)
        
        # subscribe_to = active
        
        # bpy.msgbus.subscribe_rna(
        #     key = subscribe_to,
        #     owner = owner,
        #     args = (active,),
        #     notify = func,
        # )
          
        # # ... to clear
        # # bpy.msgbus.clear_by_owner(handle)