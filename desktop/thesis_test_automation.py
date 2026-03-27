"""
Thesis Test Automation - Professional PDF Processing & Organization
────────────────────────────────────────────────────────────────────
Extracts ALL content from reports in exact order and organizes by technique.
"""

import os
import sys
import json
import time
import shutil
import urllib.request
import tempfile
from datetime import datetime
from pathlib import Path
from io import BytesIO


def run_thesis_tests(flask_port, current_settings, current_region_data, ref_file_info, sample_file_info):
    """
    Execute thesis tests with strict PDF processing and organization.
    
    Structure:
    thesis/
    ├── Direct_Pixel/
    │   ├── PDFs/
    │   ├── Images/
    │   ├── JSON/
    │   └── Attempts/
    │       └── Attempt_01_2026-03-27_18-30-45/
    ├── AI_SmartMatch/
    │   └── ...
    └── BESTCH/
        └── ...
    """
    try:
        desktop_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(desktop_dir)
        static_dir = os.path.join(project_dir, 'static')
        readytotest_dir = os.path.join(static_dir, 'READYTOTEST')
        
        thesis_dir = os.path.join(project_dir, 'thesis')
        os.makedirs(thesis_dir, exist_ok=True)
        
        # Determine images
        use_fallback = False
        if ref_file_info and sample_file_info and ref_file_info.get('path') and sample_file_info.get('path'):
            ref_image_path = ref_file_info['path']
            sample_image_path = sample_file_info['path']
            ref_image_name = ref_file_info.get('name', 'reference.png')
            sample_image_name = sample_file_info.get('name', 'sample.png')
        else:
            use_fallback = True
            ref_image_path = os.path.join(readytotest_dir, '1.png')
            sample_image_path = os.path.join(readytotest_dir, '2.png')
            ref_image_name = '1.png'
            sample_image_name = '2.png'
            
            if not os.path.exists(ref_image_path) or not os.path.exists(sample_image_path):
                return {'success': False, 'error': 'No images available'}
        
        # Alignment modes
        alignment_modes = [
            {'mode': 'direct', 'folder': 'Direct_Pixel'},
            {'mode': 'ai_smart_match', 'folder': 'AI_SmartMatch'},
            {'mode': 'bestch', 'folder': 'BESTCH'}
        ]
        
        base_url = f'http://127.0.0.1:{flask_port}'
        run_timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        
        results = {
            'success': True,
            'timestamp': run_timestamp,
            'techniques': [],
            'total_pdfs': 0,
            'total_images': 0,
            'total_json': 0
        }
        
        # Process each alignment mode
        for idx, alignment in enumerate(alignment_modes):
            mode = alignment['mode']
            folder_name = alignment['folder']
            attempt_num = str(idx + 1).zfill(2)
            
            print(f"Processing technique {idx + 1}/3: {folder_name}")
            
            # Create technique folder structure
            technique_dir = os.path.join(thesis_dir, folder_name)
            pdfs_dir = os.path.join(technique_dir, 'PDFs')
            images_dir = os.path.join(technique_dir, 'Images')
            json_dir = os.path.join(technique_dir, 'JSON')
            attempts_dir = os.path.join(technique_dir, 'Attempts')
            
            for d in [pdfs_dir, images_dir, json_dir, attempts_dir]:
                os.makedirs(d, exist_ok=True)
            
            # Create attempt folder
            attempt_folder = f'Attempt_{attempt_num}_{run_timestamp}'
            attempt_dir = os.path.join(attempts_dir, attempt_folder)
            os.makedirs(attempt_dir, exist_ok=True)
            
            # Run analysis
            test_settings = current_settings.copy()
            test_settings['alignment_mode'] = mode
            
            test_start = time.time()
            
            # Prepare multipart request
            boundary = '----WebKitFormBoundary' + ''.join([str(i % 10) for i in range(16)])
            body = BytesIO()
            
            with open(ref_image_path, 'rb') as f:
                ref_data = f.read()
            body.write(f'--{boundary}\r\n'.encode())
            body.write(f'Content-Disposition: form-data; name="ref_image"; filename="{ref_image_name}"\r\n'.encode())
            body.write(b'Content-Type: image/png\r\n\r\n')
            body.write(ref_data)
            body.write(b'\r\n')
            
            with open(sample_image_path, 'rb') as f:
                sample_data = f.read()
            body.write(f'--{boundary}\r\n'.encode())
            body.write(f'Content-Disposition: form-data; name="sample_image"; filename="{sample_image_name}"\r\n'.encode())
            body.write(b'Content-Type: image/png\r\n\r\n')
            body.write(sample_data)
            body.write(b'\r\n')
            
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="settings"\r\n\r\n')
            body.write(json.dumps(test_settings).encode())
            body.write(b'\r\n')
            
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="region_data"\r\n\r\n')
            body.write(json.dumps(current_region_data).encode())
            body.write(b'\r\n')
            
            body.write(f'--{boundary}\r\n'.encode())
            body.write(b'Content-Disposition: form-data; name="single_image_mode"\r\n\r\n')
            body.write(b'false\r\n')
            
            body.write(f'--{boundary}--\r\n'.encode())
            
            req = urllib.request.Request(
                f'{base_url}/api/analyze',
                data=body.getvalue(),
                headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
            )
            
            try:
                with urllib.request.urlopen(req, timeout=300) as response:
                    result = json.loads(response.read().decode())
                
                test_end = time.time()
                duration = test_end - test_start
                
                if not result.get('success'):
                    results['techniques'].append({
                        'name': folder_name,
                        'mode': mode,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
                    continue
                
                session_id = result.get('session_id', '')
                report_id = result.get('report_id', '')
                
                # Download ALL 12 PDFs
                pdf_files = [
                    ('full_report', f'{report_id}_Full_Report.pdf'),
                    ('color_report', f'{report_id}_Color_Report.pdf'),
                    ('pattern_report', f'{report_id}_Pattern_Report.pdf'),
                    ('settings_receipt', f'{report_id}_Settings_Receipt.pdf')
                ]
                
                pdfs_saved = []
                for pdf_type, pdf_name in pdf_files:
                    try:
                        pdf_url = f'{base_url}/api/download_report/{pdf_type}/{session_id}'
                        if pdf_type == 'settings_receipt':
                            pdf_url = f'{base_url}/api/download_receipt/{session_id}'
                        
                        pdf_req = urllib.request.Request(pdf_url)
                        with urllib.request.urlopen(pdf_req, timeout=60) as pdf_response:
                            pdf_data = pdf_response.read()
                            
                            pdf_path = os.path.join(pdfs_dir, pdf_name)
                            with open(pdf_path, 'wb') as f:
                                f.write(pdf_data)
                            
                            pdfs_saved.append(pdf_name)
                            results['total_pdfs'] += 1
                    except Exception as e:
                        print(f"PDF download failed: {pdf_name} - {e}")
                
                # Extract ALL images from report in ORDER
                image_names = [
                    'delta_e_heatmap.png',
                    'spectral_proxy.png',
                    'rgb_histograms.png',
                    'lab_scatter.png',
                    'lab_bars.png',
                    'ssim_map.png',
                    'gradient_map.png',
                    'phase_map.png',
                    'gradient_boundary.png',
                    'gradient_filled.png',
                    'phase_boundary.png',
                    'phase_filled.png',
                    'multi_method.png',
                    'pure_diff.png',
                    'fourier_fft.png',
                    'glcm_heatmap.png'
                ]
                
                images_saved = []
                for img_name in image_names:
                    try:
                        img_url = f'{base_url}/api/report_image/{session_id}/{img_name}'
                        img_req = urllib.request.Request(img_url)
                        with urllib.request.urlopen(img_req, timeout=30) as img_response:
                            img_data = img_response.read()
                            
                            img_path = os.path.join(images_dir, img_name)
                            with open(img_path, 'wb') as f:
                                f.write(img_data)
                            
                            images_saved.append(img_name)
                            results['total_images'] += 1
                    except:
                        pass
                
                # Extract ALL tables and data as JSON
                json_data = {
                    'report_id': report_id,
                    'session_id': session_id,
                    'alignment_mode': mode,
                    'duration_seconds': round(duration, 2),
                    'overall_scores': {
                        'color_score': result.get('color_score', 0),
                        'pattern_score': result.get('pattern_score', 0),
                        'overall_score': result.get('overall_score', 0),
                        'decision': result.get('decision', 'UNKNOWN')
                    },
                    'color_analysis': extract_color_data(result),
                    'pattern_analysis': extract_pattern_data(result),
                    'tables': extract_all_tables(result),
                    'statistics': extract_statistics(result),
                    'settings': test_settings,
                    'region_data': current_region_data
                }
                
                json_path = os.path.join(json_dir, f'{folder_name}_Complete_Data.json')
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2, ensure_ascii=False)
                results['total_json'] += 1
                
                # Save attempt metadata
                attempt_data = {
                    'attempt_number': attempt_num,
                    'timestamp': run_timestamp,
                    'technique': folder_name,
                    'alignment_mode': mode,
                    'duration_seconds': round(duration, 2),
                    'pdfs_saved': pdfs_saved,
                    'images_saved': images_saved,
                    'success': True
                }
                
                attempt_json = os.path.join(attempt_dir, 'attempt_metadata.json')
                with open(attempt_json, 'w', encoding='utf-8') as f:
                    json.dump(attempt_data, f, indent=2, ensure_ascii=False)
                
                results['techniques'].append({
                    'name': folder_name,
                    'mode': mode,
                    'success': True,
                    'pdfs': len(pdfs_saved),
                    'images': len(images_saved),
                    'duration': round(duration, 2)
                })
                
                print(f"Completed {folder_name}: {len(pdfs_saved)} PDFs, {len(images_saved)} images")
                
            except Exception as e:
                print(f"Error processing {folder_name}: {e}")
                results['techniques'].append({
                    'name': folder_name,
                    'mode': mode,
                    'success': False,
                    'error': str(e)
                })
        
        # Save master index
        master_index = {
            'run_timestamp': run_timestamp,
            'image_source': 'Ready-to-Test Pair 1' if use_fallback else 'Workspace Images',
            'techniques_processed': results['techniques'],
            'total_pdfs': results['total_pdfs'],
            'total_images': results['total_images'],
            'total_json': results['total_json'],
            'folder_structure': {
                'Direct_Pixel': 'thesis/Direct_Pixel/',
                'AI_SmartMatch': 'thesis/AI_SmartMatch/',
                'BESTCH': 'thesis/BESTCH/'
            }
        }
        
        master_path = os.path.join(thesis_dir, f'Master_Index_{run_timestamp}.json')
        with open(master_path, 'w', encoding='utf-8') as f:
            json.dump(master_index, f, indent=2, ensure_ascii=False)
        
        successful = sum(1 for t in results['techniques'] if t.get('success'))
        
        return {
            'success': True,
            'message': f'{successful}/3 techniques processed successfully',
            'thesis_folder': thesis_dir,
            'master_index': master_path,
            'total_pdfs': results['total_pdfs'],
            'total_images': results['total_images'],
            'total_json': results['total_json'],
            'techniques': results['techniques']
        }
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {'success': False, 'error': str(e)}


def extract_color_data(result):
    """Extract ALL color analysis data"""
    return {
        'delta_e_2000': {
            'mean': result.get('delta_e_2000_mean', 0),
            'std': result.get('delta_e_2000_std', 0),
            'min': result.get('delta_e_2000_min', 0),
            'max': result.get('delta_e_2000_max', 0)
        },
        'delta_e_76': {
            'mean': result.get('delta_e_76_mean', 0),
            'std': result.get('delta_e_76_std', 0),
            'min': result.get('delta_e_76_min', 0),
            'max': result.get('delta_e_76_max', 0)
        },
        'delta_e_94': {
            'mean': result.get('delta_e_94_mean', 0),
            'std': result.get('delta_e_94_std', 0),
            'min': result.get('delta_e_94_min', 0),
            'max': result.get('delta_e_94_max', 0)
        },
        'csi_score': result.get('csi_score', 0),
        'color_similarity_percentage': result.get('color_similarity_percentage', 0)
    }


def extract_pattern_data(result):
    """Extract ALL pattern analysis data"""
    return {
        'ssim': {
            'score': result.get('ssim_score', 0),
            'mean': result.get('ssim_mean', 0),
            'std': result.get('ssim_std', 0)
        },
        'gradient': {
            'score': result.get('gradient_score', 0),
            'similarity': result.get('gradient_similarity', 0)
        },
        'phase': {
            'score': result.get('phase_score', 0),
            'correlation': result.get('phase_correlation', 0)
        },
        'structural': {
            'score': result.get('structural_score', 0),
            'match': result.get('structural_match', 0)
        },
        'glcm_features': result.get('glcm_features', {}),
        'fft_metrics': result.get('fft_metrics', {})
    }


def extract_all_tables(result):
    """Extract ALL tables (RGB, CMYK, LAB, XYZ, etc.)"""
    return {
        'rgb_values': result.get('rgb_values', {}),
        'cmyk_values': result.get('cmyk_values', {}),
        'lab_values': result.get('lab_values', {}),
        'xyz_values': result.get('xyz_values', {}),
        'sampling_points': result.get('sampling_points', []),
        'illuminant_analysis': result.get('illuminant_analysis', {})
    }


def extract_statistics(result):
    """Extract ALL statistical data"""
    return {
        'image_dimensions': {
            'width': result.get('image_width', 0),
            'height': result.get('image_height', 0)
        },
        'processing_time': result.get('processing_time', 0),
        'alignment_quality': result.get('alignment_quality', {}),
        'region_info': result.get('region_info', {})
    }


if __name__ == '__main__':
    print("Thesis test automation module loaded")
