import math
import os

import bpy
import mathutils


def get_output_node(nodes):
    for node in nodes:
        if (
            node.bl_idname == "ShaderNodeOutputMaterial"
            and node.is_active_output == True
        ):
            return node


class FULCRUM_OT_dof_setup(bpy.types.Operator):
    bl_idname = "fulcrum.dof_setup"
    bl_label = "DOF Setup"
    bl_description = "Add an empty and make it the active camera's Focus Object"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return bool(context.scene.camera)

    # TODO empty scale ?

    def execute(self, context):
        cam_obj = context.scene.camera
        dof = cam_obj.data.dof
        dof.use_dof = True
        focus_obj = dof.focus_object

        if focus_obj and focus_obj.type == "EMPTY":
            empty = focus_obj
        else:
            empty = bpy.data.objects.new(f"{cam_obj.name}_focus", None)
            for col in cam_obj.users_collection:
                col.objects.link(empty)
            dof.focus_object = empty

        empty.location = context.scene.cursor.location

        for obj in bpy.data.objects:
            obj.select_set(state=False)
        empty.select_set(state=True)
        context.view_layer.objects.active = empty

        return {"FINISHED"}


class FULCRUM_OT_isometric_setup(bpy.types.Operator):
    bl_idname = "fulcrum.isometric_setup"
    bl_label = "Isometric Setup"
    bl_description = "Set up an orthographic camera for isometric view"
    bl_options = {"REGISTER", "UNDO"}

    # @classmethod
    # def poll(cls, context):
    # 	return bool(context.scene.camera)

    direction: bpy.props.EnumProperty(
        name="Direction",
        description="From which quadrant should the camera point to center",
        items=[
            ("0", "+X +Y", ""),
            ("1", "-X +Y", ""),
            ("2", "-X -Y", ""),
            ("3", "+X -Y", ""),
        ],
        default="3",
    )
    from_below: bpy.props.BoolProperty(
        name="From Below", description="Camera will be tilted upwards", default=False
    )
    scale: bpy.props.FloatProperty(
        name="Scale",
        description="Orthographic Scale",
        min=0.0,
        default=8.0,
        soft_max=64,
    )
    distance: bpy.props.FloatProperty(
        name="Distance",
        description="How far from the center is the camera",
        soft_min=0.0,
        default=8.0,
        soft_max=64,
    )

    def execute(self, context):
        if context.scene.camera:
            cam_obj = context.scene.camera
        else:
            cam_data = bpy.data.cameras.new(name="camera_isometric")
            cam_obj = bpy.data.objects.new("camera_isometric", cam_data)
            context.scene.collection.objects.link(cam_obj)
            context.scene.camera = cam_obj

        # bpy.ops.view3d.view_camera()
        context.space_data.region_3d.view_perspective = "CAMERA"

        magic_angle = math.atan(math.sqrt(2))

        # euler = mathutils.Euler(mathutils.Vector((magic_angle, 0, - math.tau/8 )))
        # matrix_new = euler.to_matrix().to_4x4()
        # context.scene.camera.matrix_world = matrix_new

        dir_idx = int(self.direction)

        cam_obj.rotation_euler[0] = (
            math.tau / 2 - magic_angle if self.from_below else magic_angle
        )
        cam_obj.rotation_euler[1] = 0.0
        cam_obj.rotation_euler[2] = (2 * dir_idx + 3) * math.tau * 0.125

        if dir_idx == 0:
            y = 1.0
            x = 1.0
        elif dir_idx == 1:
            x = -1.0
            y = 1.0
        elif dir_idx == 2:
            x = -1.0
            y = -1.0
        elif dir_idx == 3:
            x = 1.0
            y = -1.0

        z = -1.0 if self.from_below else 1.0

        dist = self.distance
        cam_obj.location = dist * mathutils.Vector((x, y, z))

        cam_obj.data.type = "ORTHO"
        cam_obj.data.ortho_scale = self.scale

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "direction", expand=True)

        layout.prop(self, "from_below")

        col = layout.column(align=True)
        col.prop(self, "scale")
        col.prop(self, "distance")


