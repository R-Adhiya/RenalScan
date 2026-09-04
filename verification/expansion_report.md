# Dataset Expansion Verification Report

**Generated:** 2026-09-02 20:13:07

================================================================================

## 1. Executive Summary

**Total Images in Merged Dataset:** 3305
**Duplicates Removed:** 2202

**Status:** ✓ Dataset expansion completed successfully


## 2. Download Results

**Source Dataset:** N/A
**Downloaded Images:** 0
**Download Status:** Skipped


## 3. Class Validation

**Compatible:** ✓ Yes
**Current Classes:** Kidney Stone
**Source Classes:** Stone
**Remapping Required:** Yes

**Message:** Classes are compatible but different ('Stone' -> 'Kidney Stone'). Remapping recommended.

**Class Mapping:**
  - Source class 0 → Target class 0


## 4. Format Validation

**Target Format:** JPG
**Target Resolution:** (512, 512)

**Format Consistency:** 4640/4640 images match target
**Resolution Consistency:** 0/4640 images match target

**Format Distribution:**

| Category | Count | Percentage |
|----------|-------|------------|
| JPG | 4,640 | 100.0% |
**Resolution Distribution:**

| Category | Count | Percentage |
|----------|-------|------------|
| 640x640 | 3,340 | 72.0% |
| 391x320 | 1,300 | 28.0% |
| **Total** | **4,640** | **100.0%** |
**Preprocessing Recommendations:**
- ⚠ Resolution Mismatch: 4640/4640 images (100.0%) are not 512x512
-   → Found resolutions: 391x320, 640x640
-   → Resize all images to 512x512
-   → Recommended tool: PIL/Pillow Image.resize() with LANCZOS resampling
-   → Note: Ensure bounding box coordinates are adjusted after resizing



## 5. Quality Check

**Sampled Images:** 20
**Visualization Directory:** verification\quality_samples

**Sample Visualizations:**

Found 25 quality check samples:

