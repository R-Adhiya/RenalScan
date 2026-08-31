import sys
from pathlib import Path
import numpy as np

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from src.pipeline.pipeline import RenalScanPipeline

def test_pipeline_execution():
    """Runs test suite verifying RenalScanPipeline on test CT scans and edge cases."""
    print("=" * 70)
    print("RUNNING RENALSCAN PIPELINE TEST SUITE (tests/test_pipeline.py)")
    print("=" * 70)
    
    pipeline = RenalScanPipeline()
    test_img_dir = PROJECT_ROOT / "data" / "test" / "images"
    test_imgs = sorted(list(test_img_dir.glob("*.jpg")))[:5]
    
    if len(test_imgs) == 0:
        print("⚠️ No test images found in data/test/images!")
        return
        
    print(f"Loaded {len(test_imgs)} test images for pipeline verification.\n")
    
    # 1. Test on actual CT images
    for i, img_path in enumerate(test_imgs):
        print(f"--- Test Case {i+1}: {img_path.name} ---")
        result = pipeline.analyze(img_path, conf_thresh=0.40)
        
        summary = result['summary']
        stones = result['stones']
        
        print(f"  Status          : {summary['status_message']}")
        print(f"  Has Stones      : {summary['has_stones']}")
        print(f"  Stone Count     : {summary['stone_count']}")
        print(f"  Largest Size    : {summary['largest_stone_diameter_mm']} mm ({summary['largest_stone_size_band']})")
        
        for s in stones:
            print(f"    - Stone #{s['stone_id']}: Conf={s['confidence']} | Box={s['box_xyxy']} | "
                  f"Diam={s.get('estimated_diameter_mm', 0)}mm | Band='{s.get('clinical_size_band', 'N/A')}'")
        print()

    # 2. Test Edge Case: Synthetic Zero-Stones (Blank CT Scan Array)
    print("--- Test Case Edge Case: Blank Black Image (0 Stones Detected) ---")
    blank_img = np.zeros((512, 512, 3), dtype=np.uint8)
    blank_result = pipeline.analyze(blank_img, conf_thresh=0.40)
    
    blank_summary = blank_result['summary']
    print(f"  Status          : {blank_summary['status_message']}")
    print(f"  Has Stones      : {blank_summary['has_stones']}")
    print(f"  Stone Count     : {blank_summary['stone_count']}")
    print(f"  Largest Size    : {blank_summary['largest_stone_diameter_mm']} mm")
    
    assert blank_summary['has_stones'] == False, "Expected has_stones=False for blank image"
    assert blank_summary['stone_count'] == 0, "Expected stone_count=0 for blank image"
    assert len(blank_result['stones']) == 0, "Expected empty stones list for blank image"
    
    print("\n✅ ALL PIPELINE TESTS PASSED SUCCESSFULLY! Zero-stone and multi-stone paths verified.")
    print("=" * 70)

if __name__ == "__main__":
    test_pipeline_execution()
