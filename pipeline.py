#!/usr/bin/env python3
"""
Galen Translation Evaluation Pipeline

Complete workflow:
1. Parse input document (Greek + reference translations)
2. Translate Greek text using AI models
3. Evaluate translations against references
4. Generate comprehensive report

Usage:
    python3 pipeline.py input/10_chunks_clean.txt
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from pathlib import Path

# Load environment variables - try multiple locations
try:
    from dotenv import load_dotenv
    env_loaded = False
    
    # Try current directory (galen_eval/.env)
    current_env = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(current_env):
        load_dotenv(current_env)
        print(f"✓ Loaded environment from {current_env}")
        env_loaded = True
    # Try project root (one level up)
    elif os.path.exists(os.path.join(os.path.dirname(__file__), '..', '.env')):
        root_env = os.path.join(os.path.dirname(__file__), '..', '.env')
        load_dotenv(root_env)
        print(f"✓ Loaded environment from {root_env}")
        env_loaded = True
    # Try config/.env
    elif os.path.exists(os.path.join(os.path.dirname(__file__), 'config', '.env')):
        config_env = os.path.join(os.path.dirname(__file__), 'config', '.env')
        load_dotenv(config_env)
        print(f"✓ Loaded environment from {config_env}")
        env_loaded = True
    
    if not env_loaded:
        print("⚠️  No .env file found - API keys must be set in environment")
except ImportError:
    pass

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import InputParser
from translator import Translator
from evaluator import Evaluator
from reporter import Reporter

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Pipeline:
    """Complete translation evaluation pipeline."""
    
    def __init__(
        self,
        models: list = None,
        metrics: list = None,
        use_gpu: bool = False,
        parallel_translation: bool = False
    ):
        """
        Initialize pipeline.
        
        Args:
            models: List of translation models to use
            metrics: List of evaluation metrics to use
            use_gpu: Whether to use GPU for neural metrics
            parallel_translation: Whether to translate with models in parallel
        """
        self.models = models or ['openai', 'claude', 'gemini']
        self.metrics = metrics or ['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet']
        self.use_gpu = use_gpu
        self.parallel_translation = parallel_translation
        
        self.parser = None
        self.translator = None
        self.evaluator = None
        self.reporter = None
    
    def run(self, input_file: str, output_dir: str = None) -> dict:
        """
        Run the complete pipeline.
        
        Args:
            input_file: Path to input file
            output_dir: Output directory (default: output/)
            
        Returns:
            Dictionary with paths to all output files
        """
        if output_dir is None:
            output_dir = 'output'
        
        # Create output directories
        os.makedirs(f"{output_dir}/translations", exist_ok=True)
        os.makedirs(f"{output_dir}/evaluations", exist_ok=True)
        os.makedirs(f"{output_dir}/reports", exist_ok=True)
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = Path(input_file).stem
        
        output_files = {}
        
        print("\n" + "=" * 80)
        print("GALEN TRANSLATION EVALUATION PIPELINE")
        print("=" * 80)
        print(f"\nInput: {input_file}")
        print(f"Models: {', '.join(self.models)}")
        print(f"Metrics: {', '.join(self.metrics)}")
        print(f"GPU: {'Yes' if self.use_gpu else 'No'}")
        print()
        
        # Step 1: Parse input
        print("=" * 80)
        print("STEP 1: PARSING INPUT")
        print("=" * 80)
        print()
        
        self.parser = InputParser()
        parsed_chunks = self.parser.parse_file(input_file)
        
        if not parsed_chunks:
            logger.error("No chunks parsed! Check input file format.")
            return {}
        
        self.parser.print_summary(parsed_chunks)
        
        # Validate
        if not self.parser.validate_parsed_chunks(parsed_chunks):
            logger.error("Validation failed! Check warnings above.")
            return {}
        
        print("✓ Parsing complete\n")
        
        # Step 2: Translate
        print("=" * 80)
        print("STEP 2: TRANSLATING WITH AI MODELS")
        print("=" * 80)
        print()
        
        self.translator = Translator(models=self.models)
        
        chunks_for_translation = [
            {'chunk_id': chunk.chunk_id, 'greek_text': chunk.greek_text}
            for chunk in parsed_chunks
        ]
        
        translations = self.translator.translate_chunks(
            chunks_for_translation,
            parallel=self.parallel_translation
        )
        
        # Save translations
        translations_file = f"{output_dir}/translations/{base_name}_translations_{timestamp}.json"
        self.translator.save_translations(translations, translations_file)
        output_files['translations'] = translations_file
        
        print(f"\n✓ Translation complete")
        print(f"  Output: {translations_file}\n")
        
        # Step 3: Evaluate
        print("=" * 80)
        print("STEP 3: EVALUATING TRANSLATIONS")
        print("=" * 80)
        print()
        
        self.evaluator = Evaluator(metrics=self.metrics, use_gpu=self.use_gpu)
        
        evaluations = self.evaluator.evaluate_all(parsed_chunks, translations)
        
        # Save evaluations
        evaluations_file = f"{output_dir}/evaluations/{base_name}_evaluation_{timestamp}.json"
        evaluation_summary = self.evaluator.save_results(evaluations, evaluations_file)
        output_files['evaluations'] = evaluations_file
        
        print(f"\n✓ Evaluation complete")
        print(f"  Output: {evaluations_file}\n")
        
        # Step 4: Generate report
        print("=" * 80)
        print("STEP 4: GENERATING REPORT")
        print("=" * 80)
        print()
        
        self.reporter = Reporter()
        
        data = {
            'evaluations': evaluation_summary,
            'translations': translations,
            'parsed_chunks': parsed_chunks
        }
        
        # Summary report
        summary_report = self.reporter.generate_summary_report(data)
        summary_file = f"{output_dir}/reports/{base_name}_summary_{timestamp}.txt"
        self.reporter.save_report(summary_report, summary_file)
        output_files['summary'] = summary_file
        
        # Detailed report
        detailed_report = self.reporter.generate_detailed_report(data, max_examples=3)
        detailed_file = f"{output_dir}/reports/{base_name}_detailed_{timestamp}.txt"
        self.reporter.save_report(detailed_report, detailed_file)
        output_files['detailed'] = detailed_file
        
        # CSV export
        csv_file = f"{output_dir}/reports/{base_name}_scores_{timestamp}.csv"
        self.reporter.generate_csv_export(data, csv_file)
        output_files['csv'] = csv_file
        
        print(f"✓ Reports generated")
        print(f"  Summary: {summary_file}")
        print(f"  Detailed: {detailed_file}")
        print(f"  CSV: {csv_file}\n")
        
        # Print summary to console
        print("=" * 80)
        print("FINAL RESULTS")
        print("=" * 80)
        print()
        print(summary_report)
        
        return output_files


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description="Complete translation evaluation pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with all defaults
  python pipeline.py input/10_chunks.txt
  
  # Use only specific models
  python pipeline.py input/10_chunks.txt --models openai claude
  
  # Use only fast metrics (no neural metrics)
  python pipeline.py input/10_chunks.txt --metrics bleu rouge chrf
  
  # Use GPU for faster neural metrics
  python pipeline.py input/10_chunks.txt --gpu
  
  # Parallel translation (faster but more API load)
  python pipeline.py input/10_chunks.txt --parallel
        """
    )
    
    parser.add_argument(
        'input_file',
        help='Input file with Greek text and reference translations'
    )
    
    parser.add_argument(
        '--models',
        nargs='+',
        choices=['openai', 'claude', 'gemini'],
        default=['openai', 'claude', 'gemini'],
        help='Translation models to use (default: all)'
    )
    
    parser.add_argument(
        '--metrics',
        nargs='+',
        choices=['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet', 'bleurt'],
        default=['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet'],
        help='Evaluation metrics to use (default: bleu chrf meteor rouge bertscore comet). Add bleurt on Linux.'
    )
    
    parser.add_argument(
        '--output-dir',
        default='output',
        help='Output directory (default: output/)'
    )
    
    parser.add_argument(
        '--gpu',
        action='store_true',
        help='Use GPU for neural metrics (BERTScore, BLEURT, COMET)'
    )
    
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Translate with models in parallel (faster but more API load)'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check input file exists
    if not os.path.exists(args.input_file):
        logger.error(f"Input file not found: {args.input_file}")
        return 1
    
    # Run pipeline
    pipeline = Pipeline(
        models=args.models,
        metrics=args.metrics,
        use_gpu=args.gpu,
        parallel_translation=args.parallel
    )
    
    try:
        output_files = pipeline.run(args.input_file, args.output_dir)
        
        if output_files:
            print("\n" + "=" * 80)
            print("✅ PIPELINE COMPLETE!")
            print("=" * 80)
            print("\nOutput files:")
            for file_type, file_path in output_files.items():
                print(f"  {file_type:15s} → {file_path}")
            print()
            return 0
        else:
            logger.error("Pipeline failed - check errors above")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Pipeline interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Pipeline failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit(main())
