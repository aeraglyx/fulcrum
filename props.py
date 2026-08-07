import bpy


class FulcrumProps(bpy.types.PropertyGroup):
    result: bpy.props.FloatProperty(default=1.0) # type: ignore
    confidence: bpy.props.FloatProperty(default=0.5) # type: ignore


registry = [FulcrumProps]
