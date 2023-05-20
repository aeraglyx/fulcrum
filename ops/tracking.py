import math

import bpy


class FULCRUM_OT_clip_to_scene_resolution(bpy.types.Operator):
    bl_idname = "fulcrum.clip_to_scene_resolution"
    bl_label = "Clip to Scene Resolution"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        scene = context.scene
        clip = bpy.context.edit_movieclip

        scene.render.resolution_x = clip.size[0]
        scene.render.resolution_y = clip.size[1]

        # TODO pixel aspect ratio

        return {"FINISHED"}


class FULCRUM_OT_auto_marker_weight(bpy.types.Operator):
    bl_idname = "fulcrum.auto_marker_weight"
    bl_label = "(Auto Track Weight)"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True
        # if not context.edit_movieclip:
        #     return False
        # context.edit_movieclip.tracking.reconstruction.is_valid
        # TODO

    error_threshold: bpy.props.FloatProperty(
        name="Half Life",
        description="Track weight decreases exponentially with increasing average error, this specifies what error has 0.5 weight. Lower values should yield smaller error but will rely on fewer tracks",
        min=0.0,
        default=1.0,
        soft_max=10.0,
    )
    smooth: bpy.props.IntProperty(
        name="Smoothing",
        description="Number of frames to fade in/out track weights to reduce jumps",
        min=1,
        default=8,
        soft_max=100,
    )
    prioritize_center: bpy.props.FloatProperty(
        name="Prioritize Center",
        description="Gaussian function. 1.0 means 0.5 at horizontal edge",
        min=0.0,
        default=0.5,
        soft_max=10.0,
    )
    edge_weight: bpy.props.FloatProperty(
        name="Edge Weight",
        description="Uses Safe Areas",
        min=0.0,
        default=0.5,
        max=1.0,
        subtype="FACTOR",
    )
    keyed_mult: bpy.props.FloatProperty(
        name="Keyed Mult",
        description="How strongly are manual keyframes considered",
        min=0.0,
        default=0.5,
        soft_max=1.0,
        subtype="FACTOR",
    )

    def execute(self, context):
        scene = context.scene
        clip = bpy.context.edit_movieclip
        tracks = clip.tracking.tracks
        frames = range(scene.frame_start, scene.frame_end + 1)

        if clip.animation_data is None:
            clip.animation_data_create()
        anim_data = clip.animation_data
        if anim_data.action is None:
            action = bpy.data.actions.new(clip.name + "Action")
            anim_data.action = action

        action = clip.animation_data.action
        fcurves = action.fcurves

        for track in tracks:
            keyframes = []
            for frame in frames:
                if frame == scene.frame_start or frame == scene.frame_end:
                    continue
                markers = track.markers
                marker_before = markers.find_frame(frame - 1)
                marker_after = markers.find_frame(frame + 1)
                # TODO what if there is a lonely frame?
                if bool(marker_before) ^ bool(marker_after):
                    keyframes.append(frame)

            def map_range(x, a, b):
                """Map x from a-b to 0-1."""
                x = (x - a) / (b - a)
                return min(max(x, 0), 1)

            def smoothstep(x):
                """Smooth 0-1 range."""
                x = 3 * x**2 - 2 * x**3
                return x

            weight_base = track.weight_stab  # context this frame or sample at time

            mult_error = math.pow(2.0, -track.average_error / self.error_threshold)
            weight_base *= mult_error

            data_path = track.path_from_id() + ".weight"

            fcurve = fcurves.find(data_path)
            if fcurve:
                fcurves.remove(fcurve)
            fcurve = fcurves.new(data_path)

            for frame in frames:
                weight = weight_base
                marker = markers.find_frame(frame)

                if marker:
                    if keyframes:
                        closest_key_dist = min([abs(key - frame) for key in keyframes])
                        mult_trans = map_range(closest_key_dist, -1, self.smooth - 1)
                        weight *= smoothstep(mult_trans)
                    # mult_manual = marker.is_keyed

                    safe_areas = context.scene.safe_areas
                    # title - closer to center
                    # action - closer to edges
                    aspect = clip.tracking.camera.pixel_aspect
                    # TODO

                    co_to_safe_areas_x = 1 - 2 * abs(marker.co.x - 0.5)
                    co_to_safe_areas_y = 1 - 2 * abs(marker.co.y - 0.5)

                    mult_safe_x = map_range(
                        co_to_safe_areas_x,
                        safe_areas.action.x,
                        safe_areas.title.x,
                    )
                    mult_safe_y = map_range(
                        co_to_safe_areas_y,
                        safe_areas.action.y,
                        safe_areas.title.y,
                    )

                    mult_safe = smoothstep(mult_safe_x * mult_safe_y)
                    weight *= mult_safe
                else:
                    weight = 0.0

                fcurve.keyframe_points.insert(frame, weight, options={"FAST"})

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        # col = layout.column(align=True)
        layout.prop(self, "error_threshold")
        layout.prop(self, "smooth")
