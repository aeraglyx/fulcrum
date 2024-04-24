import math

import bpy
import mathutils


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
    bl_label = "Auto Track Weight"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if hasattr(context, "edit_movieclip"):
            if hasattr(context.edit_movieclip, "tracking"):
                return True
        return False
        # context.edit_movieclip.tracking.reconstruction.is_valid
        # TODO

    error_threshold: bpy.props.FloatProperty(
        name="Target Error",
        description="Decrease track weight exponentially with increasing average error. This specifies what error has 0.5 weight. Lower values yield smaller error but rely on fewer tracks",
        min=0.0,
        default=2.0,
        soft_max=10.0,
    )
    smooth: bpy.props.IntProperty(
        name="Smoothing",
        description="Number of frames to fade in/out track weights to reduce discontinuities",
        min=1,
        default=6,
        soft_max=100,
    )
    prioritize_center: bpy.props.FloatProperty(
        name="Prioritize Center",
        description="Gaussian function. 1.0 means 0.5 at horizontal edge",
        min=0.0,
        default=0.5,
        soft_max=10.0,
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

            weight_base = 0.0
            avg_error = track.average_error
            if not math.isnan(avg_error):
                weight_base = track.weight_stab  # context this frame or sample at time
                mult_error = math.pow(2.0, -avg_error / self.error_threshold)
                weight_base = mult_error * mult_error
            weight_base = 0.1 + 0.9 * weight_base

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
                        # TODO fade bad tracks longer?
                    # marker.is_keyed

                    aspect = scene.render.resolution_y / scene.render.resolution_x
                    x = 2.0 * (marker.co.x - 0.5)
                    y = 2.0 * (marker.co.y - 0.5) * aspect
                    r = math.sqrt(x**2.0 + y**2.0)

                    mult_center = math.pow(
                        2.0, -math.pow(self.prioritize_center * r, 2.0)
                    )
                    weight *= mult_center
                else:
                    weight = 0.0
                    # TODO if not needed, don't write keyframe

                fcurve.keyframe_points.insert(frame, weight, options={"FAST"})

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "error_threshold")
        col.prop(self, "smooth")
        col.prop(self, "prioritize_center")


class FULCRUM_OT_rolling_shutter(bpy.types.Operator):
    bl_idname = "fulcrum.rolling_shutter"
    bl_label = "(Rolling Shutter)"
    bl_description = ""
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return True

    scan_time: bpy.props.FloatProperty(
        name="Scan Time",
        description="1.0 means the scanning takes the whole frame",
        subtype="FACTOR",
        min=0.0,
        default=0.25,
        max=1.0,
    )

    def execute(self, context):
        def cubic(x, a, b, c, d):
            # https://danceswithcode.net/engineeringnotes/interpolation/interpolation.html
            a3 = 0.5 * (-a + 3 * b - 3 * c + d)
            a2 = 0.5 * (2 * a - 5 * b + 4 * c - d)
            a1 = 0.5 * (-a + c)
            y = a3 * x**3 + a2 * x**2 + a1 * x + b
            return y

        scene = context.scene
        clip = bpy.context.edit_movieclip
        tracks = clip.tracking.tracks
        # frames = range(scene.frame_start, scene.frame_end + 1)

        # for frame in frames:
        for track in tracks:
            markers = track.markers
            new_name = "_" + track.name
            tracks.new(name=new_name, frame=frame)
            # TODO check if markers are ordered by frame or creation
            # frames = [marker.frame for marker in markers]
            for i, marker in enumerate(markers):
                offset = (marker.co.x - 0.5) * self.scan_time
                marker_last = markers[i - 1]
                marker_next = markers[i + 1]
                markers.insert_frame(marker.frame, (x_new, y_new))
                pass
            for frame in frames:
                marker = markers.find_frame(frame)
                # TODO check if nearby frames exist
                if offset < 0:
                    a = markers.find_frame(frame - 2).co
                    b = markers.find_frame(frame - 1).co
                    c = marker.co
                    d = markers.find_frame(frame + 1).co
                    t = 1 + offset  # + because it's negative
                else:
                    a = markers.find_frame(frame - 1).co
                    b = marker.co
                    c = markers.find_frame(frame + 1).co
                    d = markers.find_frame(frame + 2).co
                    t = offset
                x_new = cubic(t, a.x, b.x, c.x, d.x)
                y_new = cubic(t, a.y, b.y, c.y, d.y)

                marker.co = mathutils.Vector((x_new, y_new))

        return {"FINISHED"}

    def draw(self, context):
        layout = self.layout

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(align=True)
        col.prop(self, "scan_time")
