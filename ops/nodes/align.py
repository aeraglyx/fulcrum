import itertools

import bpy
import mathutils

from .utils import socket_loc, node_height, node_width, node_center, node_intersection


class FULCRUM_OT_align_nodes(bpy.types.Operator):
    # layered graph drawing

    bl_idname = "fulcrum.align_nodes"
    bl_label = "Align Nodes"
    bl_description = "Automatically align all the nodes preceding the selection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    test: bpy.props.FloatProperty(
        name="Test",
        description="Number of total subdivisions",
        soft_min=0.0,
        default=0.25,
        soft_max=8.0,
    ) # type: ignore
    spacing: bpy.props.IntVectorProperty(
        name="Spacing",
        description="Spacing between nodes",
        min=0,
        default=(40, 20),
        soft_max=100,
        size=2,
    ) # type: ignore

    def execute(self, context):
        # if node_tree.type == 'COMPOSITING':
        # 	nodes = context.scene.node_tree.nodes
        # print(context.space_data)
        # print(context.space_data.type)
        if context.space_data.tree_type == "CompositorNodeTree":
            nodes = context.scene.node_tree.nodes
        else:
            nodes = context.space_data.edit_tree.nodes  # BUG doesn't work in compositor
        # bpy.context.space_data.edit_tree
        # nodes = context.active_node.id_data.nodes
        levels = {node: 0 for node in nodes}

        def figure_out_levels(node_current, level_current):
            inputs = (x for x in node_current.inputs if x.enabled)
            for input in inputs:
                for link in input.links:
                    node = link.from_node
                    if levels[node] <= level_current:
                        levels[node] = level_current + 1
                        figure_out_levels(node, level_current + 1)

        root_node = context.active_node
        figure_out_levels(root_node, 0)

        level_current = 1
        x = 0
        while True:
            nodes = [node for (node, level) in levels.items() if level == level_current]
            if not nodes:
                break
            orders = []
            for node in nodes:
                node.select = True
                weight_total = 0.0
                pos_thingy = 0.0
                outputs = (x for x in node.outputs if x.enabled and not x.hide)
                for output in outputs:
                    links = (
                        x for x in output.links
                        if x.to_socket.enabled and not x.to_socket.hide
                    )
                    for (
                        link
                    ) in (
                        links
                    ):  # [link for link in output.links if link.to_socket.enabled or not link.to_socket.hide]
                        level_diff = level_current - levels[link.to_node]
                        weight = 2 ** (self.test * (1 - level_diff))
                        weight_total += weight
                        pos_thingy += socket_loc(link.to_socket)[1] * weight
                orders.append(pos_thingy / weight_total)
            nodes = [
                node for _, node in sorted(
                    zip(orders, nodes), key=lambda x: x[0], reverse=True
                )
            ]
            spacing_y = self.spacing[1]
            full_height = sum([node_height(node) for node in nodes]) + spacing_y * (len(nodes) - 1)
            x -= max([node_width(node) for node in nodes]) + self.spacing[0]
            y = full_height * 0.5
            for node in nodes:
                node.location = [x, y]
                y -= node_height(node) + spacing_y
            level_current += 1

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "spacing")
        layout.prop(self, "test")