from bpy_extras.io_utils import ImportHelper


class FULCRUM_OT_projection_setup(bpy.types.Operator, ImportHelper):
    bl_idname = "fulcrum.projection_setup"
    bl_label = "Projection Setup"
    bl_description = "Set up camera projection"
    bl_options = {"REGISTER", "UNDO"}

    # @classmethod
    # def poll(cls, context):
    # 	return bool(context.scene.camera)

    filter_glob: bpy.props.StringProperty(
        default="*.jpg;*.jpeg;*.png;*.tif;*.tiff;*.bmp", options={"HIDDEN"}
    )

    subdivision: bpy.props.IntProperty(
        name="Subdivision",
        description="Number of total subdivisions",
        min=0,
        default=4,
        soft_max=6,
    )
    sharp_or_smooth: bpy.props.FloatProperty(
        name="Sharp / Smooth",
        description="Number of total subdivisions",
        min=0.0,
        default=0.5,
        max=1.0,
        subtype="FACTOR",
    )
    shade_smooth: bpy.props.BoolProperty(
        name="Shade Smooth", description="Turn on shade smoothing", default=True
    )

    def execute(self, context):
        obj = context.object
        cam_obj = context.scene.camera  # TODO selected cam ?

        if self.subdivision:
            smooth_subdiv = round(self.subdivision * self.sharp_or_smooth)
            sharp_subdiv = self.subdivision - smooth_subdiv

            if sharp_subdiv:
                subsurf_modif = obj.modifiers.get(
                    "Subdivision Sharp"
                ) or obj.modifiers.new("Subdivision Sharp", "SUBSURF")
                subsurf_modif.subdivision_type = "SIMPLE"
                subsurf_modif.levels = sharp_subdiv
                subsurf_modif.render_levels = sharp_subdiv

            if smooth_subdiv:
                subsurf_modif = obj.modifiers.get(
                    "Subdivision Smooth"
                ) or obj.modifiers.new("Subdivision Smooth", "SUBSURF")
                subsurf_modif.subdivision_type = "CATMULL_CLARK"
                subsurf_modif.levels = smooth_subdiv
                subsurf_modif.render_levels = smooth_subdiv

        uv_proj_modif = obj.modifiers.get("UVProject") or obj.modifiers.new(
            "UVProject", "UV_PROJECT"
        )
        uv_proj_modif.uv_layer = "UVMap"
        uv_proj_modif.projectors[0].object = cam_obj
        uv_proj_modif.aspect_x = context.scene.render.resolution_x
        uv_proj_modif.aspect_y = context.scene.render.resolution_y

        if self.shade_smooth:
            bpy.ops.object.shade_smooth()
        else:
            bpy.ops.object.shade_flat()

        # ---- IMAGE & MATERIAL ----

        img_filepath = self.filepath
        img = bpy.data.images.load(img_filepath)
        filename = os.path.splitext(bpy.path.basename(img_filepath))[0]

        mat = bpy.data.materials.new(filename)
        mat.use_nodes = True

        nodes = mat.node_tree.nodes
        links = mat.node_tree.links

        obj.data.materials.append(mat)
        obj.active_material_index = len(obj.data.materials) - 1

        nodes.remove(nodes.get("Principled BSDF"))

        coords_node = nodes.new(type="ShaderNodeTexCoord")
        img_node = nodes.new(type="ShaderNodeTexImage")
        output_node = get_output_node(nodes)

        img_node.image = img

        links.new(coords_node.outputs["UV"], img_node.inputs["Vector"])
        links.new(img_node.outputs["Color"], output_node.inputs["Surface"])

        # FIXME redo panel gone when using the import helper

        # TODO UVProject aspect from image resolution
        # TODO align nodes
        # TODO enter edit mode

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "subdivision")
        col.prop(self, "sharp_or_smooth")

        layout.prop(self, "shade_smooth")


def get_cams(context):
    cams = [obj for obj in context.selected_objects if obj.type == "CAMERA"]
    if not cams:
        cams = [context.scene.camera]
    return cams

