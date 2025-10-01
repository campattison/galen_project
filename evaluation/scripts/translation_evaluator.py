#!/usr/bin/env python3
"""
Comprehensive Translation Evaluation Framework

Evaluates AI translations against human gold standards using multiple NLP metrics
optimized for Ancient Greek texts.
"""

import os
import json
import argparse
import numpy as np
import pandas as pd
from typing import List, Dict, Tuple, Any, Optional
from datetime import datetime
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import evaluation libraries
try:
    from rouge_score import rouge_scorer
    from rouge_score.rouge_scorer import RougeScorer
except ImportError:
    logger.warning("ROUGE not installed. Run: pip install rouge-score")
    rouge_scorer = None

try:
    import nltk
    from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    from nltk.translate.meteor_score import meteor_score
    from nltk.tokenize import word_tokenize
except ImportError:
    logger.warning("NLTK not installed. Run: pip install nltk")
    nltk = None

try:
    from sentence_transformers import SentenceTransformer
    import torch
except ImportError:
    logger.warning("SentenceTransformers not installed. Run: pip install sentence-transformers")
    SentenceTransformer = None

try:
    from bert_score import score as bert_score
except ImportError:
    logger.warning("BERTScore not installed. Run: pip install bert-score")
    bert_score = None


@dataclass
class EvaluationResult:
    """Container for evaluation results."""
    metric_name: str
    score: float
    details: Dict[str, Any]
    chunk_id: str
    model_name: str


@dataclass
class ComparisonResult:
    """Container for model comparison results."""
    chunk_id: str
    source_text: str
    gold_standard: str
    model_scores: Dict[str, Dict[str, float]]
    best_model: str
    worst_model: str