1. [annotated_1-3-46-670589-33-1-63706641772764805000001-5029730734513337703_png_jpg.rf.b417161d433405de346ee9933d0383eb.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63706641772764805000001-5029730734513337703_png_jpg.rf.b417161d433405de346ee9933d0383eb.jpg)
2. [annotated_1-3-46-670589-33-1-63708731690501427000001-5196467758041326827_png_jpg.rf.51beb26562d6fe6e10fe2097212db3e4.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63708731690501427000001-5196467758041326827_png_jpg.rf.51beb26562d6fe6e10fe2097212db3e4.jpg)
3. [annotated_1-3-46-670589-33-1-63709084528426342100001-5346911111081937098_png_jpg.rf.4d828a838b1449e43f259d3896d7629b.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63709084528426342100001-5346911111081937098_png_jpg.rf.4d828a838b1449e43f259d3896d7629b.jpg)
4. [annotated_1-3-46-670589-33-1-63711136318693213600001-4987801166806938557_png_jpg.rf.3b74f6e4bd0a356e11eb2a9f606a63db.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63711136318693213600001-4987801166806938557_png_jpg.rf.3b74f6e4bd0a356e11eb2a9f606a63db.jpg)
5. [annotated_1-3-46-670589-33-1-63712447732709729500001-5332677781930674817_png_jpg.rf.0d7b6741fa751ed1dee75d65b5ff8920.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63712447732709729500001-5332677781930674817_png_jpg.rf.0d7b6741fa751ed1dee75d65b5ff8920.jpg)
6. [annotated_1-3-46-670589-33-1-63712871326759742200001-4997279614880263429_png_jpg.rf.e1c74c458b24f299f1b2d3895b1709f1.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63712871326759742200001-4997279614880263429_png_jpg.rf.e1c74c458b24f299f1b2d3895b1709f1.jpg)
7. [annotated_1-3-46-670589-33-1-63714071926693893500001-5065273098250219072_png_jpg.rf.d859cf4f36579ff6c7301244a72733be.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63714071926693893500001-5065273098250219072_png_jpg.rf.d859cf4f36579ff6c7301244a72733be.jpg)
8. [annotated_1-3-46-670589-33-1-63714762778448524900001-5096671957963205419_png_jpg.rf.f75d6a8bee122ee5dac1f4d41730039a.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63714762778448524900001-5096671957963205419_png_jpg.rf.f75d6a8bee122ee5dac1f4d41730039a.jpg)
9. [annotated_1-3-46-670589-33-1-63714778964147526500001-5659149365717113924_png_jpg.rf.70372d7f77053d8511358a8fdab92d99.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63714778964147526500001-5659149365717113924_png_jpg.rf.70372d7f77053d8511358a8fdab92d99.jpg)
10. [annotated_1-3-46-670589-33-1-63715478193448360500001-5010227791196116152_png_jpg.rf.43d8b0af2ae344929eeb0a4dcea2cecd.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63715478193448360500001-5010227791196116152_png_jpg.rf.43d8b0af2ae344929eeb0a4dcea2cecd.jpg)
11. [annotated_1-3-46-670589-33-1-63716060912854083200001-5244862981767021826_png_jpg.rf.0843c033ae01d22dbe0509342665d151.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63716060912854083200001-5244862981767021826_png_jpg.rf.0843c033ae01d22dbe0509342665d151.jpg)
12. [annotated_1-3-46-670589-33-1-63716409318753002000001-4712773722353272969_png_jpg.rf.c175d5e6193033f40d281afe180a178d.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63716409318753002000001-4712773722353272969_png_jpg.rf.c175d5e6193033f40d281afe180a178d.jpg)
13. [annotated_1-3-46-670589-33-1-63716496539674327900001-5382266281094660619_png_jpg.rf.5199f9992b4223b04df65e91aa7b497b.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63716496539674327900001-5382266281094660619_png_jpg.rf.5199f9992b4223b04df65e91aa7b497b.jpg)
14. [annotated_1-3-46-670589-33-1-63717275390993953400001-4711978371398588691_png_jpg.rf.9ccb31aee234cbefa8fcbc8eecfd8534.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63717275390993953400001-4711978371398588691_png_jpg.rf.9ccb31aee234cbefa8fcbc8eecfd8534.jpg)
15. [annotated_1-3-46-670589-33-1-63717277650355181500001-5538083783713267945_png_jpg.rf.ec3a5823c4e9601d514136bf8c722b63.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63717277650355181500001-5538083783713267945_png_jpg.rf.ec3a5823c4e9601d514136bf8c722b63.jpg)
16. [annotated_1-3-46-670589-33-1-63717795134857973100001-4961218282382428870_png_jpg.rf.e763b367f238cb696fc9a158117506e5.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63717795134857973100001-4961218282382428870_png_jpg.rf.e763b367f238cb696fc9a158117506e5.jpg)
17. [annotated_1-3-46-670589-33-1-63720209448120532100001-5039251107728897035_png_jpg.rf.354bfc6a939a0a62b93d3658b14eed70.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63720209448120532100001-5039251107728897035_png_jpg.rf.354bfc6a939a0a62b93d3658b14eed70.jpg)
18. [annotated_1-3-46-670589-33-1-63733253865035755300001-4735710385933343151_png_jpg.rf.ceb12b75e1e09de1afb55542de3d81ff.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63733253865035755300001-4735710385933343151_png_jpg.rf.ceb12b75e1e09de1afb55542de3d81ff.jpg)
19. [annotated_1-3-46-670589-33-1-63735336130240422700001-5434640726191670437_png_jpg.rf.d4067727d904bbf25f0a3128187836f4.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63735336130240422700001-5434640726191670437_png_jpg.rf.d4067727d904bbf25f0a3128187836f4.jpg)
20. [annotated_1-3-46-670589-33-1-63735844363634848800001-4800417648369869341_png_jpg.rf.c386fb666ed449d8793366c09a5b34c9.jpg](verification\quality_samples\annotated_1-3-46-670589-33-1-63735844363634848800001-4800417648369869341_png_jpg.rf.c386fb666ed449d8793366c09a5b34c9.jpg)

*... and 5 more samples*
**Summary:** Generated 20 quality visualizations


## 6. Duplicate Detection

**Perceptual Hash Duplicates:** 2202
**Filename Duplicates:** 0

**Duplicate Pairs (sample):**

1. Hamming Distance: 0
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700749865510700001-5062181202000819812_png_jpg.rf.269520bcaab75e008e00f57f3fa98851.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\train\images\1-3-46-670589-33-1-63700700749865510700001-5062181202000819812_png_jpg.rf.385dabe9dda8e205a1a8b902cfbea25d.jpg`

2. Hamming Distance: 0
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700749865510700001-5062181202000819812_png_jpg.rf.74493ef7bdab6de49e88f708a5745000.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\test\images\1-3-46-670589-33-1-63700700749865510700001-5062181202000819812_png_jpg.rf.b7e68e927bbb5933d0ce03cc9a2093ae.jpg`