def get_cam_min_max(cam):
    frame_min = int(cam.name.split("_")[-2])
    frame_max = int(cam.name.split("_")[-1])
    return frame_min, frame_max

class FULCRUM_OT_frame_range_from_cam(bpy.types.Operator):
    bl_idname = "fulcrum.frame_range_from_cam"
    bl_label = "Frame Range from Cameras"
    bl_description = "Set scene frame range from selected cameras or scene camera. Expected format: cam_name_###_###"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        # TODO if camera is parented inside active object ?
        return context.selected_objects or context.scene.camera

    def execute(self, context):
        # TODO scene. frame_preview_start, end + use_preview_range
        def get_cams(context):
            cams = [obj for obj in context.selected_objects if obj.type == "CAMERA"]
            if not cams:
                cams = [context.scene.camera]
            return cams

        def get_cam_min_max(cam):
            frame_min = int(cam.name.split("_")[-2])
            frame_max = int(cam.name.split("_")[-1])
            return frame_min, frame_max

        cams = get_cams(context)

        if len(cams) == 1:
            context.scene.camera = cams[0]

        frame_min = frame_max = None
        for cam in cams:
            try:
                min_cam, max_cam = get_cam_min_max(cam)
            except:
                self.report({"WARNING"}, f"Expected format: cam_name_###_###")
                return {"CANCELLED"}
            if frame_min is None or min_cam < frame_min:
                frame_min = min_cam
            if frame_max is None or max_cam > frame_max:
                frame_max = max_cam

        if frame_max < frame_min:
            # ERROR WARNING ERROR_INVALID_INPUT
            self.report(
                {"WARNING"}, f"Make sure that end_frame isn't lower than start_frame."
            )
            return {"CANCELLED"}

        bpy.context.scene.frame_start = frame_min
        bpy.context.scene.frame_end = frame_max

        frame_orig = bpy.context.scene.frame_current
        # XXX 3 options - keep frame_current / middle of new range / keep but constrained
        # bpy.context.scene.frame_current = int((frame_min + frame_max) / 2)
        new_frame = max(frame_min, min(frame_orig, frame_max))
        bpy.context.scene.frame_current = new_frame

        for area in bpy.context.screen.areas:
            if area.type in ["DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR"]:
                for region in area.regions:
                    if region.type == "WINDOW":
                        override = {"area": area, "region": region}
                        with bpy.context.temp_override(**override):
                            if area.type == "DOPESHEET_EDITOR":
                                bpy.ops.action.view_frame()
                            if area.type == "GRAPH_EDITOR":
                                bpy.ops.graph.view_frame()
                            if area.type == "NLA_EDITOR":
                                bpy.ops.nla.view_frame()

        return {"FINISHED"}


class FULCRUM_OT_markers_to_cameras(bpy.types.Operator):
    bl_idname = "fulcrum.markers_to_cameras"
    bl_label = "Markers to Cameras"
    bl_description = "TODO"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        def get_camera_markers():
            markers = bpy.context.scene.timeline_markers
            camera_markers = []
            for marker in markers:
                if not marker.camera:
                    continue
                if marker.camera.type != "CAMERA":
                    continue
                camera_markers.append(marker)
            return camera_markers

        def frame_to_string(frame):
            return str(frame).zfill(3)

        camera_markers = get_camera_markers()
        frames = [m.frame for m in camera_markers]
        
        for marker in camera_markers:
            camera = marker.camera
            frame_start = marker.frame
            suffix = "_" + frame_to_string(frame_start)

            next_frames = [f for f in frames if f > frame_start]
            if next_frames:
                frame_end = min(next_frames) - 1
            else:
                frame_end = frame_start + 100
            suffix += "_" + frame_to_string(frame_end)
            
            camera.name = camera.name + suffix
        
        # TODO update normal cam names

        return {"FINISHED"}


