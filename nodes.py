from enum import Enum
import torch


class ImageType(Enum):
    """Image type enumeration for consistent checking."""
    solidColor = "SolidColor"
    mask = "Mask"
    depth = "DepthMap"
    normalMap = "NormalMap"
    color = "Color"
    default = "Unknown"


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
        # Determine the number of channels from the last dimension
        channels = image.shape[-1]
        result_enum = ImageType.default

        if channels == 3:
            # Multi-channel Input Logic (RGB)
            # Check for solid color
            r = image[..., 0]
            g = image[..., 1]
            b = image[..., 2]
            if (r == g).all() and (r == b).all():
                result_enum = ImageType.solidColor
            # Check for normal map
            elif (r == b).all() and torch.allclose(r, g + 0.5):
                result_enum = ImageType.normalMap
            # Check for mask (black and white)
            elif torch.all((r == 0) & (g == 0) & (b == 0)) or torch.all((r == 1) & (g == 1) & (b == 1)):
                result_enum = ImageType.mask
            # Check for depth map (levels of grey)
            elif torch.any((r > 0) & (r < 1)) or torch.any((g > 0) & (g < 1)) or torch.any((b > 0) & (b < 1)):
                result_enum = ImageType.depth
            else:
                # Assume standard colored image
                result_enum = ImageType.color

        return (result_enum.value,)


NODE_CLASS_MAPPINGS = {
    "ImageTypeCheck": ImageCheckTypeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageTypeCheck&W": "Image Type Check",
}