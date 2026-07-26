import bpy
from datetime import datetime


def is_valid_timestamp(timestamp: str):
    try:
        datetime.fromisoformat(timestamp)
        return True
    except ValueError:
        return False


class FULCRUM_OT_node_timestamp(bpy.types.Operator):

    bl_idname = "fulcrum.node_timestamp"
    bl_label = "Timestamp Group"
    bl_description = "Append timestamp to the end of node group's description"

    # FIXME: doesn't work in compositor?
    @classmethod
    def poll(cls, context):
        if hasattr(context, "active_node"):
            node = context.active_node
            if node:
                return hasattr(node, "node_tree")
        return False

    def execute(self, context):
        node = context.active_node

        description = node.node_tree.description
        parts = description.split(" ")
        parts = list(filter(None, parts))

        if parts:
            if is_valid_timestamp(parts[-1]):
                del parts[-1]

        timestamp = datetime.now().isoformat(timespec="seconds")
        parts.append(timestamp)

        description = " ".join(parts)
        node.node_tree.description = description

        return {"FINISHED"}
