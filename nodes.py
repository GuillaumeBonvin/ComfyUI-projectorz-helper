from .image_methods import ImageChecker, ImageType

class ImageCheckTypeNode:
    """
    Node to check image types (SolidColor, Mask, DepthMap, NormalMap, Color).
    Distinguishes between different image types based on pixel values.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {"image": ("IMAGE", {}), },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("type",)
    FUNCTION = "check_type"
    CATEGORY = "ProjectorzHelp"

    def check_type(self, image):
        return (ImageChecker.check_type(image).value,)


NODE_CLASS_MAPPINGS = {
    "ImageTypeCheck": ImageCheckTypeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageTypeCheck": "Image Type Check",
}