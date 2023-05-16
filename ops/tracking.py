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
        if not context.edit_movieclip:
            return False
        context.edit_movieclip.tracking.reconstruction.is_valid
        # TODO

    error_threshold: bpy.props.FloatProperty(
        name="Half Life",
        description="Track weight decreases exponentially with increasing average error, this specifies what error has 0.5 weight. Lower values should yield smaller error but will rely on fewer tracks",
        min=0.0,
        default=0.5,
        soft_max=10.0,
    )
    keyed_mult: bpy.props.FloatProperty(
        name="Keyed Mult",
        description="How strongly are manual keyframes considered",
        min=0.0,
        default=0.5,
        soft_max=1.0,
        subtype="FACTOR",
    )
    transitions: bpy.props.IntProperty(
        name="Smoothing",
        description="Fade in/out track weights",
        min=0,
        default=6,
        soft_max=100,
    )

    def execute(self, context):
        clip = bpy.context.edit_movieclip
        tracks = clip.tracking.tracks

        for track in tracks:
            keyframes = []

            for frame in range(frames_total):
                markers = track.markers
                marker_before = markers.find_frame(frame - 1)
                marker_after = markers.find_frame(frame + 1)
                if marker_before ^ marker_after:
                    keyframes.append(frame)

            def map_range(x, transition):
                x = (x + 1) / (transition + 1)
                x = min(x, 1)
                x = 3 * x**2 - 2 * x**3
                return x

            mult_base = track.weight_stab  # context this frame or sample at time
            mult_error = math.pow(2.0, -track.average_error / self.error_threshold)

            for frame in frames:
                marker = markers.find_frame(frame)
                if not marker:
                    weight = 0.0
                closest_key_dist = min([abs(key - frame) for key in keyframes])
                mult_trans = map_range(closest_key_dist, self.transitions)

                # TODO write weight

                track.weight = mult_base * mult_error * mult_trans  # TODO at this frame

        # set weights
        # clip.animation_data.action.fcurves[0].keyframe_points[0].co

        # clip.tracking.tracks[0].markers[100].frame
        # marker.frame
        # marker.co
        # marker.mute
        # marker.is_keyed

        # markers.find_frame(26, exact=False).frame

        return {"FINISHED"}
