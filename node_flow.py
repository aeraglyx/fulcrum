import bpy

class AX_OT_node_flow(bpy.types.Operator):
    
    bl_idname = "ax.node_flow"
    bl_label = "Dependencies"
    bl_description = "Show all nodes used by the selected nodes"
    
    @classmethod
    def poll(cls, context):
        return bool(context.selected_nodes)

    def execute(self, context):

        nodes = context.material.node_tree.nodes
        selected = context.selected_nodes
        #active = context.active_node
        #output_node = nodes.get("Material Output")

        for node in nodes:
            node.use_custom_color = False

        out = []
        def func(node_current):
            for input in node_current.inputs:
                for link in input.links: # TODO links plural ?
                    node = link.from_node
                    if node not in out:
                        out.append(node)
                        func(node)
        for node in selected:
            func(node)
        
        for node in out:
            node.use_custom_color = True
            node.color = [0.2,0.45,0.6]
            # node.color = [0.65,0.29,0.32]

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


class AX_OT_unused_nodes(bpy.types.Operator):
    
    bl_idname = "ax.unused_nodes"
    bl_label = "Dependencies"
    bl_description = "Show all nodes used by the selected nodes"
    
    @classmethod
    def poll(cls, context):
        return bool(context.selected_nodes)

    def execute(self, context):

        nodes = context.material.node_tree.nodes
        selected = context.selected_nodes
        #active = context.active_node
        output_node = nodes.get("Material Output")

        for node in nodes:
            node.use_custom_color = False

        used = []
        def func(node_current):
            for input in node_current.inputs:
                for link in input.links:
                    node = link.from_node
                    if node not in used:
                        used.append(node)
                        func(node)
        func(output_node)
        
        unused = [node for node in nodes if node not in used]

        for node in unused:
            node.use_custom_color = True
            # node.color = [0.2,0.45,0.6]
            node.color = [0.65,0.29,0.32]

        return {'FINISHED'}