class FULCRUM_OT_cameras_to_markers(bpy.types.Operator):
    bl_idname = "fulcrum.cameras_to_markers"
    bl_label = "Cameras to Markers"
    bl_description = "Set camera markers from selected cameras or scene camera. Expected format: cam_name_###_###"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):

        def delete_cam_markers(markers, camera):
            markers_to_delete = []
            for marker in markers:
                if marker.camera == cam:
                    markers_to_delete.append(marker)
            
            for marker in markers_to_delete:
                markers.remove(marker)

        markers = context.scene.timeline_markers
        cams = get_cams(context)

        # TODO refactor this shit
        for cam in cams:
            try:
                min_cam, max_cam = get_cam_min_max(cam)
            except:
                self.report({"WARNING"}, f"Expected format: cam_name_###_###")
                return {"CANCELLED"}

            delete_cam_markers(markers, cam)
            
            marker_new = markers.new(cam.name, frame=min_cam)
            marker_new.camera = cam

        return {"FINISHED"}


class FULCRUM_OT_set_resolution(bpy.types.Operator):
    bl_idname = "fulcrum.set_resolution"
    bl_label = "Set Resolution"
    bl_description = "Changes resolution proportionally"
    bl_options = {"REGISTER", "UNDO"}

    width: bpy.props.IntProperty(
        name="Width",
        default=1920,
    )

    def execute(self, context):
        x = context.scene.render.resolution_x
        y = context.scene.render.resolution_y

        context.scene.render.resolution_x = self.width
        context.scene.render.resolution_y = self.width * y / x

        return {"FINISHED"}


class FULCRUM_OT_set_aspect_ratio(bpy.types.Operator):
    bl_idname = "fulcrum.set_aspect_ratio"
    bl_label = "Set Aspect Ratio"
    bl_description = "Sets aspect ratio while keeping Resolution X the same"
    bl_options = {"REGISTER", "UNDO"}

    aspect_ratio: bpy.props.FloatProperty(
        name="Aspect Ratio",
        default=2.0,
    )

    def execute(self, context):
        x = context.scene.render.resolution_x
        y_new = int(x / self.aspect_ratio)
        context.scene.render.resolution_y = y_new

        return {"FINISHED"}


class FULCRUM_OT_passepartout(bpy.types.Operator):
    bl_idname = "fulcrum.passepartout"
    bl_label = "Set Passepartout"
    bl_description = "Sets passepartout opacity"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.scene.camera  # TODO rather if any cams exist?

    alpha: bpy.props.FloatProperty(
        name="Alpha", description="", min=0.0, default=0.8, max=1.0, subtype="FACTOR"
    )

    def execute(self, context):
        cams = [
            cam for cam in bpy.data.objects if cam.type == "CAMERA"
        ]  # and cam.name.startswith("cam_")

        for cam in cams:
            cam.data.passepartout_alpha = self.alpha

        return {"FINISHED"}


class FULCRUM_OT_center_render_region(bpy.types.Operator):
    bl_idname = "fulcrum.center_render_region"
    bl_label = "Center Render Region"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        render = context.scene.render
        x = 0.5 * (render.border_min_x + render.border_max_x) - 0.5
        y = 0.5 * (render.border_min_y + render.border_max_y) - 0.5

        width = 1 / (render.border_max_x - render.border_min_x)
        zoom = 175 * math.log10(width + 0.5)
        context.region.data.view_camera_zoom = zoom

        context.region.data.view_camera_offset[0] = 0.5 * x
        context.region.data.view_camera_offset[1] = 0.5 * y * 16 / 9
        # BUG offset y is bugged in blender, idk

        return {"FINISHED"}


# regions[5].data.view_perspective == 'CAMERA'


class FULCRUM_OT_set_cam_scale(bpy.types.Operator):
    bl_idname = "fulcrum.set_cam_scale"
    bl_label = "Scale Cameras"
    bl_description = "Set visual scale of all cameras"
    bl_options = {"REGISTER", "UNDO"}

    scale: bpy.props.FloatProperty(
        name="Scale",
        description="",
        min=0.0,
        default=0.1,
        soft_max=1.0,
        max=100.0,
        subtype='DISTANCE'
    )

    @classmethod
    def poll(cls, context):
        return bpy.data.cameras

    def execute(self, context):
        for cam in bpy.data.cameras:
            cam.display_size = self.scale

        return {"FINISHED"}
