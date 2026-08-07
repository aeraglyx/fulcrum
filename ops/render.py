import os
import re

import bpy
from bpy_extras.io_utils import ImportHelper

from ..functions import version_up


class FULCRUM_OT_anim_time_limit(bpy.types.Operator):
    bl_idname = "fulcrum.anim_time_limit"
    bl_label = "Animation Time Limit"
    bl_description = "Calculate and set Time Limit in Cycles"
    bl_options = {"REGISTER", "UNDO"}
    COMPAT_ENGINES = {"CYCLES"}

    @classmethod
    def poll(cls, context):
        if context.scene.render.engine not in cls.COMPAT_ENGINES:
            cls.poll_message_set("Works only in Cycles")
            return False
        return True

    time_needed: bpy.props.FloatProperty(
        name="Time",
        description="How much time you want the render to take",
        unit="TIME_ABSOLUTE",
        min=0,
        default=3600,
        soft_max=86400,
        step=6000,
    ) # type: ignore
    multiplier: bpy.props.FloatProperty(
        name="Multiplier",
        description="Decrease for extra margin, increase when using multiple machines",
        soft_min=0.0,
        default=1.0,
        soft_max=10.0,
        step=5,
    ) # type: ignore

    def execute(self, context):
        start = context.scene.frame_start
        end = context.scene.frame_end
        step = context.scene.frame_step
        frames = (end - start + 1) // step

        time_limit = self.time_needed * self.multiplier / frames
        context.scene.cycles.time_limit = time_limit

        self.report({"INFO"}, f"Time Limit set to {time_limit:.2f}s per frame")
        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "time_needed")
        col.prop(self, "multiplier")


# TODO clear empty slots


def check_if_render_slot_is_used(slot):
    tmp_path = os.path.join(bpy.path.abspath("//"), "tmp_img.png")

    try:
        bpy.data.images["Render Result"].save_render(filepath=tmp_path)
        # XXX probably only works for saved files ^
    except RuntimeError:
        return False

    os.remove(tmp_path)  # TODO delete only once at the end ?
    return True


class FULCRUM_OT_render_to_new_slot(bpy.types.Operator):
    bl_idname = "fulcrum.render_to_new_slot"
    bl_label = "Render to New Slot"
    bl_description = "Render to Next Available Render Slot"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        render_result = bpy.data.images["Render Result"]
        render_slots = render_result.render_slots

        render_slots.active = render_slots.new()
        render_slots.update()

        return {"FINISHED"}


