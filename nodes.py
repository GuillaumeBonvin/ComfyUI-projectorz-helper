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
    RETURN_NAMES = ("image_type",)
    FUNCTION = "check_type"
    CATEGORY = "ProjectorzHelp"

    def check_type(self, image):
        foundtype, conf = ImageChecker.check_type(image)
        logging.info(f"{foundtype.value} detected with {conf*100:.2f}% confidence.")

        return (foundtype.value,)


class ValidateTypeNode:
    """
    Validates an image type string against a target value using an operator.
    """

    @classmethod
    def INPUT_TYPES(cls):
        options = [item.value for item in ImageType]
        return {
            "required": {
                "image_type": ("STRING", {"multiline": False, "default": ""}),
                "operator": (["is", "is not"], {"default": "is"}),
                "target_type": (options, {"default": options[0] if options else "SolidColor"}),
            }
        }


    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("result",)
    FUNCTION = "validate"
    CATEGORY = "ProjectorzHelp"


    def validate(self, image_type, operator, target_type):
        # Note: 'target_type' might be a string from the combo selection
        # Perform the comparison based on the operator
        if operator == "is":
            result = (image_type == target_type,)
        elif operator == "is not":
            result = (image_type != target_type,)
        else:
            result = (False,)  # Default fallback

        return result

class ControlNetModelSelectorNode:
    """
    Node to select the correct ControlNet model based on image type (NormalMap or DepthMap).
    """

    _NOT_LINKED = "unassigned"
    """
    Allows to differentiate between not yet loaded lazy arguments (None) and 
    actual empty inputs (no node linked)
    """

    def __init__(self):
        self._cached_type = None

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fallback_model": ("CONTROL_NET", {}),
            },
            "optional": {
                "image": ("IMAGE", {}),
                "image_type": ("STRING", {"default": ""}),
                "depth_model": ("CONTROL_NET", {"lazy": True}),
                "normal_model": ("CONTROL_NET", {"lazy": True}),
                "openpose_model": ("CONTROL_NET", {"lazy": True}),
            }
        }

    RETURN_TYPES = ("CONTROL_NET", "STRING")
    RETURN_NAMES = ("model", "image_type")
    FUNCTION = "select_model"
    CATEGORY = "ProjectorzHelp"

    def _get_cached_type_or_evaluate(self, image, image_type):
        """
        Checks if the type is already cached. If so, return it.
        Otherwise, evaluates the given image_type or image using ImageChecker and caches the result.
        Returns None if no valid input is provided or if evaluation fails (cache remains cleared/None).
        """
        if self._cached_type is not None:
            return self._cached_type

        # string detection
        if image_type:
            # If user explicitly passed a type string (e.g. "depthMap"), use it.
            # Validate against allowed types to avoid errors with invalid strings
            if image_type in [v.value for v in ImageType]:
                self._cached_type = image_type
                return  image_type

        # image analysis
        if image is not None:
            try:
                found_type, confidence = ImageChecker.check_type(image)
                type_value = found_type.value
                self._cached_type = type_value
                return type_value
            except Exception:
                return None

        return None

    def check_lazy_status(self, fallback_model, image=None, image_type="",
                          depth_model=_NOT_LINKED,
                          normal_model=_NOT_LINKED,
                          openpose_model=_NOT_LINKED):
        """
        Checks which models actually need loading based on the image type detection result.
        Evaluates and caches the result if not already cached.
        """

        needed_models = []
        detected_type = self._get_cached_type_or_evaluate(image, image_type)

        # Determine which models are actually selected/needed
        if depth_model != self._NOT_LINKED and detected_type == ImageType.depthMap.value:
            needed_models.append("depth_model")
        if normal_model != self._NOT_LINKED and detected_type == ImageType.normalMap.value:
            needed_models.append("normal_model")
        if openpose_model != self._NOT_LINKED and detected_type == ImageType.openPose.value:
            needed_models.append("openpose_model")

        return needed_models

    def select_model(self, fallback_model, image=None, image_type="",
                     depth_model=None,
                     normal_model=None,
                     openpose_model=None):
        """
        Selects the appropriate model for the given image or provided type.
        Evaluates and caches the result if not already cached.
        :return: Tuple containing the selected model and the image type.
        """
        selected_model = fallback_model
        selected_type = self._get_cached_type_or_evaluate(image, image_type)

        # Logic to select model based on the resolved type
        # Map known types to specific models, else fallback
        if depth_model and selected_type == ImageType.depthMap.value:
            selected_model = depth_model
        elif normal_model and selected_type == ImageType.normalMap.value:
            selected_model = normal_model
        elif openpose_model and selected_type == ImageType.openPose.value:
            selected_model = normal_model

        #clear cache for next run
        self._cached_type = None


        if selected_type is None:
            selected_type = ImageType.default.value

        return (selected_model, selected_type)


class SelectMatchingTypeNode:
    """
    Node to select the matching image from multiple inputs based on requested type.
    Similar to ControlNetModelSelectorNode but for image routing.
    """

    @classmethod
    def INPUT_TYPES(cls):
        options = [item.value for item in ImageType]
        return {
            "required": {
                "image1": ("IMAGE", {}),
                "image_type1": ("STRING", {}),
                "image2": ("IMAGE", {}),
                "image_type2": ("STRING", {}),
                "image3": ("IMAGE", {}),
                "image_type3": ("STRING", {}),
                "target_type": (options, {"default": options[0] if options else "SolidColor"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "BOOLEAN", "STRING", )
    RETURN_NAMES = ("selected_image", "any_match", "selected_type")
    FUNCTION = "select_matching"
    CATEGORY = "ProjectorzHelp"

    def select_matching(self, image1, image_type1, image2, image_type2, image3, image_type3, target_type):
        """
        Select the image that matches the target type.

        Args:
            image1, image2, image3: Three input images
            type1, type2, type3: The detected types for each image
            target_type: The type that needs selection (e.g., "depthMap", "normalMap")

        Returns:
            The matching image
        """
        # Priority: check if target matches with provided type info
        if image_type1 and target_type and target_type == image_type1:
            return (image1, True, image_type1, )

        if image_type2 and target_type and target_type == image_type2:
            return (image2, True, image_type2, )

        if image_type3 and target_type and target_type == image_type3:
            return (image3, True, image_type3, )

        return (image1, False, target_type, )

NODE_CLASS_MAPPINGS = {
    "ImageTypeCheck": ImageCheckTypeNode,
    "ValidateTypeNode" : ValidateTypeNode,
    "ControlNetModelSelector": ControlNetModelSelectorNode,
    "SelectMatchingType": SelectMatchingTypeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageTypeCheck": "Image Type Check",
    "ValidateTypeNode": "Validate Type",
    "ControlNetModelSelector": "Control Net Model Selector",
    "SelectMatchingType": "Image Selector",
}