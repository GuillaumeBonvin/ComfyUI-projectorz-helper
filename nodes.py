import logging
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
        foundtype, conf = ImageChecker.check_type(image)
        logging.info(f"{foundtype.value} detected with {conf*100:.2f}% confidence.")

        return (foundtype.value,)


class ControlNetModelSelectorNode:
    """
    Node to select the correct ControlNet model based on image type (NormalMap or DepthMap).
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "depth_model": ("CONTROL_NET", {}),
                "normal_model": ("CONTROL_NET", {}),
                "fallback_model": ("CONTROL_NET", {}),
                "image": ("IMAGE", {})
            },
            "optional": {}
        }

    RETURN_TYPES = ("CONTROL_NET",)
    RETURN_NAMES = ("model",)
    FUNCTION = "select_model"
    CATEGORY = "ProjectorzHelp"

    def select_model(self, depth_model, normal_model, fallback_model, image):
        if image is not None:
            img_type = ImageChecker.check_type(image)

            # Check specifically for NormalMap to return the normal model
            if img_type == ImageType.depthMap:
                return (depth_model,)
            if img_type == ImageType.normalMap:
                return (normal_model,)
            else:
                # Default fallback or DepthMap detection, return depth model
                return (fallback_model,)
        else:
            # Fallback behavior if no image provided
            return (fallback_model,)


NODE_CLASS_MAPPINGS = {
    "ImageTypeCheck": ImageCheckTypeNode,
    "ControlNetModelSelector": ControlNetModelSelectorNode,

}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageTypeCheck": "Image Type Check",
    "ControlNetModelSelector": "Control Net Model Selector",
}