class FULCRUM_OT_set_render_passes(bpy.types.Operator):
    bl_idname = "fulcrum.set_render_passes"
    bl_label = "(Set Render Passes)"
    bl_description = "Set-up compositor nodes."
    bl_options = {"REGISTER", "UNDO"}

    # @classmethod
    # def poll(cls, context):
    # 	return bool(context.scene.camera)

    combine_dir_ind: bpy.props.BoolProperty(
        name="Combine Direct & Indirect",
        description="",
        default=True,
    ) # type: ignore
    combine_light_color: bpy.props.BoolProperty(
        name="Combine Light & Color",
        description="",
        default=True,
    ) # type: ignore
    transparent: bpy.props.BoolProperty(
        name="Transparent",
        description="",
        default=True,
    ) # type: ignore
    denoise: bpy.props.BoolProperty(
        name="Denoise",
        description="",
        default=True,
    ) # type: ignore

    diffuse: bpy.props.BoolProperty(
        name="Diffuse",
        description="",
        default=True,
    ) # type: ignore
    glossy: bpy.props.BoolProperty(
        name="Glossy",
        description="",
        default=True,
    ) # type: ignore
    transmission: bpy.props.BoolProperty(
        name="Transmission",
        description="",
        default=False,
    ) # type: ignore
    volume: bpy.props.BoolProperty(
        name="Volume",
        description="",
        default=False,
    ) # type: ignore
    emit: bpy.props.BoolProperty(
        name="Emission",
        description="",
        default=False,
    ) # type: ignore
    env: bpy.props.BoolProperty(
        name="Environment",
        description="",
        default=False,
    ) # type: ignore
    shadow: bpy.props.BoolProperty(
        name="Shadow",
        description="",
        default=False,
    ) # type: ignore
    ao: bpy.props.BoolProperty(
        name="Ambient Occlusion",
        description="",
        default=False,
    ) # type: ignore
    shadow_catcher: bpy.props.BoolProperty(
        name="Shadow Catcher",
        description="",
        default=False,
    ) # type: ignore
    z: bpy.props.BoolProperty(
        name="Z",
        description="",
        default=True,
    ) # type: ignore
    mist: bpy.props.BoolProperty(
        name="Mist",
        description="",
        default=False,
    ) # type: ignore
    position: bpy.props.BoolProperty(
        name="Position",
        description="",
        default=False,
    ) # type: ignore
    normal: bpy.props.BoolProperty(
        name="Normal",
        description="",
        default=False,
    ) # type: ignore
    vector: bpy.props.BoolProperty(
        name="Vector",
        description="",
        default=False,
    ) # type: ignore
    uv: bpy.props.BoolProperty(
        name="UV",
        description="",
        default=False,
    ) # type: ignore

    crypto_asset: bpy.props.BoolProperty(
        name="Asset",
        description="",
        default=False,
    ) # type: ignore
    crypto_material: bpy.props.BoolProperty(
        name="Material",
        description="",
        default=False,
    ) # type: ignore
    crypto_object: bpy.props.BoolProperty(
        name="Object",
        description="",
        default=False,
    ) # type: ignore

    def execute(self, context):
        context.scene.render.film_transparent = self.transparent

        def set_render_passes(view_layer):
            view_layer.use_pass_combined = True

            view_layer.use_pass_diffuse_color = self.diffuse
            view_layer.use_pass_diffuse_direct = self.diffuse
            view_layer.use_pass_diffuse_indirect = self.diffuse

            view_layer.use_pass_glossy_color = self.glossy
            view_layer.use_pass_glossy_direct = self.glossy
            view_layer.use_pass_glossy_indirect = self.glossy

            view_layer.use_pass_transmission_color = self.transmission
            view_layer.use_pass_transmission_direct = self.transmission
            view_layer.use_pass_transmission_indirect = self.transmission

            view_layer.cycles.use_pass_volume_direct = self.volume
            view_layer.cycles.use_pass_volume_indirect = self.volume

            view_layer.use_pass_emit = self.emit
            view_layer.use_pass_environment = self.env
            view_layer.use_pass_shadow = self.shadow
            view_layer.use_pass_ambient_occlusion = self.ao
            view_layer.cycles.use_pass_shadow_catcher = self.shadow_catcher

            view_layer.use_pass_z = self.z
            view_layer.use_pass_mist = self.mist
            view_layer.use_pass_position = self.position
            view_layer.use_pass_normal = self.normal
            view_layer.use_pass_vector = self.vector
            view_layer.use_pass_uv = self.uv
            view_layer.cycles.denoising_store_passes = self.denoise

            view_layer.use_pass_cryptomatte_accurate = True
            view_layer.use_pass_cryptomatte_asset = self.crypto_asset
            view_layer.use_pass_cryptomatte_material = self.crypto_material
            view_layer.use_pass_cryptomatte_object = self.crypto_object

            view_layer.use_pass_object_index = False
            view_layer.use_pass_material_index = False

        def plug_socket(socket, name):
            socket_a = output_node.layer_slots.new(name)
            links.new(socket, socket_a)

        def mix_nodes(socket_a, socket_b, mode):
            mix_node = nodes.new(type="CompositorNodeMixRGB")
            mix_node.blend_type = mode
            mix_node.hide = True
            links.new(socket_a, mix_node.inputs[1])
            links.new(socket_b, mix_node.inputs[2])
            return mix_node.outputs[0]

        def make_link_1(input, output):
            socket_a = input_node.outputs[input]
            socket_b = output_node.layer_slots.new(output)
            links.new(socket_a, socket_b)

        def make_link_2(dir, ind, out):
            socket_dir = input_node.outputs[dir]
            socket_ind = input_node.outputs[ind]
            if self.combine_dir_ind:
                socket_light = mix_nodes(socket_dir, socket_ind, "ADD")
                plug_socket(socket_light, out + "_light")
            else:
                plug_socket(socket_dir, out + "_dir")
                plug_socket(socket_ind, out + "_ind")

        def make_link_3(dir, ind, col, out):
            socket_dir = input_node.outputs[dir]
            socket_ind = input_node.outputs[ind]
            socket_col = input_node.outputs[col]
            if self.combine_dir_ind:
                socket_light = mix_nodes(socket_dir, socket_ind, "ADD")
                if self.combine_light_color:
                    socket_combined = mix_nodes(socket_light, socket_col, "MULTIPLY")
                    plug_socket(socket_combined, out)
                else:
                    plug_socket(socket_light, out + "_light")
                    plug_socket(socket_col, out + "_col")
            else:
                if self.combine_light_color:
                    socket_dir = mix_nodes(socket_dir, socket_col, "MULTIPLY")
                    socket_ind = mix_nodes(socket_ind, socket_col, "MULTIPLY")
                    plug_socket(socket_dir, out + "_dir")
                    plug_socket(socket_ind, out + "_ind")
                else:
                    plug_socket(socket_dir, out + "_dir")
                    plug_socket(socket_ind, out + "_ind")
                    plug_socket(socket_col, out + "_col")

        bpy.context.scene.use_nodes = True
        nodes = context.scene.node_tree.nodes
        links = context.scene.node_tree.links

        view_layers = context.scene.view_layers
        for view_layer in view_layers:
            set_render_passes(view_layer)

            input_node = nodes.new(type="CompositorNodeRLayers")
            input_node.layer = view_layer.name
            input_node.show_preview = False

            output_node = nodes.new(type="CompositorNodeOutputFile")
            # nodes.active = output_node
            output_node.format.file_format = "OPEN_EXR"
            output_node.format.color_mode = "RGBA" if self.transparent else "RGB"
            output_node.format.color_depth = "32"
            output_node.format.exr_codec = "NONE"

            output_node.layer_slots.clear()

            for node in nodes:
                if node.type == "COMPOSITE":
                    links.new(input_node.outputs["Image"], node.inputs["Image"])

            make_link_1("Image", "rgba" if self.transparent else "rgb")

            if self.diffuse:
                make_link_3("DiffDir", "DiffInd", "DiffCol", "diff")
            if self.glossy:
                make_link_3("GlossDir", "GlossInd", "GlossCol", "gloss")
            if self.transmission:
                make_link_3("TransDir", "TransInd", "TransCol", "trans")
            if self.volume:
                make_link_2("VolumeDir", "VolumeInd", "trans")
            if self.emit:
                make_link_1("Emit", "emit")
            if self.env:
                make_link_1("Env", "env")
            if self.shadow:
                make_link_1("Shadow", "shadow")
            if self.ao:
                make_link_1("AO", "ao")
            if self.shadow_catcher:
                make_link_1("Shadow Catcher", "shadow_catcher")

            if self.z:
                make_link_1("Depth", "z")
            if self.mist:
                make_link_1("Mist", "mist")
            if self.position:
                make_link_1("Position", "position")
            if self.normal:
                make_link_1("Normal", "normal")
            if self.vector:
                make_link_1("Vector", "vector")
            if self.uv:
                make_link_1("UV", "uv")

            nodes.active = output_node
            bpy.ops.fulcrum.align_nodes()

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Main", align=True)
        col.prop(self, "combine_dir_ind")
        col.prop(self, "combine_light_color")
        col.prop(self, "transparent")
        col.prop(self, "denoise")

        col = layout.column(heading="Light", align=True)
        col.prop(self, "diffuse")
        col.prop(self, "glossy")
        col.prop(self, "transmission")
        col.prop(self, "volume")
        col.prop(self, "emit")
        col.prop(self, "env")

        col = layout.column(heading="Extra", align=True)
        col.prop(self, "shadow")
        col.prop(self, "ao")
        col.prop(self, "shadow_catcher")

        col = layout.column(heading="Data", align=True)
        col.prop(self, "z")
        col.prop(self, "mist")
        col.prop(self, "position")
        col.prop(self, "normal")
        col.prop(self, "vector")
        col.prop(self, "uv")

        col = layout.column(heading="Crypto", align=True)
        col.prop(self, "crypto_asset")
        col.prop(self, "crypto_material")
        col.prop(self, "crypto_object")


