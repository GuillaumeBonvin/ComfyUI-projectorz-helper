import logging

import torch
from enum import Enum

from .openpose_colors import _VALID_OPEN_POSE_COLORS

class ImageType(Enum):
    """Image type enumeration for consistent checking."""
    solidColor = "SolidColor"
    mask = "Mask"
    depthMap = "DepthMap"
    normalMap = "NormalMap"
    openPose = "OpenPose"
    regularImage = "RegularImage"
    default = "Unknown"


class ImageChecker:

    def is_close_color(c, palette, threshold=40):
        r, g, b = c
        for pr, pg, pb in palette:
            if (r - pr) ** 2 + (g - pg) ** 2 + (b - pb) ** 2 < threshold * threshold:
                return True
        return False

    def extract_unique_colors(image: torch.Tensor, max_pixels: int = 512 * 512, return_pixels: bool = False):
        """
        Extracts the unique colors from an image.
        If the image has more pixels than the given limit, random pixel sampling is done.
        Optionally can return the sampled pixels.
        """
        # --- 1. Ensure channels-last (H, W, C) ---
        if image.ndim == 3 and image.shape[0] in (3, 4):
            image = image.permute(1, 2, 0)  # (H, W, C)
            #logging.warning(f"Warning: Had to permute channels")

        # --- 2. Convert float [0,1] → uint8 [0,255] ---
        if image.dtype in (torch.float32, torch.float64):
            image = (image * 255).clamp(0, 255).to(torch.uint8)

        # --- 3. Drop alpha if present ---
        if image.shape[-1] == 4:
            image = image[:, :, :3]
            #logging.warning(f"Warning: Had to drop alpha channel")

        # --- 4. Flatten to (N, 3) ---
        pixels = image.reshape(-1, 3)
        N = pixels.shape[0]

        # --- 5. Random sampling if too many pixels ---
        if N > max_pixels:
            idx = torch.randperm(N)[:max_pixels]
            pixels = pixels[idx]
            #logging.warning(f"Warning: Had to random sample - too many pixels")


        # --- 6. Pack RGB into a single 32-bit integer ---
        pixels = pixels.to(torch.int32)
        packed = (pixels[:, 0] << 16) | (pixels[:, 1] << 8) | pixels[:, 2]

        # --- 7. Unique packed values (fast) ---
        unique_vals = torch.unique(packed)

        # --- 8. Unpack back to RGB ---
        r = (unique_vals >> 16) & 255
        g = (unique_vals >> 8) & 255
        b = unique_vals & 255

        unique_colors = torch.stack([r, g, b], dim=1)
        rgb_tuples = [tuple(color.tolist()) for color in unique_colors]

        if return_pixels:
            return len(rgb_tuples), rgb_tuples, pixels

        return len(rgb_tuples), rgb_tuples

    @staticmethod
    def check_type(image):
        """
        Determine the image type (SolidColor, Mask, DepthMap, NormalMap, Color)
        based on pixel values. This method is reusable across multiple nodes.
        """

        confidence = 1.0
        num_colors, rgb_tuples, pixels = ImageChecker.extract_unique_colors(image, return_pixels=True)
        #logging.warning(f"IMAGE INFO: unique colors found: {len(rgb_tuples)}")

        # 1. Check for Solid Color (all R, G, B values are equal across the entire image)
        if num_colors == 1:
            return ImageType.solidColor, confidence

        # 2. Check for Mask (Pure Black or Pure White)
        MASK_COLORS = {(0, 0, 0), (255, 255, 255)}
        if num_colors < 3 and all(c in MASK_COLORS for c in rgb_tuples):
            return ImageType.mask, confidence

        # 3. Check for Depth Map / Greyscale
        # Checks whether all pixels individually have the same amount of r, g and b.
        if all(r == g == b for (r, g, b) in rgb_tuples):
            return ImageType.depthMap, confidence

        # 4. Check for Normal Map (Typical blueish/purple tint and unit vector)
        # Calculate the mean RGB value across the entire image spatial dimensions

        # blue dominance
        blue_test_goal = 0.9

        r = pixels[:, 0].float() / 255.0
        g = pixels[:, 1].float() / 255.0
        b = pixels[:, 2].float() / 255.0

        blue_score = (b > 0.5).float().mean()
        blue_ok = blue_score > blue_test_goal
        blue_confidence = min(1.0, max(0.0, (blue_score - blue_test_goal) / (1 - blue_score)))

        # unit vector length
        unit_test_goal = 0.7

        nx = 2 * r - 1
        ny = 2 * g - 1
        nz = 2 * b - 1
        length = torch.sqrt(nx * nx + ny * ny + nz * nz)

        unit_score = ((length > 0.95) & (length < 1.05)).float().mean()
        unit_ok = unit_score > unit_test_goal
        unit_confidence = min(1.0, max(0.0, (unit_score - unit_test_goal) / (1 - unit_score)))

        if blue_ok and unit_ok:
            confidence = (blue_confidence + unit_confidence) / 2
            return ImageType.normalMap, confidence

        # 5. Check for OpenPose / Keypoint Map (Distinct colored joints)
        if 5 <= num_colors:

            # pixels close to black
            near_black = (pixels < 30).all(dim=1)  # True if R,G,B all < 30
            black_ratio = near_black.float().mean().item()
            black_ratio_ok = black_ratio > 0.80

            # pixels close to the openpose palette
            close_matches = sum(
                1 for c in rgb_tuples if ImageChecker.is_close_color(c, _VALID_OPEN_POSE_COLORS)
            )

            match_ratio = close_matches / num_colors
            color_match_ok = match_ratio > 0.5

            #logging.warning(f"open pose color checked with {black_ratio*100:.2f}% black pixels and {match_ratio*100:.2f}% of color match")

            if black_ratio_ok and color_match_ok:
                confidence = (min(black_ratio + 0.1, 1) + match_ratio) / 2
                return ImageType.openPose, confidence

        # 6. Ensure any color in image
        if torch.any((r != g) | (g != b)):
            return ImageType.regularImage, confidence

        return ImageType.default, confidence
