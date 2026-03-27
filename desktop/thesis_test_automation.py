"""
Thesis Test Automation - Professional Data Extraction & Organization
â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
Runs each alignment technique against the current images, downloads
all PDFs, images, and structured data, organized per-technique.

Output structure (one timestamped run folder per execution):

  thesis/
  â””â”€â”€ run_YYYY-MM-DD_HH-MM-SS/
      â”œâ”€â”€ Master_Index.json
      â”œâ”€â”€ Direct_Pixel/
      â”‚   â”œâ”€â”€ PDFs/
      â”‚   â”‚   â”œâ”€â”€ Full_Report.pdf
      â”‚   â”‚   â”œâ”€â”€ Color_Report.pdf
      â”‚   â”‚   â”œâ”€â”€ Pattern_Report.pdf
      â”‚   â”‚   â””â”€â”€ Settings_Receipt.pdf
      â”‚   â”œâ”€â”€ Images/
      â”‚   â”‚   â”œâ”€â”€ heatmap.png
      â”‚   â”‚   â”œâ”€â”€ spectral.png
      â”‚   â”‚   â””â”€â”€ ...
      â”‚   â””â”€â”€ Data.json
      â”œâ”€â”€ AI_SmartMatch/
      â”‚   â””â”€â”€ ...
      â””â”€â”€ BESTCH/
          â””â”€â”€ ...
"""

import os
import sys
import json
import time
import traceback
import urllib.request
import urllib.error
from datetime import datetime
from io import BytesIO


# â”€â”€ Alignment technique definitions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
TECHNIQUES = [
    {'mode': 'direct',         'folder': 'Direct_Pixel',  'label': 'Direct Pixel'},
    {'mode': 'ai_smart_match', 'folder': 'AI_SmartMatch', 'label': 'AI SmartMatch'},
    {'mode': 'bestch',         'folder': 'BESTCH',        'label': 'BESTCH'},
]


# â”€â”€ Public entry point â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def run_thesis_tests(flask_port, current_settings, current_region_data, ref_file_info, sample_file_info):
    """
    Execute thesis tests: 3 alignment techniques Ã— full analysis pipeline.

    Returns dict with success status, folder path, and per-technique summary.
    """
    try:
        # Resolve project paths (works both frozen EXE and source)
        desktop_dir = os.path.dirname(os.path.abspath(__file__))
        if getattr(sys, 'frozen', False):
            project_dir = sys._MEIPASS
        else:
            project_dir = os.path.dirname(desktop_dir)

        readytotest_dir = os.path.join(project_dir, 'static', 'READYTOTEST')
        thesis_dir      = os.path.join(project_dir, 'thesis')
        os.makedirs(thesis_dir, exist_ok=True)

        # â”€â”€ Resolve image paths â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        ref_path, sample_path, ref_name, sample_name, img_source = \
            _resolve_images(ref_file_info, sample_file_info, readytotest_dir)

        base_url  = f'http://127.0.0.1:{flask_port}'
        run_ts    = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        run_dir   = os.path.join(thesis_dir, f'run_{run_ts}')
        os.makedirs(run_dir, exist_ok=True)

        print(f'[ThesisTest] Run folder: {run_dir}')
        print(f'[ThesisTest] Images: {ref_name} / {sample_name}  ({img_source})')

        tech_results = []

        for i, tech in enumerate(TECHNIQUES):
            print(f'[ThesisTest] â”€â”€ Technique {i+1}/3: {tech["label"]} â”€â”€')
            r = _run_technique(
                tech, base_url, run_dir,
                current_settings, current_region_data,
                ref_path, sample_path, ref_name, sample_name
            )
            tech_results.append(r)

        # â”€â”€ Master index â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
        successful   = sum(1 for r in tech_results if r.get('success'))
        total_pdfs   = sum(r.get('pdfs_saved',   0) for r in tech_results)
        total_images = sum(r.get('images_saved', 0) for r in tech_results)

        master = {
            'run_timestamp' : run_ts,
            'run_folder'    : run_dir,
            'image_source'  : img_source,
            'images_used'   : {'reference': ref_name, 'sample': sample_name},
            'techniques'    : tech_results,
            'summary': {
                'total'        : len(tech_results),
                'successful'   : successful,
                'total_pdfs'   : total_pdfs,
                'total_images' : total_images,
            },
        }
        with open(os.path.join(run_dir, 'Master_Index.json'), 'w', encoding='utf-8') as f:
            json.dump(master, f, indent=2, ensure_ascii=False)

        print(f'[ThesisTest] Done: {successful}/3 succeeded | {total_pdfs} PDFs | {total_images} images')

        return {
            'success'      : True,
            'message'      : f'{successful}/3 techniques completed successfully',
            'thesis_folder': run_dir,
            'total_pdfs'   : total_pdfs,
            'total_images' : total_images,
            'techniques'   : tech_results,
        }

    except Exception as e:
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