class FULCRUM_OT_set_output_directory(bpy.types.Operator, ImportHelper):
    bl_idname = "fulcrum.set_output_directory"
    bl_label = "Set Output Directory"
    bl_description = "Change path in Output Properties and selected File Output nodes"
    bl_options = {"REGISTER", "UNDO"}

    # https://docs.blender.org/api/current/bpy.types.FileSelectParams.html

    filepath = bpy.props.StringProperty(
        name="File Path", description="File path", maxlen=1024
    )

    @classmethod
    def poll(cls, context):
        if not hasattr(context, "space_data"):
            return False
        if not hasattr(context.space_data, "tree_type"):
            return False
        if context.space_data.tree_type != "CompositorNodeTree":
            return False
        if not hasattr(context, "selected_nodes"):
            return False
        return True

    def execute(self, context):
        old_name = os.path.split(context.scene.render.filepath)[1]
        new_dir, input_name = os.path.split(self.filepath)

        new_name = input_name if input_name else old_name
        # context.scene.render.filepath = os.path.join(new_dir, new_name)

        if not context.scene.node_tree:
            return {"FINISHED"}

        nodes = context.selected_nodes
        # nodes = context.scene.node_tree.nodes
        nodes = [node for node in nodes if node.type == "OUTPUT_FILE"]
        for node in nodes:
            node_filename = os.path.split(node.base_path)[1]
            node.base_path = os.path.join(new_dir, node_filename)

        return {"FINISHED"}

    def invoke(self, context, event):
        self.filepath = context.scene.render.filepath
        wm = context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}


