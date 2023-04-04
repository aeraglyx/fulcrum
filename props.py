import bpy


class fulcrum_props(bpy.types.PropertyGroup):

    dev: bpy.props.BoolProperty(
        name="More Stuff",
        default=False,
    )
    restart_needed: bpy.props.BoolProperty(
        name="Restart Needed", default=False, options={"SKIP_SAVE"}
    )
    use_node_handler: bpy.props.BoolProperty(
        name="Node Visualizer",
        default=False,
    )
    node_vis_type: bpy.props.EnumProperty(
        name="Visualization Type",
        description="...",
        items=[("UNUSED", "Unused", ""), ("LEVELS", "Levels", "")],
        default="UNUSED",
    )

    result: bpy.props.FloatProperty(default=1.0)
    confidence: bpy.props.FloatProperty(default=0.5)