class FULCRUM_OT_align_nodes_v2(bpy.types.Operator):
    # layered graph drawing

    bl_idname = "fulcrum.align_nodes_v2"
    bl_label = "Align Nodes (Force Directed)"
    bl_description = "Automatically align all the nodes preceding the selection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    link_length: bpy.props.IntProperty(
        name="Link Length",
        description="...",
        min=0,
        default=128,
        soft_max=1024,
    ) # type: ignore
    spacing: bpy.props.IntVectorProperty(
        name="Spacing",
        description="Spacing between nodes",
        min=0,
        default=(40, 20),
        soft_max=100,
        size=2,
    ) # type: ignore
    angle: bpy.props.FloatProperty(
        name="Angle",
        description="...",
        min=0.0,
        default=1.25,
        soft_max=4.0,
    ) # type: ignore
    iter: bpy.props.IntProperty(
        name="Iterations",
        description="Number of iterations",
        min=0,
        default=1,
        soft_max=1024,
    ) # type: ignore
    step_size: bpy.props.FloatProperty(
        name="Step Size",
        description="...",
        min=0.0,
        default=0.1,
        soft_max=1.0,
    ) # type: ignore
    repulsion: bpy.props.FloatProperty(
        name="repulsion",
        description="...",
        soft_min=0.0,
        default=1.0,
        soft_max=4.0,
    ) # type: ignore
    spring: bpy.props.FloatProperty(
        name="spring",
        description="...",
        soft_min=0.0,
        default=1.0,
        soft_max=4.0,
    ) # type: ignore

    def execute(self, context):
        # if node_tree.type == 'COMPOSITING':
        # 	nodes = context.scene.node_tree.nodes
        # print(context.space_data)
        # print(context.space_data.type)

        # def node_intersection(node_1, node_2):
        # 	pass

        tree = context.space_data.edit_tree
        # BUG: doesn't work in compositor
        nodes = tree.nodes
        links = tree.links
        # bpy.context.space_data.edit_tree
        # nodes = context.active_node.id_data.nodes
        # intersection = node_intersection(context.selected_nodes[0], context.selected_nodes[1])
        # self.report({'INFO'}, f'{intersection}')

        for _ in range(self.iter):
            # TODO cooling factor
            node_pairs = itertools.combinations(nodes, 2)
            force_field = {node: mathutils.Vector((0.0, 0.0)) for node in nodes}

            for node_pair in node_pairs:
                # print(node_pair)
                force = mathutils.Vector((0.0, 0.0))
                direction = node_center(node_pair[1]) - node_center(node_pair[0])

                intersection = node_intersection(node_pair[0], node_pair[1])
                print(intersection)
                # self.report({'INFO'}, f'{get_node_name(node_a)} - {intersection}')
                if intersection:
                    intersect_size = intersection[1]
                    # direction = node_center(node_a) - node_center(node_b)
                    # if abs(direction.x) < 0.1 and abs(direction.y) < 0.1:

                    if abs(direction.x) < 0.1:
                        factor = intersect_size.y / abs(direction.y)
                    elif abs(direction.y) < 0.1:
                        factor = intersect_size.y / abs(direction.x)
                    else:
                        factor = min(
                            intersect_size.x / abs(direction.x),
                            intersect_size.y / abs(direction.y),
                        )
                    force += -factor * 0.5 * direction

                repulsion = (
                    1.0 * direction.normalized() / (direction.length / 200) ** 2.0
                )
                force -= repulsion * self.repulsion
                force_field[node_pair[0]] += force
                force_field[node_pair[1]] -= force

            for link in links:
                node_a = link.from_node
                node_b = link.to_node
                loc_a = socket_loc(link.from_socket)
                loc_b = socket_loc(link.to_socket)
                dir = loc_b - loc_a
                # angle = dir.angle_signed(mathutils.Vector((1.0, 0.0)), 0.0)
                force = (
                    0.5
                    * (mathutils.Vector((dir.length, 0)) - self.angle * dir)
                    * self.spring
                    * self.step_size
                )
                # force = 0.5 * dir.normalized() * (self.link_length - dir.length)
                force_field[node_a] -= force
                force_field[node_b] += force

            for node, force in force_field.items():
                node.location += force

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.prop(self, "iter")
        layout.prop(self, "step_size")
        layout.prop(self, "spring")
        layout.prop(self, "repulsion")
        layout.prop(self, "angle")