# â”€â”€ Image path resolver â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _resolve_images(ref_file_info, sample_file_info, readytotest_dir):
    """Return (ref_path, sample_path, ref_name, sample_name, source_label)."""
    if (ref_file_info and sample_file_info
            and ref_file_info.get('path')
            and os.path.exists(ref_file_info['path'])
            and sample_file_info.get('path')
            and os.path.exists(sample_file_info['path'])):
        return (
            ref_file_info['path'],
            sample_file_info['path'],
            ref_file_info.get('name', 'reference.png'),
            sample_file_info.get('name', 'sample.png'),
            'Workspace Images',
        )

    # Fallback: built-in Ready-to-Test pair 1
    ref = os.path.join(readytotest_dir, '1.png')
    sam = os.path.join(readytotest_dir, '2.png')
    if not os.path.exists(ref) or not os.path.exists(sam):
        raise FileNotFoundError(
            f'Ready-to-Test images not found in: {readytotest_dir}\n'
            'Please load images in the workspace, or ensure the '
            'READYTOTEST folder exists.'
        )
    return ref, sam, '1.png', '2.png', 'Ready-to-Test Pair 1'


# â”€â”€ Per-technique runner â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _run_technique(tech, base_url, run_dir, settings, region_data,
                   ref_path, sample_path, ref_name, sample_name):
    """Run one analysis technique and save all outputs.  Always returns a dict."""
    mode   = tech['mode']
    folder = tech['folder']
    label  = tech['label']

    tech_dir   = os.path.join(run_dir, folder)
    pdfs_dir   = os.path.join(tech_dir, 'PDFs')
    images_dir = os.path.join(tech_dir, 'Images')
    for d in (pdfs_dir, images_dir):
        os.makedirs(d, exist_ok=True)

    t_start = time.time()

    # â”€â”€ 1. Call /api/analyze â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    test_settings = dict(settings)
    test_settings['alignment_mode'] = mode

    try:
        result = _call_analyze(
            base_url, ref_path, sample_path, ref_name, sample_name,
            test_settings, region_data
        )
    except Exception as e:
        traceback.print_exc()
        return {
            'technique': folder, 'mode': mode, 'label': label,
            'success': False, 'error': f'Analysis request failed: {e}',
        }

    if not result.get('success'):
        err = result.get('error', 'Analysis returned success=false')
        print(f'  [FAIL] {label}: {err}')
        return {'technique': folder, 'mode': mode, 'label': label, 'success': False, 'error': err}

    session_id = result.get('session_id', '')
    if not session_id:
        return {
            'technique': folder, 'mode': mode, 'label': label,
            'success': False,
            'error': 'No session_id in response â€” update app.py to include it (already fixed in this build)',
        }

    duration = time.time() - t_start
    print(f'  [OK] Analysis done in {duration:.1f}s  |  decision={result.get("decision")}  |  '
          f'color={result.get("color_score",0):.1f}  pattern={result.get("pattern_score",0):.1f}')

    # â”€â”€ 2. Download PDFs â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    pdf_map = [
        ('Full_Report.pdf',      result.get('pdf_url',           f'/api/download_report/merged/{session_id}')),
        ('Color_Report.pdf',     result.get('color_report_url',  f'/api/download_report/color/{session_id}')),
        ('Pattern_Report.pdf',   result.get('pattern_report_url',f'/api/download_report/pattern/{session_id}')),
        ('Settings_Receipt.pdf', result.get('receipt_url',       f'/api/download_receipt/{session_id}')),
    ]
    pdfs_saved = []
    for pdf_name, pdf_path in pdf_map:
        try:
            data = _fetch(base_url + pdf_path, timeout=120)
            out  = os.path.join(pdfs_dir, pdf_name)
            with open(out, 'wb') as f:
                f.write(data)
            pdfs_saved.append(pdf_name)
            print(f'  [PDF] {pdf_name}  ({len(data)//1024} KB)')
        except Exception as e:
            print(f'  [WARN] PDF failed ({pdf_name}): {e}')

    # â”€â”€ 3. Download visualization images â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    # The response already contains the correct URLs in result['images']
    images_saved = []
    viz = result.get('images') or {}
    for key, img_url in viz.items():
        try:
            data = _fetch(base_url + img_url, timeout=60)
            out  = os.path.join(images_dir, f'{key}.png')
            with open(out, 'wb') as f:
                f.write(data)
            images_saved.append(f'{key}.png')
            print(f'  [IMG] {key}.png  ({len(data)//1024} KB)')
        except Exception as e:
            print(f'  [WARN] Image failed ({key}): {e}')

    # â”€â”€ 4. Save structured Data.json â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    data_json = _build_data_json(
        result, mode, label, duration,
        ref_name, sample_name, pdfs_saved, images_saved
    )
    json_path = os.path.join(tech_dir, 'Data.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data_json, f, indent=2, ensure_ascii=False)
    print(f'  [JSON] Data.json saved')

    print(f'  [{label}] {len(pdfs_saved)} PDFs  |  {len(images_saved)} images')

    return {
        'technique'       : folder,
        'mode'            : mode,
        'label'           : label,
        'success'         : True,
        'pdfs_saved'      : len(pdfs_saved),
        'images_saved'    : len(images_saved),
        'duration_seconds': round(duration, 2),
        'report_id'       : result.get('report_id', ''),
        'decision'        : result.get('decision', ''),
        'color_score'     : result.get('color_score', 0),
        'pattern_score'   : result.get('pattern_score', 0),
        'overall_score'   : result.get('overall_score', 0),
    }


# â”€â”€ HTTP helpers â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _call_analyze(base_url, ref_path, sample_path, ref_name, sample_name,
                  settings, region_data):
    """POST multipart/form-data to /api/analyze and return parsed JSON dict."""
    boundary = b'SpectraMatchThesisBoundary7a2f9c'
    body     = BytesIO()

    def _add_file(field, filename, data, ctype=b'image/png'):
        body.write(b'--' + boundary + b'\r\n')
        body.write(
            b'Content-Disposition: form-data; name="' +
            field.encode() + b'"; filename="' + filename.encode() + b'"\r\n'
        )
        body.write(b'Content-Type: ' + ctype + b'\r\n\r\n')
        body.write(data)
        body.write(b'\r\n')

    def _add_field(field, value):
        body.write(b'--' + boundary + b'\r\n')
        body.write(
            b'Content-Disposition: form-data; name="' + field.encode() + b'"\r\n\r\n'
        )
        body.write(value.encode() if isinstance(value, str) else value)
        body.write(b'\r\n')

    with open(ref_path, 'rb')    as f: _add_file('ref_image',    ref_name,    f.read())
    with open(sample_path, 'rb') as f: _add_file('sample_image', sample_name, f.read())
    _add_field('settings',          json.dumps(settings))
    _add_field('region_data',       json.dumps(region_data))
    _add_field('single_image_mode', 'false')
    body.write(b'--' + boundary + b'--\r\n')

    req = urllib.request.Request(
        f'{base_url}/api/analyze',
        data=body.getvalue(),
        headers={'Content-Type': f'multipart/form-data; boundary={boundary.decode()}'},
    )
    with urllib.request.urlopen(req, timeout=360) as resp:
        raw = resp.read()
    return json.loads(raw.decode('utf-8'))


