import bpy


class fulcrum_props(bpy.types.PropertyGroup):
    dev: bpy.props.BoolProperty(
        name="More Stuff",
        default=False,
    ) # type: ignore
    # restart_needed: bpy.props.BoolProperty(
    #     name="Restart Needed", default=False, options={"SKIP_SAVE"}
    # )

    result: bpy.props.FloatProperty(default=1.0) # type: ignore
    confidence: bpy.props.FloatProperty(default=0.5) # type: ignore