class FULCRUM_OT_align_nodes_v3(bpy.types.Operator):
    # layered graph drawing

    bl_idname = "fulcrum.align_nodes_v3"
    bl_label = "Align Nodes (FD v3)"
    bl_description = "Automatically align all the nodes"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    spacing: bpy.props.IntVectorProperty(
        name="Spacing",
        description="Spacing between nodes",
        min=0,
        default=(40, 20),
        soft_max=100,
        size=2,
    ) # type: ignore
    angle: bpy.props.FloatProperty(
        name="Angle",
        description="...",
        min=0.0,
        default=1.25,
        soft_max=4.0,
    ) # type: ignore
    iter: bpy.props.IntProperty(
        name="Iterations",
        description="Number of iterations",
        min=0,
        default=1,
        soft_max=1024,
    ) # type: ignore
    step_size: bpy.props.FloatProperty(
        name="Step Size",
        description="...",
        min=0.0,
        default=0.1,
        soft_max=1.0,
    ) # type: ignore
    repulsion: bpy.props.FloatProperty(
        name="repulsion",
        description="...",
        soft_min=0.0,
        default=1.0,
        soft_max=4.0,
    ) # type: ignore
    spring: bpy.props.FloatProperty(
        name="spring",
        description="...",
        soft_min=0.0,
        default=1.0,
        soft_max=4.0,
    ) # type: ignore

    def execute(self, context):
        tree = context.space_data.edit_tree  # BUG doesn't work in compositor
        nodes = tree.nodes
        links = tree.links
        # self.report({'INFO'}, f'{intersection}')

        for _ in range(self.iter):
            # TODO cooling factor
            node_pairs = itertools.combinations(nodes, 2)
            force_field = {node: mathutils.Vector((0.0, 0.0)) for node in nodes}

            for node_pair in node_pairs:
                # print(node_pair)
                force = mathutils.Vector((0.0, 0.0))
                direction = node_center(node_pair[1]) - node_center(node_pair[0])

                intersection = node_intersection(node_pair[0], node_pair[1])
                print(intersection)
                # self.report({'INFO'}, f'{get_node_name(node_a)} - {intersection}')
                if intersection:
                    intersect_size = intersection[1]
                    # direction = node_center(node_a) - node_center(node_b)
                    # if abs(direction.x) < 0.1 and abs(direction.y) < 0.1:

                    if abs(direction.x) < 0.1:
                        factor = intersect_size.y / abs(direction.y)
                    elif abs(direction.y) < 0.1:
                        factor = intersect_size.y / abs(direction.x)
                    else:
                        factor = min(
                            intersect_size.x / abs(direction.x),
                            intersect_size.y / abs(direction.y),
                        )
                    force += -factor * 0.5 * direction

                repulsion = (
                    1.0 * direction.normalized() / (direction.length / 200) ** 2.0
                )
                force -= repulsion * self.repulsion
                force_field[node_pair[0]] += force
                force_field[node_pair[1]] -= force

            for link in links:
                node_a = link.from_node
                node_b = link.to_node
                loc_a = socket_loc(link.from_socket)
                loc_b = socket_loc(link.to_socket)
                dir = loc_b - loc_a
                force = (
                    0.5
                    * (mathutils.Vector((dir.length, 0)) - self.angle * dir)
                    * self.spring
                    * self.step_size
                )
                force_field[node_a] -= force
                force_field[node_b] += force

            for node, force in force_field.items():
                node.location += force

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        # col = layout.column(align = True)
        layout.prop(self, "iter")
        layout.prop(self, "step_size")
        layout.prop(self, "spring")
        layout.prop(self, "repulsion")
        layout.prop(self, "angle")


class FULCRUM_OT_center_nodes(bpy.types.Operator):
    bl_idname = "fulcrum.center_nodes"
    bl_label = "Center Nodes"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    def execute(self, context):
        nodes = context.space_data.edit_tree.nodes
        # FIXME takes nodes inside groups as well (does it?)

        node_center = mathutils.Vector((0, 0))
        n = 0
        for node in nodes:
            if node.type == "FRAME" or node.type == "REROUTE":
                continue
            node_center_offset = node.dimensions * mathutils.Vector((0.5, -0.5))
            node_center += node.location + node_center_offset
            n += 1

        node_center /= n

        for node in nodes:
            if node.type == "FRAME":  # TODO move frames, not their children
                continue
            node.location -= node_center

        bpy.ops.node.view_all()

        return {"FINISHED"}


class FULCRUM_OT_nodes_to_grid(bpy.types.Operator):
    bl_idname = "fulcrum.nodes_to_grid"
    bl_label = "Nodes to Grid"
    bl_description = ""

    @classmethod
    def poll(cls, context):
        return hasattr(context, "selected_nodes")

    def execute(self, context):
        selected = context.selected_nodes
        for node in selected:
            node.location.x = int(node.location.x / 10) * 10
            node.location.y = int(node.location.y / 10) * 10
        return {"FINISHED"}
