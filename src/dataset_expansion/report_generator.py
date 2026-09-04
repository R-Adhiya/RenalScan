"""
Report generation for dataset expansion pipeline.

This module generates comprehensive verification reports including download results,
validation summaries, quality checks, duplicate detection, and merge statistics.
"""

import os
from typing import Dict, Any, List
from datetime import datetime


class ReportGenerator:
    """
    Generates comprehensive verification reports for dataset expansion.
    
    Creates markdown reports with all pipeline stage results including
    executive summary, validation results, quality checks, duplicate detection,
    merge statistics, recommendations, and next steps.
    """
    
    def __init__(self, pipeline_results: Dict[str, Any]):
        """
        Initialize ReportGenerator with pipeline results.
        
        Args:
            pipeline_results: Dictionary containing results from all pipeline stages:
                - download_results: Download statistics and status
                - class_validation: ClassValidator results
                - format_validation: FormatValidator results
                - quality_check: QualityChecker results
                - duplicate_detection: DuplicateDetector results
                - merge_results: DatasetMerger results
        """
        self.pipeline_results = pipeline_results
    
    def generate_report(self, output_path: str = "verification/expansion_report.md") -> None:
        """
        Generate markdown verification report with all pipeline details.
        
        Creates a comprehensive report with 9 sections:
        1. Executive Summary
        2. Download Results
        3. Class Validation
        4. Format Validation
        5. Quality Check
        6. Duplicate Detection
        7. Merge Results
        8. Recommendations
        9. Next Steps
        
        Args:
            output_path: Path where the report should be saved (default: verification/expansion_report.md)
            
        Raises:
            IOError: If report cannot be written to output_path
        """
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Build report sections
        report_lines = []
        
        # Header
        report_lines.append("# Dataset Expansion Verification Report")
        report_lines.append("")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        # 1. Executive Summary
        report_lines.extend(self._generate_executive_summary())
        report_lines.append("")
        
        # 2. Download Results
        report_lines.extend(self._generate_download_section())
        report_lines.append("")
        
        # 3. Class Validation
        report_lines.extend(self._generate_class_validation_section())
        report_lines.append("")
        
        # 4. Format Validation
        report_lines.extend(self._generate_format_validation_section())
        report_lines.append("")
        
        # 5. Quality Check
        report_lines.extend(self._generate_quality_check_section())
        report_lines.append("")
        
        # 6. Duplicate Detection
        report_lines.extend(self._generate_duplicate_detection_section())
        report_lines.append("")
        
        # 7. Merge Results
        report_lines.extend(self._generate_merge_results_section())
        report_lines.append("")
        
        # 8. Recommendations
        report_lines.extend(self._generate_recommendations_section())
        report_lines.append("")
        
        # 9. Next Steps
        report_lines.extend(self._generate_next_steps_section())
        report_lines.append("")
        
        # Write report to file
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report_lines))
            print(f"Verification report generated: {output_path}")
        except Exception as e:
            raise IOError(f"Failed to write report to {output_path}: {e}")
    
    def _generate_executive_summary(self) -> List[str]:
        """Generate executive summary section."""
        lines = []
        lines.append("## 1. Executive Summary")
        lines.append("")
        
        # Extract key statistics
        merge_results = self.pipeline_results.get('merge_results', {})
        splits = merge_results.get('splits', {})
        
        total_images = splits.get('total', 0)
        duplicate_count = self.pipeline_results.get('duplicate_detection', {}).get('total_perceptual_duplicates', 0)
        
        lines.append(f"**Total Images in Merged Dataset:** {total_images}")
        lines.append(f"**Duplicates Removed:** {duplicate_count}")
        lines.append("")
        
        # Overall status
        validation_result = self.pipeline_results.get('class_validation', {})
        is_compatible = validation_result.get('is_compatible', False)
        
        if is_compatible and total_images > 0:
            lines.append("**Status:** ✓ Dataset expansion completed successfully")
        else:
            lines.append("**Status:** ⚠ Issues detected - review recommendations below")
        
        lines.append("")
        
        return lines
    
    def _generate_download_section(self) -> List[str]:
        """Generate download results section."""
        lines = []
        lines.append("## 2. Download Results")
        lines.append("")
        
        download_results = self.pipeline_results.get('download_results', {})
        
        if download_results:
            lines.append(f"**Source Dataset:** {download_results.get('source_url', 'N/A')}")
            lines.append(f"**Downloaded Images:** {download_results.get('total_images', 0)}")
            lines.append(f"**Download Status:** {download_results.get('status', 'N/A')}")
            
            if 'message' in download_results:
                lines.append(f"**Message:** {download_results['message']}")
        else:
            lines.append("*No download information available*")
        
        lines.append("")
        
        return lines
    
    def _generate_class_validation_section(self) -> List[str]:
        """Generate class validation section."""
        lines = []
        lines.append("## 3. Class Validation")
        lines.append("")
        
        validation = self.pipeline_results.get('class_validation', {})
        
        if validation:
            lines.append(f"**Compatible:** {'✓ Yes' if validation.get('is_compatible') else '✗ No'}")
            lines.append(f"**Current Classes:** {', '.join(validation.get('current_classes', []))}")
            lines.append(f"**Source Classes:** {', '.join(validation.get('source_classes', []))}")
            lines.append(f"**Remapping Required:** {'Yes' if validation.get('needs_remapping') else 'No'}")
            lines.append("")
            lines.append(f"**Message:** {validation.get('message', 'N/A')}")
            
            if validation.get('mapping'):
                lines.append("")
                lines.append("**Class Mapping:**")
                for src_id, tgt_id in validation['mapping'].items():
                    lines.append(f"  - Source class {src_id} → Target class {tgt_id}")
        else:
            lines.append("*No class validation information available*")
        
        lines.append("")
        
        return lines
    
    def _generate_format_validation_section(self) -> List[str]:
        """Generate format validation section."""
        lines = []
        lines.append("## 4. Format Validation")
        lines.append("")
        
        format_validation = self.pipeline_results.get('format_validation', {})
        
        if format_validation:
            consistency = format_validation.get('consistency_report', {})
            
            lines.append(f"**Target Format:** {consistency.get('target_format', 'JPG')}")
            lines.append(f"**Target Resolution:** {consistency.get('target_resolution', (512, 512))}")
            lines.append("")
            
            total = consistency.get('total_images', 0)
            format_matches = consistency.get('format_matches', 0)
            resolution_matches = consistency.get('resolution_matches', 0)
            
            lines.append(f"**Format Consistency:** {format_matches}/{total} images match target")
            lines.append(f"**Resolution Consistency:** {resolution_matches}/{total} images match target")
            lines.append("")
            
            # Format distribution
            format_report = format_validation.get('format_report', {})
            if format_report.get('format_counts'):
                lines.append("**Format Distribution:**")
                lines.append("")
                lines.append(self.format_class_distribution(format_report['format_counts']))
            
            # Resolution distribution
            resolution_report = format_validation.get('resolution_report', {})
            if resolution_report.get('resolution_counts'):
                lines.append("**Resolution Distribution:**")
                lines.append("")
                res_counts = {f"{w}x{h}": count for (w, h), count in resolution_report['resolution_counts'].items()}
                lines.append(self.format_class_distribution(res_counts))
            
            # Recommendations
            if format_validation.get('recommendations'):
                lines.append("**Preprocessing Recommendations:**")
                for rec in format_validation['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
        else:
            lines.append("*No format validation information available*")
        
        lines.append("")
        
        return lines
    
    def _generate_quality_check_section(self) -> List[str]:
        """Generate quality check section."""
        lines = []
        lines.append("## 5. Quality Check")
        lines.append("")
        
        quality_check = self.pipeline_results.get('quality_check', {})
        
        if quality_check:
            lines.append(f"**Sampled Images:** {quality_check.get('sample_count', 0)}")
            lines.append(f"**Visualization Directory:** {quality_check.get('output_dir', 'N/A')}")
            lines.append("")
            
            if quality_check.get('output_dir'):
                lines.append("**Sample Visualizations:**")
                lines.append("")
                lines.append(self.include_quality_samples(quality_check['output_dir']))
            
            if quality_check.get('summary'):
                lines.append(f"**Summary:** {quality_check['summary']}")
        else:
            lines.append("*No quality check information available*")
        
        lines.append("")
        
        return lines
    
    def _generate_duplicate_detection_section(self) -> List[str]:
        """Generate duplicate detection section."""
        lines = []
        lines.append("## 6. Duplicate Detection")
        lines.append("")
        
        dup_detection = self.pipeline_results.get('duplicate_detection', {})
        
        if dup_detection:
            perceptual_dups = dup_detection.get('total_perceptual_duplicates', 0)
            filename_dups = dup_detection.get('total_filename_duplicates', 0)
            
            lines.append(f"**Perceptual Hash Duplicates:** {perceptual_dups}")
            lines.append(f"**Filename Duplicates:** {filename_dups}")
            lines.append("")
            
            # Show sample duplicate pairs (limit to first 10)
            if perceptual_dups > 0:
                pairs = dup_detection.get('perceptual_duplicate_pairs', [])
                lines.append("**Duplicate Pairs (sample):**")
                lines.append("")
                for i, pair in enumerate(pairs[:10]):
                    lines.append(f"{i+1}. Hamming Distance: {pair.get('hamming_distance', 'N/A')}")
                    lines.append(f"   - Dataset 1: `{pair.get('dataset1_image', 'N/A')}`")
                    lines.append(f"   - Dataset 2: `{pair.get('dataset2_image', 'N/A')}`")
                    lines.append("")
                
                if len(pairs) > 10:
                    lines.append(f"*... and {len(pairs) - 10} more duplicate pairs*")
                    lines.append("")
            
            # Recommendations
            if dup_detection.get('recommendations'):
                lines.append("**Recommendations:**")
                for rec in dup_detection['recommendations']:
                    lines.append(f"- {rec}")
                lines.append("")
        else:
            lines.append("*No duplicate detection information available*")
        
        lines.append("")
        
        return lines
    
    def _generate_merge_results_section(self) -> List[str]:
        """Generate merge results section."""
        lines = []
        lines.append("## 7. Merge Results")
        lines.append("")
        
        merge_results = self.pipeline_results.get('merge_results', {})
        
        if merge_results:
            output_dir = merge_results.get('output_dir', 'N/A')
            lines.append(f"**Output Directory:** {output_dir}")
            lines.append("")
            
            # Split statistics
            splits = merge_results.get('splits', {})
            if splits:
                lines.append("**Split Statistics:**")
                lines.append("")
                lines.append(self.format_statistics_table(splits))
            
            # Source distribution
            source_dist = merge_results.get('source_distribution', {})
            if source_dist:
                lines.append("**Source Distribution:**")
                lines.append("")
                lines.append(self.format_class_distribution(source_dist))
        else:
            lines.append("*No merge results information available*")
        
        lines.append("")
        
        return lines
    
    def _generate_recommendations_section(self) -> List[str]:
        """Generate recommendations section."""
        lines = []
        lines.append("## 8. Recommendations")
        lines.append("")
        
        recommendations = []
        
        # Check class validation
        validation = self.pipeline_results.get('class_validation', {})
        if not validation.get('is_compatible'):
            recommendations.append("⚠ **Class Incompatibility:** Review class validation section and resolve class definition issues")
        
        # Check format validation
        format_validation = self.pipeline_results.get('format_validation', {})
        consistency = format_validation.get('consistency_report', {})
        if consistency.get('format_mismatches', 0) > 0 or consistency.get('resolution_mismatches', 0) > 0:
            recommendations.append("⚠ **Format Inconsistency:** Preprocessing recommended - see format validation section")
        
        # Check duplicates
        dup_detection = self.pipeline_results.get('duplicate_detection', {})
        if dup_detection.get('total_perceptual_duplicates', 0) > 0:
            recommendations.append(f"✓ **Duplicates Removed:** {dup_detection['total_perceptual_duplicates']} duplicates identified and excluded from merge")
        
        # Check quality
        quality_check = self.pipeline_results.get('quality_check', {})
        if quality_check.get('sample_count', 0) > 0:
            recommendations.append(f"✓ **Quality Check:** Review {quality_check['sample_count']} sample visualizations in quality check section")
        
        # Overall recommendation
        merge_results = self.pipeline_results.get('merge_results', {})
        if merge_results.get('splits', {}).get('total', 0) > 0:
            recommendations.append("✓ **Dataset Ready:** Merged dataset created successfully and ready for model training")
        
        if recommendations:
            for rec in recommendations:
                lines.append(f"- {rec}")
        else:
            lines.append("*No specific recommendations*")
        
        lines.append("")
        
        return lines
    
    def _generate_next_steps_section(self) -> List[str]:
        """Generate next steps section."""
        lines = []
        lines.append("## 9. Next Steps")
        lines.append("")
        
        lines.append("### Model Retraining")
        lines.append("")
        lines.append("The dataset expansion is complete. To retrain your YOLOv8 model:")
        lines.append("")
        lines.append("1. **Review Quality Samples:** Manually inspect the quality check visualizations to ensure annotation quality")
        lines.append("2. **Update Configuration:** Ensure your training script points to the new merged dataset location")
        lines.append("3. **Backup Current Model:** Save your current model weights before retraining")
        lines.append("4. **Train Model:** Run training with the expanded dataset")
        lines.append("5. **Evaluate Performance:** Compare validation metrics with your previous model")
        lines.append("6. **Test on Hold-out Set:** Validate the new model on the test split")
        lines.append("")
        
        merge_results = self.pipeline_results.get('merge_results', {})
        if merge_results.get('output_dir'):
            lines.append("**Training Command Example:**")
            lines.append("```bash")
            lines.append("yolo detect train \\")
            lines.append(f"  data={merge_results['output_dir']}/data.yaml \\")
            lines.append("  model=yolov8n.pt \\")
            lines.append("  epochs=100 \\")
            lines.append("  imgsz=512 \\")
            lines.append("  batch=16")
            lines.append("```")
            lines.append("")
        
        lines.append("**Note:** Model retraining is NOT executed automatically. Please review this report and manually initiate training when ready.")
        lines.append("")
        
        return lines
    
    def format_statistics_table(self, stats: Dict[str, int]) -> str:
        """
        Format split statistics as markdown table.
        
        Args:
            stats: Dictionary with split names as keys and counts as values
                   e.g., {'train': 3500, 'valid': 750, 'test': 750, 'total': 5000}
        
        Returns:
            Formatted markdown table string
        """
        lines = []
        
        # Table header
        lines.append("| Split | Count | Percentage |")
        lines.append("|-------|-------|------------|")
        
        # Calculate total if not provided
        total = stats.get('total', sum(v for k, v in stats.items() if k != 'total'))
        
        # Add rows for each split (exclude total from rows, add at end)
        for split in ['train', 'valid', 'test']:
            if split in stats:
                count = stats[split]
                percentage = (count / total * 100) if total > 0 else 0
                lines.append(f"| {split.capitalize()} | {count:,} | {percentage:.1f}% |")
        
        # Add total row
        lines.append(f"| **Total** | **{total:,}** | **100.0%** |")
        
        return '\n'.join(lines)
    
    def format_class_distribution(self, distribution: Dict[str, int]) -> str:
        """
        Format class distribution statistics as markdown table.
        
        Args:
            distribution: Dictionary with class names/categories as keys and counts as values
                         e.g., {'Kidney Stone': 5000} or {'current': 1300, 'roboflow': 3700}
        
        Returns:
            Formatted markdown table string
        """
        lines = []
        
        if not distribution:
            return "*No distribution data available*"
        
        # Calculate total
        total = sum(distribution.values())
        
        # Table header
        lines.append("| Category | Count | Percentage |")
        lines.append("|----------|-------|------------|")
        
        # Add rows sorted by count (descending)
        sorted_items = sorted(distribution.items(), key=lambda x: x[1], reverse=True)
        for category, count in sorted_items:
            percentage = (count / total * 100) if total > 0 else 0
            lines.append(f"| {category} | {count:,} | {percentage:.1f}% |")
        
        # Add total row if more than one category
        if len(distribution) > 1:
            lines.append(f"| **Total** | **{total:,}** | **100.0%** |")
        
        return '\n'.join(lines)
    
    def include_quality_samples(self, sample_dir: str) -> str:
        """
        Include links to quality check visualization images.
        
        Scans the sample directory for visualization images and generates
        markdown image links for inclusion in the report.
        
        Args:
            sample_dir: Directory containing quality check sample visualizations
        
        Returns:
            Markdown formatted string with image links
        """
        lines = []
        
        if not os.path.exists(sample_dir):
            return f"*Sample directory not found: {sample_dir}*"
        
        # Find all image files in sample directory
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        image_files = []
        
        try:
            for filename in sorted(os.listdir(sample_dir)):
                if any(filename.lower().endswith(ext) for ext in image_extensions):
                    image_files.append(filename)
        except Exception as e:
            return f"*Error reading sample directory: {e}*"
        
        if not image_files:
            return f"*No sample images found in {sample_dir}*"
        
        lines.append(f"Found {len(image_files)} quality check samples:")
        lines.append("")
        
        # Add markdown links for each sample (limit to first 20)
        for i, filename in enumerate(image_files[:20]):
            image_path = os.path.join(sample_dir, filename)
            lines.append(f"{i+1}. [{filename}]({image_path})")
        
        if len(image_files) > 20:
            lines.append("")
            lines.append(f"*... and {len(image_files) - 20} more samples*")
        
        return '\n'.join(lines)
