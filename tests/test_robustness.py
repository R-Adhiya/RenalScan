import cv2
import unittest
import numpy as np
from pathlib import Path

from src.pipeline.pipeline import RenalScanPipeline

class TestPipelineRobustness(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pipeline = RenalScanPipeline()

    def test_non_ct_image_handling(self):
        """Test that arbitrary non-CT images (noise, natural photo gradients) do not crash and report 0 stones."""
        # 1. Random noise array
        noise_img = np.random.randint(0, 256, (512, 512, 3), dtype=np.uint8)
        res_noise = self.pipeline.analyze(noise_img)
        self.assertFalse(res_noise["summary"]["has_stones"])
        self.assertEqual(res_noise["summary"]["stone_count"], 0)
        self.assertEqual(len(res_noise["stones"]), 0)
        self.assertIn("No kidney stones detected", res_noise["summary"]["status_message"])

        # 2. Smooth gradient (simulating a non-medical graphic/photo)
        grad = np.tile(np.linspace(0, 255, 512, dtype=np.uint8), (512, 1))
        grad_rgb = cv2.cvtColor(grad, cv2.COLOR_GRAY2RGB)
        res_grad = self.pipeline.analyze(grad_rgb)
        self.assertFalse(res_grad["summary"]["has_stones"])
        self.assertEqual(res_grad["summary"]["stone_count"], 0)

    def test_corrupted_file_handling(self):
        """Test that corrupted, non-image, or truncated files raise clean ValueError without hanging."""
        fake_file = Path("test_fake_corrupted.jpg")
        try:
            fake_file.write_text("THIS IS NOT A VALID JPEG FILE CONTENT")
            with self.assertRaises(ValueError):
                self.pipeline.analyze(fake_file)
        finally:
            if fake_file.exists():
                fake_file.unlink()

    def test_empty_or_invalid_array_handling(self):
        """Test that empty or 0-dimension arrays raise ValueError with informative messaging."""
        with self.assertRaises(ValueError):
            self.pipeline.analyze(np.array([]))

        with self.assertRaises(ValueError):
            self.pipeline.analyze(None)

    def test_rgba_channel_conversion(self):
        """Test that 4-channel RGBA inputs (e.g. PNG screenshots) are automatically converted to 3-channel RGB."""
        rgba = np.zeros((256, 256, 4), dtype=np.uint8)
        rgba[:, :, 3] = 255 # opaque alpha
        res = self.pipeline.analyze(rgba)
        self.assertFalse(res["summary"]["has_stones"])
        self.assertEqual(res["original_image"].shape[2], 3)

    def test_extreme_dimension_resilience(self):
        """Test that extreme small and large dimensions do not break the preprocessing or inference pipeline."""
        # 1. Tiny 1x1 image
        tiny_1 = np.array([[[128, 128, 128]]], dtype=np.uint8)
        res_tiny_1 = self.pipeline.analyze(tiny_1)
        self.assertEqual(res_tiny_1["summary"]["stone_count"], 0)

        # 2. Small 8x8 image
        tiny_8 = np.random.randint(0, 256, (8, 8, 3), dtype=np.uint8)
        res_tiny_8 = self.pipeline.analyze(tiny_8)
        self.assertEqual(res_tiny_8["summary"]["stone_count"], 0)

        # 3. Large 2048x2048 image
        large = np.zeros((2048, 2048, 3), dtype=np.uint8)
        res_large = self.pipeline.analyze(large)
        self.assertEqual(res_large["summary"]["stone_count"], 0)

if __name__ == "__main__":
    unittest.main()
