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

        nodes_out = []
        def func(node_current):
            for input in (x for x in node_current.inputs if x.enabled):
                for link in input.links: # TODO links plural ? link limit
                    node = link.from_node
                    if node not in nodes_out:
                        nodes_out.append(node)
                        func(node)
        for node in selected:
            func(node)
        
        for node in nodes_out:
            node.use_custom_color = True
            node.color = [0.2,0.45,0.6]
            # node.color = [0.65,0.29,0.32]

        return {'FINISHED'}


class AX_OT_unused_nodes(bpy.types.Operator):
    
    bl_idname = "ax.unused_nodes"
    bl_label = "Unused Nodes"
    bl_description = "Show all nodes used by the selected nodes"
    
    @classmethod
    def poll(cls, context):
        return bool(context.selected_nodes)

    def execute(self, context):

        nodes = context.material.node_tree.nodes
        links = context.material.node_tree.links
        selected = context.selected_nodes
        #active = context.active_node
        output_node = nodes.get("Material Output")

        for node in nodes:
            node.use_custom_color = False

        used = []
        def func(node_current):
            for input in (x for x in node_current.inputs if x.enabled):
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


class AX_OT_find_inputs(bpy.types.Operator):
    
    bl_idname = "ax.find_inputs"
    bl_label = "Find Inputs"
    bl_description = "Show all nodes used by the selected nodes"
    
    @classmethod
    def poll(cls, context):
        return bool(context.selected_nodes)

    def execute(self, context):

        nodes = context.material.node_tree.nodes
        selected = context.selected_nodes
        active = context.active_node

        for node in nodes:
            node.use_custom_color = False
        
        # TODO make func that finds socket locations

        # NOTE bpy.ops.node.delete_reconnect()
        


        # label > prop. name > name
        # TODO regex .001
        def get_node_name(node):
            """Get node name that is visible to user"""
            if bool(node.label):
                return node.label
            elif hasattr(node, "node_tree"):
                return node.node_tree.name
            else:
                return node.name

        offset_bottom_left = 15
        offset_top_right = 34
        gap = 21
        reroute_offset_y = 19
        char_mult = 6
        offset_left = 32
        offset_right = 8

        nodes_out = []
        select_later = []
        def get_input_node(node_current):
            for input in node_current.inputs:
                for link in input.links:
                    node = link.from_node
                    if node.type == 'REROUTE':
                        select_later.append(node)
                        get_input_node(node)
                    else:
                        last_node = node_current # TODO
                        left_node_name = get_node_name(node)
                        nodes_out.append(node)
        
        for node_orig in selected: # TODO maybe just active
            for i, input in enumerate((x for x in node_orig.inputs if x.enabled)):
                right_socket_name = input.name # TODO only if used
                for link in input.links:
                    node = link.from_node
                    if node.type == 'REROUTE':
                        select_later.append(node)
                        get_input_node(node) # TODO maybe try while
                    else:
                        left_socket_name = link.from_socket.name  # node.outputs[i].name
                        # last_node = node_current # TODO
                        left_loc_x = node.location.x
                        left_loc_y = node.location.y
                        right_loc_x = node_orig.location.x
                        right_loc_y = node_orig.location.y

                        dist_sq = (right_loc_x - left_loc_x)**2 + (right_loc_y - left_loc_y)**2
                        if dist_sq > 1_000_000:  # if distance is more than 1000
                            
                            # if contender_exists:
                            # else:
                            reroute_left = nodes.new(type = 'NodeReroute')
                            reroute_right = nodes.new(type = 'NodeReroute')

                            left_node_name = get_node_name(node)
                            right_node_name = get_node_name(node_orig)
                            label_left = f"> {right_node_name} > {right_socket_name}"
                            label_right = f"{left_node_name} > {left_socket_name} >"
                            reroute_left.label = label_left
                            reroute_right.label = label_right
                            reroute_left.mute = True
                            reroute_right.mute = True

                            left_width = node.dimensions.x
                            right_height = node_orig.dimensions.y

                            # left - outputs
                            left_x = left_loc_x + left_width + offset_left
                            left_y = left_loc_y - offset_top_right - i*gap - reroute_offset_y # FIXME i should be 
                            
                            # right - inputs
                            n_in = len((x for x in node_orig.inputs if x.enabled)) # BUG links are still there in bg, also inputs of left kinda
                            right_chars = len(label_right)
                            right_x = right_loc_x - right_chars*char_mult - offset_right
                            right_y = right_loc_y - right_height + offset_bottom_left + (n_in - i - 1)*gap - reroute_offset_y
                            # TODO precompute what can be reused ^

                            reroute_left.location.x = left_x
                            reroute_left.location.y = left_y
                            reroute_right.location.x = right_x
                            reroute_right.location.y = right_y
                        
                        nodes_out.append(node)

        # set custom node color
        for node in nodes_out:
            node.use_custom_color = True
            node.color = [0.3,0.6,0.3]
        
        # select reroutes
        for node in select_later:
            node.select = True

        return {'FINISHED'}