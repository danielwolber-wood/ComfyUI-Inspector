from .display_node import SimpleDisplayNode

NODE_CLASS_MAPPINGS = {
    "SimpleDisplayNode": SimpleDisplayNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SimpleDisplayNode": "Universal Inspector (Debug)"
}

WEB_DIRECTORY = "./js"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]