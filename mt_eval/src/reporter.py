#!/usr/bin/env python3
"""
Report Generator

Creates clear, human-readable reports from evaluation results.
"""

import json
import logging
from typing import Dict, List
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Reporter:
    """Generate human-readable evaluation reports."""
    
    def __init__(self):
        pass
    
    def load_data(self, evaluation_file: str, translations_file: str = None, 
                  input_file: str = None) -> Dict:
        """Load evaluation results and optional context."""
        with open(evaluation_file, 'r', encoding='utf-8') as f:
            evaluations = json.load(f)
        
        data = {'evaluations': evaluations}
        
        if translations_file:
            with open(translations_file, 'r', encoding='utf-8') as f:
                data['translations'] = json.load(f)
        
        if input_file:
            from parser import InputParser
            parser = InputParser()
            data['parsed_chunks'] = parser.parse_file(input_file)
        
        return data
    
    def generate_summary_report(self, data: Dict) -> str:
        """Generate a concise summary report."""
        evaluations = data['evaluations']
        
        lines = []
        lines.append("=" * 80)
        lines.append("TRANSLATION EVALUATION SUMMARY")
        lines.append("=" * 80)
        lines.append("")
        
        # Overall Rankings
        lines.append("🏆 OVERALL MODEL RANKINGS")
        lines.append("-" * 80)
        rankings = evaluations.get('overall_rankings', [])
        for i, (model, score) in enumerate(rankings, 1):
            medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(i, "  ")
            lines.append(f"{medal} {i}. {model.upper():15s} {score:.4f}")
        lines.append("")
        
        # Per-Metric Best Models
        lines.append("📊 BEST MODEL PER METRIC")
        lines.append("-" * 80)
        by_metric = evaluations.get('by_metric', {})
        for metric, scores in sorted(by_metric.items()):
            if 'best_model' in scores:
                best = scores['best_model']
                lines.append(f"  {metric:15s} → {best['name'].upper():10s} ({best['score']:.4f})")
        lines.append("")
        
        # Detailed Model Scores
        lines.append("📈 DETAILED SCORES BY MODEL")
        lines.append("-" * 80)
        by_model = evaluations.get('by_model', {})
        for model in sorted(by_model.keys()):
            lines.append(f"\n{model.upper()}:")
            metrics = by_model[model]
            for metric, stats in sorted(metrics.items()):
                lines.append(f"  {metric:15s} {stats['mean']:.4f} ± {stats['std']:.4f} "
                           f"(min={stats['min']:.3f}, max={stats['max']:.3f}, n={stats['count']})")
        lines.append("")
        
        # Methodology note
        methodology = evaluations.get('methodology', 'unknown')
        if methodology == 'multi-reference':
            lines.append("📋 METHODOLOGY")
            lines.append("-" * 80)
            lines.append("  Multi-reference evaluation:")
            lines.append("  • BLEU-4, chrF++, METEOR: n-grams matched against ANY reference")
            lines.append("  • ROUGE-L, BERTScore, COMET: MAX across references")
            lines.append("")
        
        # Metadata
        lines.append("ℹ️  EVALUATION INFO")
        lines.append("-" * 80)
        detailed = evaluations.get('detailed_scores', [])
        if detailed:
            chunks = set(d['chunk_id'] for d in detailed)
            models = set(d['model_name'] for d in detailed)
            # Count references from per_reference_scores if available
            sample = detailed[0] if detailed else {}
            per_ref = sample.get('per_reference_scores', {})
            num_refs = len(per_ref) if per_ref else 'N/A'
            lines.append(f"  Chunks evaluated: {len(chunks)}")
            lines.append(f"  Models: {', '.join(sorted(models))}")
            lines.append(f"  Reference translations: {num_refs}")
            lines.append(f"  Total evaluations: {len(detailed)}")
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_detailed_report(self, data: Dict, max_examples: int = 3) -> str:
        """Generate a detailed report with translation examples."""
        evaluations = data['evaluations']
        translations = data.get('translations', {})
        parsed_chunks = data.get('parsed_chunks', [])
        
        lines = []
        lines.append("=" * 80)
        lines.append("DETAILED TRANSLATION EVALUATION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Summary first
        lines.append(self.generate_summary_report(data))
        lines.append("\n")
        
        # Translation Examples
        if translations and parsed_chunks:
            lines.append("=" * 80)
            lines.append("TRANSLATION EXAMPLES")
            lines.append("=" * 80)
            lines.append("")
            
            for i, chunk in enumerate(parsed_chunks[:max_examples], 1):
                chunk_id = chunk.chunk_id
                lines.append(f"\n{'─' * 80}")
                lines.append(f"CHUNK {chunk_id}")
                lines.append(f"{'─' * 80}\n")
                
                # Source Greek
                greek = chunk.greek_text
                if len(greek) > 200:
                    greek = greek[:200] + "..."
                lines.append("📜 GREEK SOURCE:")
                lines.append(f"   {greek}\n")
                
                # Reference translations
                lines.append("📚 REFERENCE TRANSLATIONS:")
                for ref_idx, ref in enumerate(chunk.reference_translations, 1):
                    if len(ref) > 250:
                        ref = ref[:250] + "..."
                    lines.append(f"\n   Reference {ref_idx}:")
                    lines.append(f"   {ref}")
                lines.append("")
                
                # Model translations
                if chunk_id in translations:
                    lines.append("🤖 MODEL TRANSLATIONS:\n")
                    for model, trans_data in translations[chunk_id].items():
                        if isinstance(trans_data, dict):
                            trans = trans_data.get('translation', '')
                            status = trans_data.get('status', 'unknown')
                        else:
                            trans = str(trans_data)
                            status = 'unknown'
                        
                        if len(trans) > 250:
                            trans = trans[:250] + "..."
                        
                        status_emoji = "✓" if status == 'success' else "✗"
                        lines.append(f"   {status_emoji} {model.upper()}:")
                        lines.append(f"   {trans}\n")
                
                # Scores for this chunk
                detailed_scores = evaluations.get('detailed_scores', [])
                chunk_scores = [s for s in detailed_scores if s['chunk_id'] == chunk_id]
                
                if chunk_scores:
                    lines.append("📊 EVALUATION SCORES (multi-reference):\n")
                    
                    for score_data in chunk_scores:
                        model = score_data['model_name']
                        scores = score_data['scores']
                        per_ref = score_data.get('per_reference_scores', {})
                        
                        lines.append(f"   {model.upper()} (combined multi-ref scores):")
                        for metric, score in sorted(scores.items()):
                            lines.append(f"      {metric:15s} {score:.4f}")
                        
                        # Show per-reference breakdown if available
                        if per_ref:
                            lines.append(f"\n   {model.upper()} (per-reference breakdown):")
                            for ref_id, ref_scores in sorted(per_ref.items()):
                                lines.append(f"      {ref_id}:")
                                for metric, score in sorted(ref_scores.items()):
                                    lines.append(f"         {metric:15s} {score:.4f}")
                        lines.append("")
            
            if len(parsed_chunks) > max_examples:
                lines.append(f"\n   ... and {len(parsed_chunks) - max_examples} more chunks\n")
        
        lines.append("=" * 80)
        lines.append("END OF REPORT")
        lines.append("=" * 80)
        
        return "\n".join(lines)
    
    def generate_csv_export(self, data: Dict, output_file: str):
        """Export evaluation scores to CSV for further analysis."""
        import csv
        
        evaluations = data['evaluations']
        detailed_scores = evaluations.get('detailed_scores', [])
        
        if not detailed_scores:
            logger.warning("No detailed scores to export")
            return
        
        # Flatten the data
        rows = []
        for score_data in detailed_scores:
            base_row = {
                'chunk_id': score_data['chunk_id'],
                'model': score_data['model_name'],
                'reference': score_data['reference_id']
            }
            
            # Add all metric scores
            for metric, score in score_data['scores'].items():
                base_row[metric] = score
            
            rows.append(base_row)
        
        # Write CSV
        if rows:
            fieldnames = ['chunk_id', 'model', 'reference'] + \
                        sorted([k for k in rows[0].keys() if k not in ['chunk_id', 'model', 'reference']])
            
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
            
            logger.info(f"CSV export saved to {output_file}")
    
    def save_report(self, report: str, output_file: str):
        """Save report to file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"Report saved to {output_file}")


def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate evaluation reports")
    parser.add_argument('evaluation_file', help='Evaluation results JSON file')
    parser.add_argument('--translations', help='Translations JSON file (optional)')
    parser.add_argument('--input', help='Original input file (optional)')
    parser.add_argument('-o', '--output', help='Output report file')
    parser.add_argument('--csv', help='Export to CSV file')
    parser.add_argument('--detailed', action='store_true', help='Generate detailed report')
    parser.add_argument('--max-examples', type=int, default=3, 
                       help='Max translation examples in detailed report')
    
    args = parser.parse_args()
    
    # Load data
    reporter = Reporter()
    data = reporter.load_data(
        args.evaluation_file,
        translations_file=args.translations,
        input_file=args.input
    )
    
    # Generate report
    if args.detailed and (args.translations or args.input):
        report = reporter.generate_detailed_report(data, max_examples=args.max_examples)
    else:
        report = reporter.generate_summary_report(data)
    
    # Print to stdout
    print(report)
    
    # Save to file if requested
    if args.output:
        reporter.save_report(report, args.output)
    
    # Export CSV if requested
    if args.csv:
        reporter.generate_csv_export(data, args.csv)
    
    return 0


if __name__ == "__main__":
    exit(main())
