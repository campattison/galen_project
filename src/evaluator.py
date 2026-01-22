#!/usr/bin/env python3
"""
Translation Evaluation Module

Evaluates machine translations against reference translations using:
- BLEU-4 - multi-reference (checks n-grams against ANY reference)
- chrF++ - multi-reference (native support, includes word n-grams)
- METEOR - multi-reference (natively supports multiple references)
- ROUGE-L - max across references
- BERTScore - max across references
- COMET (contextualized multilingual evaluation) - max across references
- BLEURT - max across references

Multi-reference methodology:
- Lexical metrics (BLEU, chrF++, METEOR): Pass all references; credit for matching ANY reference
- Neural/semantic metrics (ROUGE, BERTScore, COMET, BLEURT): Compute per-reference, take MAX
"""

import logging
import json
import os
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class EvaluationScore:
    """A single evaluation score."""
    metric_name: str
    score: float
    details: Dict = None
    
    def __post_init__(self):
        if self.details is None:
            self.details = {}


@dataclass
class ChunkEvaluation:
    """Evaluation results for a single chunk (multi-reference)."""
    chunk_id: str
    model_name: str
    scores: List[EvaluationScore]
    per_reference_scores: Dict = field(default_factory=dict)  # Detailed per-ref breakdown
    
    def to_dict(self):
        return {
            'chunk_id': self.chunk_id,
            'model_name': self.model_name,
            'scores': {score.metric_name: score.score for score in self.scores},
            'score_details': {score.metric_name: score.details for score in self.scores if score.details},
            'per_reference_scores': self.per_reference_scores
        }