class FULCRUM_OT_compositor_increment_version(bpy.types.Operator):
    bl_idname = "fulcrum.compositor_increment_version"
    bl_label = "Increment Version"
    bl_description = "Change filename for all File Output nodes"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not context.scene.node_tree:
            return {"FINISHED"}

        nodes = [
            node for node in context.scene.node_tree.nodes if node.type == "OUTPUT_FILE"
        ]
        for node in nodes:
            node_path, node_filename = os.path.split(node.base_path)
            node_filename = re.sub("_+$", "", node_filename)
            node.base_path = os.path.join(node_path, version_up(node_filename) + "_")
        # FIXME make sure all nodes have the same version

        return {"FINISHED"}


class FULCRUM_OT_compositor_output_path_to_node_name(bpy.types.Operator):
    bl_idname = "fulcrum.compositor_output_path_to_node_name"
    bl_label = "Path to Node Name"
    bl_description = "If the node path is '/path/to/render_', this will name the node to 'render' (useful for some render farms)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not context.scene.node_tree:
            return {"FINISHED"}

        nodes = context.selected_nodes or context.scene.node_tree.nodes
        nodes = [node for node in nodes if node.type == "OUTPUT_FILE"]

        for node in nodes:
            node_path, node_filename = os.path.split(node.base_path)
            node.name = node_filename.rstrip("_")

        return {"FINISHED"}


class FULCRUM_OT_prepare_for_render(bpy.types.Operator):
    bl_idname = "fulcrum.prepare_for_render"
    bl_label = "Prep for Render..."
    bl_description = "Absolute paths, Compositing nodes ON, Sequencer OFF, Use border OFF, File format .PNG"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        render_settings = bpy.context.scene.render
        render_settings.use_compositing = True
        render_settings.use_sequencer = False
        render_settings.use_border = False
        render_settings.image_settings.file_format = "PNG"
        # render_settings.use_single_layer = False
        # bpy.context.scene.cycles.use_animated_seed = True  # XXX
        bpy.ops.file.make_paths_absolute()

        # TODO purge ?
        # TODO check compositor output nodes for the same layers?

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="Settings", align=True)
        col.prop(context.scene.render, "film_transparent")
        col.prop(context.scene.cycles, "use_animated_seed")
        col.prop(context.scene.render, "use_persistent_data")
        col.prop(context.scene.render, "use_single_layer")

        col = layout.column(heading="View Layers", align=True)
        layers = context.scene.view_layers
        for layer in layers:
            col.prop(layer, "use", text=f"{layer.name}")

        res_mult = context.scene.render.resolution_percentage / 100
        res_x = int(context.scene.render.resolution_x * res_mult)
        res_y = int(context.scene.render.resolution_y * res_mult)
        split = layout.split(factor=0.4)
        col_01 = split.column(align=True)
        col_02 = split.column(align=True)
        col_01.alignment = "RIGHT"
        col_01.label(text="Final Resolution")
        col_02.label(text=f"{res_x} x {res_y} px")