class TranslationEvaluator:
    """
    Comprehensive evaluation framework for Ancient Greek translations.
    """
    
    def __init__(self, use_gpu: bool = False):
        """
        Initialize the evaluator with available metrics.
        
        Args:
            use_gpu: Whether to use GPU for deep learning metrics
        """
        self.use_gpu = use_gpu and torch.cuda.is_available() if 'torch' in globals() else False
        self.metrics = {}
        self.setup_metrics()
        
    def setup_metrics(self):
        """Initialize available evaluation metrics."""
        
        # ROUGE Metrics
        if rouge_scorer:
            self.metrics['rouge'] = RougeScorer(['rouge1', 'rouge2', 'rougeL', 'rougeLsum'], 
                                              use_stemmer=True)
        
        # NLTK Metrics
        if nltk:
            try:
                nltk.download('punkt', quiet=True)
                nltk.download('wordnet', quiet=True)
                nltk.download('omw-1.4', quiet=True)
                self.metrics['nltk'] = True
            except:
                logger.warning("Failed to download NLTK data")
        
        # Sentence Transformer for semantic similarity
        if SentenceTransformer:
            try:
                self.metrics['sentence_bert'] = SentenceTransformer('all-MiniLM-L6-v2')
                if self.use_gpu:
                    self.metrics['sentence_bert'] = self.metrics['sentence_bert'].cuda()
            except Exception as e:
                logger.warning(f"Failed to load SentenceTransformer: {e}")
        
        logger.info(f"Initialized evaluator with metrics: {list(self.metrics.keys())}")
    
    def evaluate_rouge(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate using ROUGE metrics."""
        if 'rouge' not in self.metrics:
            return []
        
        results = []
        scores = self.metrics['rouge'].score(reference, hypothesis)
        
        for metric_name, score_obj in scores.items():
            result = EvaluationResult(
                metric_name=f"ROUGE-{metric_name.upper()}",
                score=score_obj.fmeasure,
                details={
                    'precision': score_obj.precision,
                    'recall': score_obj.recall,
                    'fmeasure': score_obj.fmeasure
                },
                chunk_id=chunk_id,
                model_name=model
            )
            results.append(result)
        
        return results
    
    def evaluate_bleu(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate using BLEU variants."""
        if 'nltk' not in self.metrics:
            return []
        
        results = []
        
        # Tokenize
        hyp_tokens = word_tokenize(hypothesis.lower())
        ref_tokens = word_tokenize(reference.lower())
        
        # Sentence BLEU with different n-gram weights
        smoothing = SmoothingFunction().method1
        
        # BLEU-1 through BLEU-4
        weights_list = [
            (1.0, 0, 0, 0),      # BLEU-1
            (0.5, 0.5, 0, 0),    # BLEU-2
            (0.33, 0.33, 0.33, 0), # BLEU-3
            (0.25, 0.25, 0.25, 0.25) # BLEU-4
        ]
        
        for i, weights in enumerate(weights_list, 1):
            try:
                bleu_score = sentence_bleu([ref_tokens], hyp_tokens, 
                                         weights=weights, smoothing_function=smoothing)
                results.append(EvaluationResult(
                    metric_name=f"BLEU-{i}",
                    score=bleu_score,
                    details={'weights': weights},
                    chunk_id=chunk_id,
                    model_name=model
                ))
            except Exception as e:
                logger.warning(f"BLEU-{i} calculation failed: {e}")
        
        return results
    
    def evaluate_meteor(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate using METEOR score."""
        if 'nltk' not in self.metrics:
            return []
        
        try:
            # Tokenize
            hyp_tokens = word_tokenize(hypothesis.lower())
            ref_tokens = word_tokenize(reference.lower())
            
            meteor = meteor_score([ref_tokens], hyp_tokens)
            
            return [EvaluationResult(
                metric_name="METEOR",
                score=meteor,
                details={},
                chunk_id=chunk_id,
                model_name=model
            )]
        except Exception as e:
            logger.warning(f"METEOR calculation failed: {e}")
            return []
    
    def evaluate_character_level(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate character-level metrics (chrF) using sacrebleu."""
        try:
            from sacrebleu.metrics import CHRF
            
            chrf = CHRF()
            score = chrf.sentence_score(hypothesis, [reference])
            
            logger.info(f"✓ Using sacrebleu chrF (standard implementation) for chunk {chunk_id}")
            
            return [EvaluationResult(
                metric_name="chrF",
                score=score.score / 100,  # sacrebleu returns 0-100, normalize to 0-1
                details={
                    'precision': score.precision / 100,
                    'recall': score.recall / 100,
                    'raw_score': score.score,
                    'implementation': 'sacrebleu'
                },
                chunk_id=chunk_id,
                model_name=model
            )]
        except ImportError:
            logger.warning("⚠️ sacrebleu not available, using fallback chrF implementation (non-standard)")
            # Fallback to simplified chrF (not fully standard but better than nothing)
            return self._evaluate_character_level_fallback(hypothesis, reference, chunk_id, model)
        except Exception as e:
            logger.warning(f"chrF calculation failed: {e}")
            return []
    
    def _evaluate_character_level_fallback(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Fallback chrF implementation using multisets (correct counting)."""
        from collections import Counter
        
        def calculate_chrf_multiset(hyp: str, ref: str, n: int = 6, beta: float = 2.0) -> float:
            """Calculate character n-gram F-score with proper multiset counting."""
            hyp_ngrams = Counter()
            ref_ngrams = Counter()
            
            # Generate character n-grams with frequencies
            for i in range(1, n + 1):
                for j in range(len(hyp) - i + 1):
                    hyp_ngrams[hyp[j:j + i]] += 1
                for j in range(len(ref) - i + 1):
                    ref_ngrams[ref[j:j + i]] += 1
            
            if not hyp_ngrams or not ref_ngrams:
                return 0.0
            
            # Calculate matches (minimum count for each n-gram)
            matches = sum((hyp_ngrams & ref_ngrams).values())
            hyp_total = sum(hyp_ngrams.values())
            ref_total = sum(ref_ngrams.values())
            
            precision = matches / hyp_total if hyp_total > 0 else 0
            recall = matches / ref_total if ref_total > 0 else 0
            
            if precision + recall == 0:
                return 0.0
            
            # F-score with beta parameter (beta=2 favors recall, standard for chrF)
            f_score = (1 + beta**2) * precision * recall / (beta**2 * precision + recall)
            return f_score
        
        chrf_score = calculate_chrf_multiset(hypothesis.lower(), reference.lower())
        
        return [EvaluationResult(
            metric_name="chrF",
            score=chrf_score,
            details={
                'implementation': 'fallback',
                'warning': 'Using fallback implementation - install sacrebleu for standard chrF'
            },
            chunk_id=chunk_id,
            model_name=model
        )]
    
    def evaluate_semantic_similarity(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate semantic similarity using sentence embeddings."""
        if 'sentence_bert' not in self.metrics:
            return []
        
        try:
            # Encode sentences
            embeddings = self.metrics['sentence_bert'].encode([hypothesis, reference])
            
            # Calculate cosine similarity
            similarity = np.dot(embeddings[0], embeddings[1]) / (
                np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
            )
            
            return [EvaluationResult(
                metric_name="SentenceBERT",
                score=float(similarity),
                details={},
                chunk_id=chunk_id,
                model_name=model
            )]
        except Exception as e:
            logger.warning(f"Semantic similarity calculation failed: {e}")
            return []
    
    def evaluate_bert_score(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate using BERTScore."""
        if bert_score is None:
            return []
        
        try:
            P, R, F1 = bert_score([hypothesis], [reference], lang='en', verbose=False)
            
            return [EvaluationResult(
                metric_name="BERTScore",
                score=float(F1[0]),
                details={
                    'precision': float(P[0]),
                    'recall': float(R[0]),
                    'f1': float(F1[0])
                },
                chunk_id=chunk_id,
                model_name=model
            )]
        except Exception as e:
            logger.warning(f"BERTScore calculation failed: {e}")
            return []
    
    def evaluate_single_pair(self, hypothesis: str, reference: str, chunk_id: str, model: str) -> List[EvaluationResult]:
        """Evaluate a single hypothesis-reference pair using all available metrics."""
        all_results = []
        
        # ROUGE metrics
        all_results.extend(self.evaluate_rouge(hypothesis, reference, chunk_id, model))
        
        # BLEU metrics
        all_results.extend(self.evaluate_bleu(hypothesis, reference, chunk_id, model))
        
        # METEOR
        all_results.extend(self.evaluate_meteor(hypothesis, reference, chunk_id, model))
        
        # Character-level metrics
        all_results.extend(self.evaluate_character_level(hypothesis, reference, chunk_id, model))
        
        # Semantic similarity
        all_results.extend(self.evaluate_semantic_similarity(hypothesis, reference, chunk_id, model))
        
        # BERTScore
        all_results.extend(self.evaluate_bert_score(hypothesis, reference, chunk_id, model))
        
        return all_results
    
    def evaluate_translation_file(self, translation_file: str, gold_standard_file: str) -> Dict[str, Any]:
        """
        Evaluate AI translations against gold standard using all metrics.
        
        Args:
            translation_file: JSON file with AI translations
            gold_standard_file: JSON file with gold standard translations
            
        Returns:
            Comprehensive evaluation results
        """
        # Load data
        with open(translation_file, 'r', encoding='utf-8') as f:
            translations = json.load(f)
        
        with open(gold_standard_file, 'r', encoding='utf-8') as f:
            gold_standards = json.load(f)
        
        # Create mapping of chunk IDs to gold standards (with full context)
        gold_map = {}
        gold_full_data = {}
        for item in gold_standards:
            chunk_id = item['chunk_id']
            gold_map[chunk_id] = item['translation']
            gold_full_data[chunk_id] = item
        
        # Evaluate each model's translations
        all_results = []
        model_names = set()
        translation_examples = []  # Store examples for reporting
        
        # Support both 'paragraphs' and 'chunks' format
        items = translations.get('paragraphs', translations.get('chunks', []))
        
        for item in items:
            # Support both 'number' and 'id' for chunk identification
            chunk_id = str(item.get('number', item.get('id', '')))
            
            if chunk_id not in gold_map:
                logger.warning(f"No gold standard for chunk {chunk_id}")
                continue
            
            gold_standard = gold_map[chunk_id]
            gold_info = gold_full_data[chunk_id]
            
            # Store translation example for reporting
            example = {
                'chunk_id': chunk_id,
                'source_text': item.get('content', gold_info.get('greek_text', '')),
                'reference_translation': gold_standard,
                'reference_metadata': {
                    'translator': gold_info.get('translator', 'Unknown'),
                    'passage_name': gold_info.get('passage_name', ''),
                    'edition': gold_info.get('edition', '')
                },
                'candidate_translations': {}
            }
            
            # Evaluate each model
            for model in ['openai', 'claude', 'gemini']:
                translation_key = f'{model}_translation'
                status_key = f'{model}_status'
                
                if translation_key in item and item.get(status_key) == 'completed':
                    hypothesis = item[translation_key]
                    model_names.add(model)
                    
                    # Add to examples
                    example['candidate_translations'][model] = hypothesis
                    
                    # Evaluate this model's translation
                    results = self.evaluate_single_pair(hypothesis, gold_standard, chunk_id, model)
                    all_results.extend(results)
            
            if example['candidate_translations']:
                translation_examples.append(example)
        
        # Aggregate results
        aggregated = self._aggregate_results(all_results, model_names)
        
        # Add translation examples to output
        aggregated['translation_examples'] = translation_examples
        aggregated['source_files'] = {
            'translations': translation_file,
            'gold_standards': gold_standard_file
        }
        
        return aggregated
    
    def _aggregate_results(self, results: List[EvaluationResult], model_names: set) -> Dict[str, Any]:
        """Aggregate evaluation results into summary statistics."""
        
        # Group results by metric and model
        grouped = {}
        for result in results:
            metric = result.metric_name
            model = result.model_name
            
            if metric not in grouped:
                grouped[metric] = {}
            if model not in grouped[metric]:
                grouped[metric][model] = []
            
            grouped[metric][model].append(result.score)
        
        # Calculate summary statistics
        summary = {
            'evaluation_timestamp': datetime.now().isoformat(),
            'total_evaluations': len(results),
            'models_evaluated': list(model_names),
            'metrics_used': list(grouped.keys()),
            'detailed_scores': {},
            'model_rankings': {},
            'metric_summary': {},
            'methodology_notes': {
                'metric_averaging': 'IMPORTANT: Model rankings use simple average across all metrics. This assumes equal importance of all metrics, which may not reflect translation quality priorities. Consider weighted averaging based on domain expert input.',
                'sample_size_warning': f'Based on {len(set(r.chunk_id for r in results))} passage(s). Minimum 30 passages recommended for statistical validity.',
                'single_reference': 'Evaluation uses single reference translation. Multiple references would increase reliability.'
            }
        }
        
        # Calculate mean scores for each metric-model combination
        for metric in grouped:
            summary['detailed_scores'][metric] = {}
            for model in grouped[metric]:
                scores = grouped[metric][model]
                summary['detailed_scores'][metric][model] = {
                    'mean': np.mean(scores),
                    'std': np.std(scores),
                    'count': len(scores),
                    'min': np.min(scores),
                    'max': np.max(scores)
                }
        
        # Rank models by average performance across metrics
        model_averages = {}
        for model in model_names:
            model_scores = []
            for metric in grouped:
                if model in grouped[metric]:
                    model_scores.extend(grouped[metric][model])
            if model_scores:
                model_averages[model] = np.mean(model_scores)
        
        summary['model_rankings'] = sorted(model_averages.items(), 
                                         key=lambda x: x[1], reverse=True)
        
        # Metric-wise best models
        for metric in grouped:
            metric_scores = {}
            for model in grouped[metric]:
                metric_scores[model] = np.mean(grouped[metric][model])
            
            if metric_scores:
                best_model = max(metric_scores.items(), key=lambda x: x[1])
                summary['metric_summary'][metric] = {
                    'best_model': best_model[0],
                    'best_score': best_model[1],
                    'all_scores': metric_scores
                }
        
        return summary
    
    def save_results(self, results: Dict[str, Any], output_file: str):
        """Save evaluation results to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Evaluation results saved to: {output_file}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print a human-readable summary of evaluation results."""
        print("\n" + "="*80)
        print("TRANSLATION EVALUATION SUMMARY")
        print("="*80)
        
        # Print methodology warnings first
        if 'methodology_notes' in results:
            print("\n⚠️  METHODOLOGY NOTES:")
            print("-" * 80)
            notes = results['methodology_notes']
            if 'metric_averaging' in notes:
                print(f"\n📊 Metric Averaging:")
                print(f"  {notes['metric_averaging']}")
            if 'sample_size_warning' in notes:
                print(f"\n📈 Sample Size:")
                print(f"  {notes['sample_size_warning']}")
            if 'single_reference' in notes:
                print(f"\n📚 Reference Translations:")
                print(f"  {notes['single_reference']}")
            print("\n" + "-" * 80)
        
        # Print translation examples
        if 'translation_examples' in results and results['translation_examples']:
            print("\n📖 TRANSLATION EXAMPLES:")
            print("-" * 80)
            for i, example in enumerate(results['translation_examples'][:3], 1):  # Show first 3
                print(f"\n--- Passage {example['chunk_id']} ---")
                
                # Source text
                source = example['source_text']
                if len(source) > 200:
                    source = source[:200] + "..."
                print(f"\nSource (Ancient Greek):")
                print(f"  {source}")
                
                # Reference
                ref_meta = example['reference_metadata']
                print(f"\nReference Translation ({ref_meta.get('translator', 'Unknown')}):")
                ref = example['reference_translation']
                if len(ref) > 200:
                    ref = ref[:200] + "..."
                print(f"  {ref}")
                
                # Candidates
                print(f"\nAI Translations:")
                for model, translation in example['candidate_translations'].items():
                    if len(translation) > 150:
                        translation = translation[:150] + "..."
                    print(f"  • {model.upper()}: {translation}")
            
            if len(results['translation_examples']) > 3:
                print(f"\n  ... and {len(results['translation_examples']) - 3} more passages")
            print("\n" + "-" * 80)
        
        print(f"\n📊 EVALUATION RESULTS:")
        print(f"  • Total evaluations: {results['total_evaluations']}")
        print(f"  • Models evaluated: {', '.join(results['models_evaluated'])}")
        print(f"  • Metrics used: {len(results['metrics_used'])}")
        
        print(f"\n🏆 Model Rankings (Overall):")
        for i, (model, score) in enumerate(results['model_rankings'], 1):
            print(f"  {i}. {model.upper()}: {score:.4f}")
        
        print(f"\n📈 Best Model by Metric:")
        for metric, data in results['metric_summary'].items():
            print(f"  • {metric}: {data['best_model'].upper()} ({data['best_score']:.4f})")
        
        print(f"\n📋 Detailed Scores:")
        for metric in results['detailed_scores']:
            print(f"\n  {metric}:")
            for model, scores in results['detailed_scores'][metric].items():
                print(f"    {model.upper()}: {scores['mean']:.4f} ± {scores['std']:.4f} (n={scores['count']})")


def main():
    """Command line interface for translation evaluation."""
    parser = argparse.ArgumentParser(description="Evaluate AI translations against gold standards")
    parser.add_argument('translation_file', help='JSON file with AI translations')
    parser.add_argument('gold_standard_file', help='JSON file with gold standard translations')
    parser.add_argument('-o', '--output', help='Output file for evaluation results')
    parser.add_argument('--gpu', action='store_true', help='Use GPU for deep learning metrics')
    parser.add_argument('--quiet', action='store_true', help='Suppress detailed output')
    
    args = parser.parse_args()
    
    # Auto-generate output filename if not provided
    if not args.output:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # Ensure output directory exists
        os.makedirs("evaluation/outputs", exist_ok=True)
        args.output = f"evaluation/outputs/evaluation_results_{timestamp}.json"
    
    # Initialize evaluator
    evaluator = TranslationEvaluator(use_gpu=args.gpu)
    
    # Run evaluation
    print(f"\n🔄 Evaluating translations...")
    print(f"📖 Translations: {args.translation_file}")
    print(f"🏆 Gold standard: {args.gold_standard_file}")
    
    try:
        results = evaluator.evaluate_translation_file(args.translation_file, args.gold_standard_file)
        
        # Save results
        evaluator.save_results(results, args.output)
        
        # Print summary
        if not args.quiet:
            evaluator.print_summary(results)
        
        print(f"\n✅ Evaluation complete! Results saved to: {args.output}")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