3. Hamming Distance: 5
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700749865510700001-5062181202000819812_png_jpg.rf.74493ef7bdab6de49e88f708a5745000.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\test\images\1-3-46-670589-33-1-63716412431764056000001-5528951312801001919_png_jpg.rf.1bf0a69fda90a6d5c2a5fb7afe4a737a.jpg`

4. Hamming Distance: 1
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700750059521800001-5070347181582747136_png_jpg.rf.1caafe96658dc8bfb7dfe174ef751da3.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\train\images\1-3-46-670589-33-1-63700700750188529100001-5659992199131706929_png_jpg.rf.2a0847cbff1a0b6ffa4e480431b3a671.jpg`

5. Hamming Distance: 0
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700750059521800001-5070347181582747136_png_jpg.rf.1caafe96658dc8bfb7dfe174ef751da3.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\valid\images\1-3-46-670589-33-1-63700700750059521800001-5070347181582747136_png_jpg.rf.2f596daf4e8d75a6fa8d20b23f30bc4d.jpg`

6. Hamming Distance: 0
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700750059521800001-5070347181582747136_png_jpg.rf.b97e32ed8347d9de676a821b992e9e50.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\train\images\1-3-46-670589-33-1-63700700750059521800001-5070347181582747136_png_jpg.rf.99fce505d6782e10f498a23d07d65e38.jpg`

7. Hamming Distance: 1
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700750188529100001-5659992199131706929_png_jpg.rf.20fb68d8630e3526b4e7e5c8198277cc.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\train\images\1-3-46-670589-33-1-63700700750188529100001-5659992199131706929_png_jpg.rf.2a0847cbff1a0b6ffa4e480431b3a671.jpg`

8. Hamming Distance: 2
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700750188529100001-5659992199131706929_png_jpg.rf.20fb68d8630e3526b4e7e5c8198277cc.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\valid\images\1-3-46-670589-33-1-63700700750059521800001-5070347181582747136_png_jpg.rf.2f596daf4e8d75a6fa8d20b23f30bc4d.jpg`

9. Hamming Distance: 0
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700700750188529100001-5659992199131706929_png_jpg.rf.32f57db5f742576e560a82af2a4666e7.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\train\images\1-3-46-670589-33-1-63700700750188529100001-5659992199131706929_png_jpg.rf.29b750b553e5fa3c9e08d0ffe250afd8.jpg`

10. Hamming Distance: 0
   - Dataset 1: `data\train\images\1-3-46-670589-33-1-63700780314615924400001-4656503585389726474_png_jpg.rf.bb783428cbaeb76974585af0199b3c8b.jpg`
   - Dataset 2: `roboflow_dataset_preprocessed\test\images\1-3-46-670589-33-1-63700780314615924400001-4656503585389726474_png_jpg.rf.10d7f3ba01222a69f3e98e9070f4bcfb.jpg`

*... and 2192 more duplicate pairs*

**Recommendations:**
- Found 2202 perceptual duplicates. Consider removing images from dataset 2 to avoid redundancy.



## 7. Merge Results

**Output Directory:** data_merged

**Split Statistics:**

| Split | Count | Percentage |
|-------|-------|------------|
| Train | 2,313 | 70.0% |
| Valid | 495 | 15.0% |
| Test | 497 | 15.0% |
| **Total** | **3,305** | **100.0%** |
**Source Distribution:**

| Category | Count | Percentage |
|----------|-------|------------|
| roboflow | 2,005 | 60.7% |
| current | 1,300 | 39.3% |
| **Total** | **3,305** | **100.0%** |


## 8. Recommendations

- ⚠ **Format Inconsistency:** Preprocessing recommended - see format validation section
- ✓ **Duplicates Removed:** 2202 duplicates identified and excluded from merge
- ✓ **Quality Check:** Review 20 sample visualizations in quality check section
- ✓ **Dataset Ready:** Merged dataset created successfully and ready for model training


## 9. Next Steps

### Model Retraining

The dataset expansion is complete. To retrain your YOLOv8 model:

1. **Review Quality Samples:** Manually inspect the quality check visualizations to ensure annotation quality
2. **Update Configuration:** Ensure your training script points to the new merged dataset location
3. **Backup Current Model:** Save your current model weights before retraining
4. **Train Model:** Run training with the expanded dataset
5. **Evaluate Performance:** Compare validation metrics with your previous model
6. **Test on Hold-out Set:** Validate the new model on the test split

**Training Command Example:**
```bash
yolo detect train \
  data=data_merged/data.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=512 \
  batch=16
```

**Note:** Model retraining is NOT executed automatically. Please review this report and manually initiate training when ready.

