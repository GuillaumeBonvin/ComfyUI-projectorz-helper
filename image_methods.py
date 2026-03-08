import torch
import logging
from enum import Enum

class ImageType(Enum):
    """Image type enumeration for consistent checking."""
    solidColor = "SolidColor"
    mask = "Mask"
    depthMap = "DepthMap"
    normalMap = "NormalMap"
    regularImage = "RegularImage"
    default = "Unknown"


class ImageChecker:
    @staticmethod
    def check_type(image):
        """
        Determine the image type (SolidColor, Mask, DepthMap, NormalMap, Color)
        based on pixel values. This method is reusable across multiple nodes.
        """
        # Determine the number of channels from the last dimension
        channels = image.shape[-1]

        # Check for non-3 channel images first and log warning
        if channels < 3:
            logging.warning(f"Warning: Expected 3-channel input or more, but got {channels} channels")
            return ImageType.default

        # Extract RGB values directly from the image tensor
        r = image[..., 0]
        g = image[..., 1]
        b = image[..., 2]

        logging.info(f"Input image has {channels} channels")

        # 1. Check for Solid Color (all R, G, B values are equal across the entire image)
        if r.unique().numel() == 1 and  g.unique().numel() == 1 and b.unique().numel() == 1:
            return ImageType.solidColor

        # 2. Check for Mask (Pure Black or Pure White)
        # Checks each pixel individually: every pixel must be all-black OR all-white
        if torch.all(((r == 0) & (g == 0) & (b == 0)) | ((r == 1) & (g == 1) & (b == 1))):
            return ImageType.mask

        # 3. Check for Depth Map / Greyscale
        # Checks whether all pixels individually have the same amount of r, g and b.
        # If true, it implies a consistent grayscale value per pixel (potentially depth-like).
        if torch.all((r == g) & (g == b)):
            return ImageType.depthMap

        # 4. Check for Normal Map (Typical blueish/purple tint)
        # Calculate the mean RGB value across the entire image spatial dimensions
        # 1. Blue dominance
        blue_ok = (b > 0.5).float().mean() > 0.7

        # 2. Decode normal
        nx = 2 * r - 1
        ny = 2 * g - 1
        nz = 2 * b - 1
        length = torch.sqrt(nx * nx + ny * ny + nz * nz)

        unit_ok = ((length > 0.85) & (length < 1.15)).float().mean() > 0.8

        if blue_ok and unit_ok:
            return ImageType.normalMap
        else:
            logging.warning(f"Warning: Not a normal map ! blueok: {blue_ok}, unitok: {unit_ok}")

        # 5. Ensure Colored Image (Standard RGB)
        if torch.any((r != g) | (g != b)):
            return ImageType.regularImage

        return ImageType.default
