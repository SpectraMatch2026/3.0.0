# Thesis Test Automation - Complete Structure

## Folder Structure

```
thesis/
├── Direct_Pixel/
│   ├── PDFs/
│   │   ├── SPEC_XXXXXX_Full_Report.pdf
│   │   ├── SPEC_XXXXXX_Color_Report.pdf
│   │   ├── SPEC_XXXXXX_Pattern_Report.pdf
│   │   └── SPEC_XXXXXX_Settings_Receipt.pdf
│   ├── Images/
│   │   ├── delta_e_heatmap.png
│   │   ├── spectral_proxy.png
│   │   ├── rgb_histograms.png
│   │   ├── lab_scatter.png
│   │   ├── lab_bars.png
│   │   ├── ssim_map.png
│   │   ├── gradient_map.png
│   │   ├── phase_map.png
│   │   ├── gradient_boundary.png
│   │   ├── gradient_filled.png
│   │   ├── phase_boundary.png
│   │   ├── phase_filled.png
│   │   ├── multi_method.png
│   │   ├── pure_diff.png
│   │   ├── fourier_fft.png
│   │   └── glcm_heatmap.png
│   ├── JSON/
│   │   └── Direct_Pixel_Complete_Data.json
│   └── Attempts/
│       └── Attempt_01_2026-03-27_18-30-45/
│           └── attempt_metadata.json
│
├── AI_SmartMatch/
│   ├── PDFs/
│   ├── Images/
│   ├── JSON/
│   └── Attempts/
│       └── Attempt_02_2026-03-27_18-30-45/
│
├── BESTCH/
│   ├── PDFs/
│   ├── Images/
│   ├── JSON/
│   └── Attempts/
│       └── Attempt_03_2026-03-27_18-30-45/
│
└── Master_Index_2026-03-27_18-30-45.json
```

## Files Created

### Modified Files:
1. `desktop/app_desktop.py` - API method (lines 102-129)
2. `templates/desktop.html` - Button (lines 199-201)
3. `static/desktop/desktop.js` - Handler (lines 2284-2352)

### Created Files:
1. `desktop/thesis_test_automation.py` - Core automation
2. `THESIS_STRUCTURE.md` - This documentation

## JSON Structure

### Complete_Data.json
```json
{
  "report_id": "SPEC_260327_180458",
  "session_id": "...",
  "alignment_mode": "direct",
  "duration_seconds": 27.83,
  "overall_scores": {
    "color_score": 100.0,
    "pattern_score": 99.5,
    "overall_score": 99.75,
    "decision": "ACCEPT"
  },
  "color_analysis": {
    "delta_e_2000": {"mean": 0, "std": 0, "min": 0, "max": 0},
    "delta_e_76": {...},
    "delta_e_94": {...},
    "csi_score": 0,
    "color_similarity_percentage": 0
  },
  "pattern_analysis": {
    "ssim": {"score": 0, "mean": 0, "std": 0},
    "gradient": {...},
    "phase": {...},
    "structural": {...},
    "glcm_features": {},
    "fft_metrics": {}
  },
  "tables": {
    "rgb_values": {},
    "cmyk_values": {},
    "lab_values": {},
    "xyz_values": {},
    "sampling_points": [],
    "illuminant_analysis": {}
  },
  "statistics": {
    "image_dimensions": {"width": 0, "height": 0},
    "processing_time": 0,
    "alignment_quality": {},
    "region_info": {}
  },
  "settings": {...},
  "region_data": {...}
}
```

### Master_Index.json
```json
{
  "run_timestamp": "2026-03-27_18-30-45",
  "image_source": "Ready-to-Test Pair 1",
  "techniques_processed": [
    {
      "name": "Direct_Pixel",
      "mode": "direct",
      "success": true,
      "pdfs": 4,
      "images": 16,
      "duration": 27.83
    },
    {...},
    {...}
  ],
  "total_pdfs": 12,
  "total_images": 48,
  "total_json": 3,
  "folder_structure": {
    "Direct_Pixel": "thesis/Direct_Pixel/",
    "AI_SmartMatch": "thesis/AI_SmartMatch/",
    "BESTCH": "thesis/BESTCH/"
  }
}
```

## Implementation Rules

### Strict Requirements:
✓ Each technique in separate folder  
✓ PDFs saved with original names  
✓ Images extracted in report order  
✓ ALL tables saved as JSON  
✓ Attempts timestamped  
✓ No mixing of techniques  
✓ No missing data  
✓ No reordering  

### Execution:
1. Click thesis test button
2. 3 analyses run (Direct_Pixel, AI_SmartMatch, BESTCH)
3. Each creates folder structure
4. All 4 PDFs downloaded per technique
5. All 16 images extracted per technique
6. Complete data saved as JSON
7. Attempt metadata recorded
8. Master index created

## Output Summary

**Per Technique:**
- 4 PDFs in PDFs/
- 16 images in Images/
- 1 JSON in JSON/
- 1 attempt folder in Attempts/

**Total:**
- 12 PDFs (4 × 3 techniques)
- 48 images (16 × 3 techniques)
- 3 JSON files (1 per technique)
- 3 attempt folders
- 1 master index

## Usage

Click thesis test button → Wait for completion → Check thesis/ folder

All content organized by technique, ready for thesis writing.