class Evaluator:
    """Evaluate translations using multiple metrics."""
    
    def __init__(self, metrics: List[str] = None, use_gpu: bool = False):
        """
        Initialize evaluator with specified metrics.
        
        Args:
            metrics: List of metrics to use. Options:
                    ['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet', 'bleurt']
                    If None, uses all available metrics
            use_gpu: Whether to use GPU for neural metrics
        """
        if metrics is None:
            # Note: BLEURT excluded by default due to TensorFlow threading issues on macOS
            # Add 'bleurt' to the list if running on Linux with proper TensorFlow setup
            metrics = ['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet']
        
        self.metrics = metrics
        self.use_gpu = use_gpu
        self.metric_handlers = {}
        self._setup_metrics()
    
    def _setup_metrics(self):
        """Initialize metric libraries."""
        
        # BLEU-4 (using SacreBLEU for reproducibility)
        if 'bleu' in self.metrics:
            try:
                from sacrebleu.metrics import BLEU
                # effective_order=True handles short sentences gracefully
                self.metric_handlers['bleu'] = BLEU(effective_order=True)
                logger.info("✓ BLEU-4 metric available (SacreBLEU)")
            except ImportError:
                logger.warning("SacreBLEU not available for BLEU")
        
        # chrF++ (character + word n-grams)
        if 'chrf' in self.metrics:
            try:
                from sacrebleu.metrics import CHRF
                # word_order=2 enables chrF++ (character n-grams + word bigrams)
                self.metric_handlers['chrf'] = CHRF(word_order=2)
                logger.info("✓ chrF++ metric available")
            except ImportError:
                logger.warning("sacrebleu not available for chrF++")
        
        # METEOR
        if 'meteor' in self.metrics:
            try:
                import nltk
                from nltk.translate.meteor_score import meteor_score
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
                self.metric_handlers['meteor'] = meteor_score
                logger.info("✓ METEOR metric available")
            except ImportError:
                logger.warning("NLTK not available for METEOR")
            except Exception as e:
                logger.warning(f"METEOR initialization failed: {e}")
        
        # ROUGE (ROUGE-L only)
        if 'rouge' in self.metrics:
            try:
                from rouge_score import rouge_scorer
                # Only ROUGE-L as per colleague's recommendation
                self.metric_handlers['rouge'] = rouge_scorer.RougeScorer(
                    ['rougeL'],
                    use_stemmer=True
                )
                logger.info("✓ ROUGE-L metric available")
            except ImportError:
                logger.warning("rouge-score not available")
        
        # BERTScore
        if 'bertscore' in self.metrics:
            try:
                import bert_score
                self.metric_handlers['bertscore'] = bert_score
                logger.info("✓ BERTScore available")
            except ImportError:
                logger.warning("bert-score not available")
        
        # BLEURT (optional - large model)
        if 'bleurt' in self.metrics:
            try:
                from bleurt import score as bleurt_score
                checkpoint = os.getenv('BLEURT_CHECKPOINT', 'bleurt-20')
                self.metric_handlers['bleurt'] = bleurt_score.BleurtScorer(checkpoint)
                logger.info("✓ BLEURT available")
            except ImportError:
                logger.warning("BLEURT not available (pip install bleurt)")
            except Exception as e:
                logger.warning(f"BLEURT initialization failed: {e}")
        
        # COMET (optional - large model)
        if 'comet' in self.metrics:
            try:
                from comet import download_model, load_from_checkpoint
                # Use the default COMET model for translation quality estimation
                model_path = download_model("Unbabel/wmt22-comet-da")
                self.metric_handlers['comet'] = load_from_checkpoint(model_path)
                if self.use_gpu:
                    self.metric_handlers['comet'] = self.metric_handlers['comet'].cuda()
                logger.info("✓ COMET available")
            except ImportError:
                logger.warning("COMET not available (pip install unbabel-comet)")
            except Exception as e:
                logger.warning(f"COMET initialization failed: {e}")
        
        if not self.metric_handlers:
            raise RuntimeError("No evaluation metrics available! Install required packages.")
        
        logger.info(f"Active metrics: {', '.join(self.metric_handlers.keys())}")
    
    def evaluate_bleu(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
        """
        Calculate BLEU-4 with multi-reference support using SacreBLEU.
        
        SacreBLEU provides reproducible BLEU scores with standardized tokenization.
        BLEU natively supports multiple references: n-gram precision is computed
        by checking if each n-gram appears in ANY of the references.
        """
        if 'bleu' not in self.metric_handlers:
            return []
        
        try:
            bleu_scorer = self.metric_handlers['bleu']
            
            # SacreBLEU's sentence_score takes hypothesis and list of references
            result = bleu_scorer.sentence_score(hypothesis, references)
            
            return [EvaluationScore(
                metric_name='BLEU-4',
                score=result.score / 100,  # Normalize to 0-1 scale
                details={
                    'raw_score': result.score,
                    'brevity_penalty': result.bp,
                    'num_references': len(references)
                }
            )]
            
        except Exception as e:
            logger.warning(f"BLEU-4 calculation failed: {e}")
            return []
    
    def evaluate_rouge(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
        """
        Calculate ROUGE-L with multi-reference support.
        
        Computes ROUGE-L against each reference and takes the MAX score.
        """
        if 'rouge' not in self.metric_handlers:
            return []
        
        try:
            scorer = self.metric_handlers['rouge']
            
            # Compute ROUGE-L against each reference, take max
            best_score = None
            best_ref_idx = 0
            
            for ref_idx, reference in enumerate(references):
                rouge_scores = scorer.score(reference, hypothesis)
                score_obj = rouge_scores['rougeL']
                
                if best_score is None or score_obj.fmeasure > best_score['fmeasure']:
                    best_score = {
                        'fmeasure': score_obj.fmeasure,
                        'precision': score_obj.precision,
                        'recall': score_obj.recall
                    }
                    best_ref_idx = ref_idx + 1
            
            return [EvaluationScore(
                metric_name='ROUGE-L',
                score=best_score['fmeasure'],
                details={
                    'precision': best_score['precision'],
                    'recall': best_score['recall'],
                    'best_reference': best_ref_idx,
                    'num_references': len(references),
                    'aggregation': 'max'
                }
            )]
            
        except Exception as e:
            logger.warning(f"ROUGE-L calculation failed: {e}")
            return []
    
    def evaluate_chrf(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
        """
        Calculate chrF++ (character n-gram F-score with word bigrams) with multi-reference support.
        
        chrF++ extends chrF by including word n-grams (bigrams), providing better
        correlation with human judgments. sacrebleu's chrF natively supports multiple references.
        """
        if 'chrf' not in self.metric_handlers:
            return []
        
        try:
            chrf_scorer = self.metric_handlers['chrf']
            # Pass all references - chrF++ natively handles multiple references
            result = chrf_scorer.sentence_score(hypothesis, references)
            
            return [EvaluationScore(
                metric_name='chrF++',
                score=result.score / 100,  # Normalize to 0-1
                details={
                    'raw_score': result.score,
                    'num_references': len(references),
                    'word_order': 2  # chrF++ uses word bigrams
                }
            )]
            
        except Exception as e:
            logger.warning(f"chrF++ calculation failed: {e}")
            return []
    
    def evaluate_meteor(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
        """
        Calculate METEOR score with multi-reference support.
        
        METEOR natively supports multiple references: it computes the score against
        each reference and returns the maximum. It incorporates stemming, synonyms,
        and word order.
        """
        if 'meteor' not in self.metric_handlers:
            return []
        
        try:
            from nltk.tokenize import word_tokenize
            meteor_score_func = self.metric_handlers['meteor']
            
            hyp_tokens = word_tokenize(hypothesis.lower())
            # Tokenize all references - METEOR accepts list of reference token lists
            ref_tokens_list = [word_tokenize(ref.lower()) for ref in references]
            
            # METEOR natively handles multiple references and takes the max
            score = meteor_score_func(ref_tokens_list, hyp_tokens)
            
            return [EvaluationScore(
                metric_name='METEOR',
                score=score,
                details={'num_references': len(references)}
            )]
            
        except Exception as e:
            logger.warning(f"METEOR calculation failed: {e}")
            return []
    
    def evaluate_bertscore(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
        """
        Calculate BERTScore with multi-reference support.
        
        Computes BERTScore against each reference and takes the MAX F1 score.
        """
        if 'bertscore' not in self.metric_handlers:
            return []
        
        try:
            bert_score_module = self.metric_handlers['bertscore']
            
            # Compute against each reference
            best_f1 = -1
            best_result = None
            best_ref_idx = 0
            
            for ref_idx, reference in enumerate(references):
                P, R, F1 = bert_score_module.score(
                    [hypothesis], 
                    [reference], 
                    lang='en',
                    verbose=False,
                    device='cuda' if self.use_gpu else 'cpu'
                )
                
                f1_val = float(F1[0])
                if f1_val > best_f1:
                    best_f1 = f1_val
                    best_result = (float(P[0]), float(R[0]), f1_val)
                    best_ref_idx = ref_idx + 1
            
            return [EvaluationScore(
                metric_name='BERTScore',
                score=best_result[2],
                details={
                    'precision': best_result[0],
                    'recall': best_result[1],
                    'f1': best_result[2],
                    'best_reference': best_ref_idx,
                    'num_references': len(references),
                    'aggregation': 'max'
                }
            )]
            
        except Exception as e:
            logger.warning(f"BERTScore calculation failed: {e}")
            return []
    
    def evaluate_bleurt(self, hypothesis: str, references: List[str]) -> List[EvaluationScore]:
        """
        Calculate BLEURT score with multi-reference support.
        
        Computes BLEURT against each reference and takes the MAX.
        """
        if 'bleurt' not in self.metric_handlers:
            return []
        
        try:
            scorer = self.metric_handlers['bleurt']
            
            # Compute against each reference, take max
            best_score = -float('inf')
            best_ref_idx = 0
            
            for ref_idx, reference in enumerate(references):
                scores = scorer.score(references=[reference], candidates=[hypothesis])
                if scores[0] > best_score:
                    best_score = scores[0]
                    best_ref_idx = ref_idx + 1
            
            return [EvaluationScore(
                metric_name='BLEURT',
                score=float(best_score),
                details={
                    'best_reference': best_ref_idx,
                    'num_references': len(references),
                    'aggregation': 'max'
                }
            )]
            
        except Exception as e:
            logger.warning(f"BLEURT calculation failed: {e}")
            return []
    
    def evaluate_comet(self, hypothesis: str, references: List[str], source: str) -> List[EvaluationScore]:
        """
        Calculate COMET score with multi-reference support (requires source text).
        
        Per Unbabel's recommendation, compute COMET against each reference
        individually and take the MAX score.
        """
        if 'comet' not in self.metric_handlers:
            return []
        
        try:
            model = self.metric_handlers['comet']
            
            # Use simpler prediction without multiprocessing
            import os
            import torch
            os.environ['TOKENIZERS_PARALLELISM'] = 'false'
            
            # Fix for MPS (Mac M1/M2) - requires num_workers > 0 when multiprocessing_context is set
            num_workers = 1 if torch.backends.mps.is_available() else 0
            
            # Compute against each reference, take max
            best_score = -float('inf')
            best_ref_idx = 0
            
            for ref_idx, reference in enumerate(references):
                data = [{
                    'src': source,
                    'mt': hypothesis,
                    'ref': reference
                }]
                
                output = model.predict(
                    data, 
                    batch_size=1, 
                    gpus=(1 if self.use_gpu else 0),
                    num_workers=num_workers,
                    progress_bar=False
                )
                
                score = float(output['scores'][0])
                if score > best_score:
                    best_score = score
                    best_ref_idx = ref_idx + 1
            
            return [EvaluationScore(
                metric_name='COMET',
                score=best_score,
                details={
                    'best_reference': best_ref_idx,
                    'num_references': len(references),
                    'aggregation': 'max'
                }
            )]
            
        except Exception as e:
            logger.warning(f"COMET calculation failed: {e}")
            return []
    
    def evaluate_single(self, hypothesis: str, references: List[str], source: str = None) -> List[EvaluationScore]:
        """
        Evaluate a single hypothesis against multiple references.
        
        Args:
            hypothesis: The translation to evaluate
            references: List of reference translations
            source: Source text (required for COMET)
            
        Returns:
            List of evaluation scores (using proper multi-reference methodology)
        """
        all_scores = []
        
        # Lexical metrics
        all_scores.extend(self.evaluate_bleu(hypothesis, references))
        all_scores.extend(self.evaluate_chrf(hypothesis, references))
        all_scores.extend(self.evaluate_meteor(hypothesis, references))
        all_scores.extend(self.evaluate_rouge(hypothesis, references))
        
        # Neural/semantic metrics
        all_scores.extend(self.evaluate_bertscore(hypothesis, references))
        all_scores.extend(self.evaluate_bleurt(hypothesis, references))
        
        if source:
            all_scores.extend(self.evaluate_comet(hypothesis, references, source))
        
        return all_scores
    
    def evaluate_per_reference(self, hypothesis: str, references: List[str], source: str = None) -> Dict[str, List[EvaluationScore]]:
        """
        Evaluate a hypothesis against each reference individually.
        
        Useful for per-reference analysis to understand which reference
        a translation aligns with more closely.
        
        Args:
            hypothesis: The translation to evaluate
            references: List of reference translations
            source: Source text (required for COMET)
            
        Returns:
            Dict mapping reference_id to list of scores
        """
        per_ref_scores = {}
        
        for ref_idx, reference in enumerate(references, 1):
            ref_id = f'ref{ref_idx}'
            scores = []
            
            # Evaluate against this single reference
            scores.extend(self.evaluate_bleu(hypothesis, [reference]))
            scores.extend(self.evaluate_chrf(hypothesis, [reference]))
            scores.extend(self.evaluate_meteor(hypothesis, [reference]))
            scores.extend(self.evaluate_rouge(hypothesis, [reference]))
            scores.extend(self.evaluate_bertscore(hypothesis, [reference]))
            scores.extend(self.evaluate_bleurt(hypothesis, [reference]))
            
            if source:
                scores.extend(self.evaluate_comet(hypothesis, [reference], source))
            
            per_ref_scores[ref_id] = scores
        
        return per_ref_scores
    
    def evaluate_chunk(
        self, 
        chunk_id: str,
        source_text: str,
        model_translations: Dict[str, str],
        reference_translations: List[str],
        include_per_reference: bool = True
    ) -> List[ChunkEvaluation]:
        """
        Evaluate all model translations for a chunk using proper multi-reference methodology.
        
        Args:
            chunk_id: Chunk identifier
            source_text: Original Greek text
            model_translations: Dict mapping model names to translations
            reference_translations: List of reference translations
            include_per_reference: Whether to include per-reference breakdown
            
        Returns:
            List of ChunkEvaluation objects (one per model, with multi-ref scores)
        """
        evaluations = []
        
        for model_name, translation in model_translations.items():
            if not translation or translation.strip() == '':
                logger.warning(f"Empty translation for {chunk_id}/{model_name}, skipping")
                continue
            
            logger.info(f"Evaluating {chunk_id}/{model_name} against {len(reference_translations)} references...")
            
            # Get multi-reference scores (proper methodology)
            scores = self.evaluate_single(translation, reference_translations, source_text)
            
            # Optionally get per-reference breakdown for detailed analysis
            per_ref_scores = {}
            if include_per_reference:
                per_ref_data = self.evaluate_per_reference(translation, reference_translations, source_text)
                for ref_id, ref_scores in per_ref_data.items():
                    per_ref_scores[ref_id] = {score.metric_name: score.score for score in ref_scores}
            
            evaluation = ChunkEvaluation(
                chunk_id=chunk_id,
                model_name=model_name,
                scores=scores,
                per_reference_scores=per_ref_scores
            )
            evaluations.append(evaluation)
        
        return evaluations
    
    def evaluate_all(
        self,
        parsed_chunks: List,  # List of ParsedChunk objects
        translations: Dict[str, Dict[str, any]]  # Translation results
    ) -> List[ChunkEvaluation]:
        """
        Evaluate all chunks.
        
        Args:
            parsed_chunks: List of ParsedChunk objects with source and references
            translations: Dict mapping chunk_id to model translations
            
        Returns:
            List of all evaluations
        """
        all_evaluations = []
        
        for chunk in parsed_chunks:
            chunk_id = chunk.chunk_id
            
            if chunk_id not in translations:
                logger.warning(f"No translations found for chunk {chunk_id}")
                continue
            
            # Get model translations
            model_translations = {}
            for model, trans_obj in translations[chunk_id].items():
                if hasattr(trans_obj, 'translation'):
                    model_translations[model] = trans_obj.translation
                elif isinstance(trans_obj, dict) and 'translation' in trans_obj:
                    model_translations[model] = trans_obj['translation']
                else:
                    model_translations[model] = str(trans_obj)
            
            # Evaluate
            chunk_evaluations = self.evaluate_chunk(
                chunk_id=chunk_id,
                source_text=chunk.greek_text,
                model_translations=model_translations,
                reference_translations=chunk.reference_translations
            )
            
            all_evaluations.extend(chunk_evaluations)
        
        logger.info(f"Completed {len(all_evaluations)} evaluations")
        return all_evaluations
    
    def aggregate_results(self, evaluations: List[ChunkEvaluation]) -> Dict:
        """
        Aggregate evaluation results into summary statistics.
        
        Returns:
            Dict with aggregated results including:
            - Per-model, per-metric averages
            - Overall rankings
            - Statistical summaries
            - Per-reference breakdown (for detailed analysis)
        """
        from collections import defaultdict
        
        # Organize scores by model and metric
        scores_by_model_metric = defaultdict(lambda: defaultdict(list))
        
        # Also collect per-reference scores for detailed analysis
        per_ref_by_model_metric = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        
        for eval in evaluations:
            model = eval.model_name
            
            # Primary multi-reference scores
            for score in eval.scores:
                metric = score.metric_name
                scores_by_model_metric[model][metric].append(score.score)
            
            # Per-reference breakdown (for detailed analysis)
            for ref_id, ref_scores in eval.per_reference_scores.items():
                for metric, score_val in ref_scores.items():
                    per_ref_by_model_metric[model][metric][ref_id].append(score_val)
        
        # Calculate aggregates
        summary = {
            'methodology': 'multi-reference',
            'methodology_details': {
                'bleu-4': 'multi-reference (n-grams matched against any reference)',
                'chrf++': 'multi-reference (native support, includes word bigrams)',
                'meteor': 'multi-reference (native support, includes synonyms/stems)',
                'rouge-l': 'max across references',
                'bertscore': 'max across references',
                'comet': 'max across references',
                'bleurt': 'max across references'
            },
            'by_model': {},
            'by_metric': {},
            'by_reference': {},
            'overall_rankings': [],
            'detailed_scores': []
        }
        
        # Per-model statistics
        model_averages = {}
        for model in scores_by_model_metric:
            summary['by_model'][model] = {}
            all_model_scores = []
            
            for metric in scores_by_model_metric[model]:
                scores = scores_by_model_metric[model][metric]
                summary['by_model'][model][metric] = {
                    'mean': float(np.mean(scores)),
                    'std': float(np.std(scores)),
                    'min': float(np.min(scores)),
                    'max': float(np.max(scores)),
                    'count': len(scores)
                }
                all_model_scores.extend(scores)
            
            model_averages[model] = np.mean(all_model_scores) if all_model_scores else 0.0
        
        # Overall rankings
        summary['overall_rankings'] = sorted(
            model_averages.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Per-metric best models
        for model in scores_by_model_metric:
            for metric in scores_by_model_metric[model]:
                if metric not in summary['by_metric']:
                    summary['by_metric'][metric] = {}
                
                scores = scores_by_model_metric[model][metric]
                summary['by_metric'][metric][model] = float(np.mean(scores))
        
        # Best model per metric
        for metric in summary['by_metric']:
            model_scores = {k: v for k, v in summary['by_metric'][metric].items() if k != 'best_model'}
            if model_scores:
                best_model = max(model_scores.items(), key=lambda x: x[1])
                summary['by_metric'][metric]['best_model'] = {
                    'name': best_model[0],
                    'score': best_model[1]
                }
        
        # Per-reference breakdown (for detailed analysis)
        for model in per_ref_by_model_metric:
            if model not in summary['by_reference']:
                summary['by_reference'][model] = {}
            
            for metric in per_ref_by_model_metric[model]:
                if metric not in summary['by_reference'][model]:
                    summary['by_reference'][model][metric] = {}
                
                for ref_id in per_ref_by_model_metric[model][metric]:
                    scores = per_ref_by_model_metric[model][metric][ref_id]
                    summary['by_reference'][model][metric][ref_id] = {
                        'mean': float(np.mean(scores)),
                        'std': float(np.std(scores)),
                        'count': len(scores)
                    }
        
        # Add detailed scores
        summary['detailed_scores'] = [eval.to_dict() for eval in evaluations]
        
        return summary
    
    def save_results(self, evaluations: List[ChunkEvaluation], output_file: str):
        """Save evaluation results to JSON."""
        summary = self.aggregate_results(evaluations)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation results saved to {output_file}")
        return summary


def main():
    """Command-line interface."""
    import argparse
    import sys
    import os
    # Ensure we import our parser, not Python's built-in
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from parser import InputParser
    
    parser = argparse.ArgumentParser(description="Evaluate translations")
    parser.add_argument('input_file', help='Input file with Greek and references')
    parser.add_argument('translations_file', help='JSON file with model translations')
    parser.add_argument('-o', '--output', help='Output file for evaluation results')
    parser.add_argument('--metrics', nargs='+', 
                       choices=['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet', 'bleurt'],
                       default=['bleu', 'chrf', 'meteor', 'rouge', 'bertscore', 'comet'],
                       help='Metrics to use (add bleurt on Linux)')
    parser.add_argument('--gpu', action='store_true', help='Use GPU for neural metrics')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse input
    input_parser = InputParser()
    chunks = input_parser.parse_file(args.input_file)
    
    # Load translations
    with open(args.translations_file, 'r', encoding='utf-8') as f:
        translations = json.load(f)
    
    # Evaluate
    evaluator = Evaluator(metrics=args.metrics, use_gpu=args.gpu)
    evaluations = evaluator.evaluate_all(chunks, translations)
    
    # Save
    if args.output:
        output_file = args.output
    else:
        output_file = 'output/evaluations/evaluation_results.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    summary = evaluator.save_results(evaluations, output_file)
    
    # Print summary
    print(f"\n{'='*80}")
    print("EVALUATION SUMMARY")
    print(f"{'='*80}\n")
    print("Overall Rankings:")
    for i, (model, score) in enumerate(summary['overall_rankings'], 1):
        print(f"  {i}. {model.upper()}: {score:.4f}")
    
    print(f"\n✓ Results saved to {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