class FULCRUM_OT_view_layers_to_muted_nodes(bpy.types.Operator):
    bl_idname = "fulcrum.view_layers_to_muted_nodes"
    bl_label = "View Layers to Muted Nodes"
    bl_description = "If File Output nodes are named correctly, this will mute any output nodes whose corresponding View Layer isn't used for rendering"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        node_tree = context.scene.node_tree

        if not node_tree:
            return {"FINISHED"}
        view_layers = context.scene.view_layers
        view_layer_names = [layer.name for layer in view_layers]

        output_nodes = [node for node in node_tree.nodes if node.type == "OUTPUT_FILE"]
        for node in output_nodes:
            if node.name in view_layer_names:
                node.mute = not view_layers.get(node.name).use

        # TODO: backtrack and find render layers?

        return {"FINISHED"}


class FULCRUM_OT_remove_unused_output_sockets(bpy.types.Operator):
    bl_idname = "fulcrum.remove_unused_output_sockets"
    bl_label = "Remove Unused Outputs"
    bl_description = "Remove unused sockets of selected File Output nodes (or all if none are selected)"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not context.scene.node_tree:
            return {"FINISHED"}

        nodes = context.selected_nodes or context.scene.node_tree.nodes
        nodes = [node for node in nodes if node.type == "OUTPUT_FILE"]

        for node in nodes:
            for input in node.inputs:
                if not input.links:
                    node.inputs.remove(input)

        return {"FINISHED"}


class FULCRUM_OT_copy_passes(bpy.types.Operator):
    bl_idname = "fulcrum.copy_passes"
    bl_label = "Copy Passes"
    bl_description = "Copy passes from active view layer to all view layers in this scene"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return len(context.scene.view_layers) > 1

    def execute(self, context):
        view_layer_active = context.view_layer
        other_view_layers = [l for l in context.scene.view_layers if l != view_layer_active]

        layer_attr_names = [
            "pass_alpha_threshold",
            "pass_cryptomatte_depth",
        ]

        layer_attr_names_cycles = [
            "denoising_store_passes",
            "denoising_pass_follow_reflections",
            "denoising_pass_use_albedo_roughness_weighting",
            "pass_debug_sample_count",
            "pass_render_time",
        ]

        for layer in other_view_layers:
            for attr in dir(layer):
                if attr.startswith("use_pass") or attr in layer_attr_names:
                    setattr(layer, attr, getattr(view_layer_active, attr))
            for attr in dir(layer.cycles):
                if attr.startswith("use_pass") or attr in layer_attr_names_cycles:
                    setattr(layer.cycles, attr, getattr(view_layer_active.cycles, attr))

        return {"FINISHED"}


class FULCRUM_OT_render_markers(bpy.types.Operator):
    bl_idname = "fulcrum.render_markers"
    bl_label = "Render Markers"
    bl_description = "Same as manually rendering marker frames in this scene"

    def execute(self, context):
        scene = context.scene
        frame_orig = scene.frame_current

        markers = scene.timeline_markers
        markers_sorted = sorted(markers, key=lambda x: x.frame)
        for marker in markers_sorted:
            scene.frame_current = marker.frame
            bpy.ops.render.render()

        scene.frame_current = frame_orig

        return {"FINISHED"}

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def draw(self, context):
        layout = self.layout
        layout.label(text="Only compositor outputs will be saved.", icon="STATUS_INFO")
        layout.label(text="Did you forget to toggle console?", icon="STATUS_INFO")


registry = [
    FULCRUM_OT_anim_time_limit,
    FULCRUM_OT_render_to_new_slot,
    FULCRUM_OT_set_render_passes,
    FULCRUM_OT_set_output_directory,
    FULCRUM_OT_compositor_increment_version,
    FULCRUM_OT_compositor_output_path_to_node_name,
    FULCRUM_OT_prepare_for_render,
    FULCRUM_OT_view_layers_to_muted_nodes,
    FULCRUM_OT_remove_unused_output_sockets,
    FULCRUM_OT_copy_passes,
    FULCRUM_OT_render_markers,
]