def _fetch(url, timeout=60):
    """Download a URL and return raw bytes.  Raises on HTTP error."""
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


# â”€â”€ Comprehensive JSON builder â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def _build_data_json(result, mode, label, duration, ref_name, sample_name,
                     pdfs_saved, images_saved):
    """Package the full /api/analyze response into a structured thesis data file."""
    return {
        'metadata': {
            'alignment_mode'   : mode,
            'alignment_label'  : label,
            'report_id'        : result.get('report_id', ''),
            'report_date'      : result.get('report_date', ''),
            'report_time'      : result.get('report_time', ''),
            'operator'         : result.get('operator', ''),
            'duration_seconds' : round(duration, 2),
            'images_used'      : {'reference': ref_name, 'sample': sample_name},
            'pdfs_saved'       : pdfs_saved,
            'images_saved'     : images_saved,
        },
        'scores': {
            'color_score'            : result.get('color_score', 0),
            'pattern_score'          : result.get('pattern_score', 0),
            'overall_score'          : result.get('overall_score', 0),
            'decision'               : result.get('decision', ''),
            'color_status'           : result.get('color_status', ''),
            'pattern_status'         : result.get('pattern_status', ''),
            'color_scoring_method'   : result.get('color_scoring_method', ''),
            'color_method_label'     : result.get('color_method_label', ''),
            'pattern_scoring_method' : result.get('pattern_scoring_method', ''),
            'pattern_method_label'   : result.get('pattern_method_label', ''),
        },
        'color_analysis': {
            'mean_de00'      : result.get('mean_de00', 0),
            'csi_value'      : result.get('csi_value', 0),
            'de_statistics'  : result.get('de_statistics', {}),
            'color_regions'  : result.get('color_regions', []),
            'color_averages' : result.get('color_averages', {}),
            'illuminant_data': result.get('illuminant_data', []),
        },
        'pattern_analysis': {
            'composite_score'   : result.get('pattern_composite', 0),
            'final_status'      : result.get('pattern_final_status', ''),
            'individual_scores' : result.get('pattern_scores', {}),
            'structural_meta'   : result.get('structural_meta', {}),
        },
        'alignment': {
            'mode'   : mode,
            'metrics': result.get('alignment_metrics', {}),
        },
        'recommendations': {
            'color_findings'           : result.get('color_findings', []),
            'color_conclusion'         : result.get('color_conclusion_text', ''),
            'color_conclusion_status'  : result.get('color_conclusion_status', ''),
            'pattern_findings'         : result.get('pattern_findings', []),
            'pattern_conclusion'       : result.get('pattern_conclusion_text', ''),
            'pattern_conclusion_status': result.get('pattern_conclusion_status', ''),
        },
        'report_sizes': {
            'full'   : result.get('report_size', ''),
            'color'  : result.get('color_report_size', ''),
            'pattern': result.get('pattern_report_size', ''),
        },
    }


if __name__ == '__main__':
    print('Thesis test automation module loaded successfully.')
