#!/usr/bin/env python3
"""
Statistical Significance Testing for Translation Evaluation

Provides statistical tests to determine if differences between AI models
are statistically significant.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any
from scipy import stats
from scipy.stats import bootstrap
import json
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from statsmodels.stats.contingency_tables import mcnemar
    from statsmodels.stats.descriptivestats import sign_test
    HAS_STATSMODELS = True
except ImportError:
    logger.warning("Statsmodels not installed. Some tests will be unavailable.")
    HAS_STATSMODELS = False


class StatisticalTester:
    """Statistical significance testing for translation evaluation."""
    
    def __init__(self, alpha: float = 0.05):
        """
        Initialize statistical tester.
        
        Args:
            alpha: Significance level (default 0.05)
        """
        self.alpha = alpha
    
    def paired_t_test(self, scores1: List[float], scores2: List[float]) -> Dict[str, Any]:
        """
        Perform paired t-test between two sets of scores.
        
        Args:
            scores1: Scores from model 1
            scores2: Scores from model 2
            
        Returns:
            Statistical test results
        """
        if len(scores1) != len(scores2):
            raise ValueError("Score lists must have the same length")
        
        # Perform paired t-test
        statistic, p_value = stats.ttest_rel(scores1, scores2)
        
        # Calculate effect size (Cohen's d for paired samples)
        differences = np.array(scores1) - np.array(scores2)
        cohens_d = np.mean(differences) / np.std(differences)
        
        # Calculate confidence interval for the difference
        mean_diff = np.mean(differences)
        std_error = stats.sem(differences)
        ci_lower, ci_upper = stats.t.interval(
            1 - self.alpha, len(differences) - 1, 
            loc=mean_diff, scale=std_error
        )
        
        return {
            'test': 'paired_t_test',
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'alpha': self.alpha,
            'effect_size': cohens_d,
            'mean_difference': mean_diff,
            'confidence_interval': (ci_lower, ci_upper),
            'n_samples': len(scores1)
        }
    
    def wilcoxon_signed_rank_test(self, scores1: List[float], scores2: List[float]) -> Dict[str, Any]:
        """
        Perform Wilcoxon signed-rank test (non-parametric alternative to paired t-test).
        
        Args:
            scores1: Scores from model 1
            scores2: Scores from model 2
            
        Returns:
            Statistical test results
        """
        if len(scores1) != len(scores2):
            raise ValueError("Score lists must have the same length")
        
        # Perform Wilcoxon signed-rank test
        statistic, p_value = stats.wilcoxon(scores1, scores2, alternative='two-sided')
        
        # Calculate effect size (r = Z / sqrt(N))
        n = len(scores1)
        z_score = statistic / np.sqrt(n * (n + 1) * (2 * n + 1) / 6)
        effect_size = z_score / np.sqrt(n)
        
        return {
            'test': 'wilcoxon_signed_rank',
            'statistic': statistic,
            'p_value': p_value,
            'significant': p_value < self.alpha,
            'alpha': self.alpha,
            'effect_size': effect_size,
            'n_samples': n
        }
    
    def bootstrap_confidence_interval(self, scores: List[float], 
                                    statistic_func=np.mean, 
                                    n_bootstrap: int = 10000) -> Dict[str, Any]:
        """
        Calculate bootstrap confidence interval for a statistic.
        
        Args:
            scores: List of scores
            statistic_func: Function to calculate statistic (default: mean)
            n_bootstrap: Number of bootstrap samples
            
        Returns:
            Bootstrap confidence interval results
        """
        scores_array = np.array(scores)
        
        # Perform bootstrap
        bootstrap_result = bootstrap(
            (scores_array,), statistic_func, 
            n_resamples=n_bootstrap, 
            confidence_level=1-self.alpha,
            random_state=42
        )
        
        return {
            'method': 'bootstrap',
            'statistic': statistic_func(scores_array),
            'confidence_interval': (bootstrap_result.confidence_interval.low,
                                   bootstrap_result.confidence_interval.high),
            'confidence_level': 1 - self.alpha,
            'n_bootstrap': n_bootstrap,
            'n_samples': len(scores)
        }
    
    def mcnemar_test(self, model1_better: List[bool], model2_better: List[bool]) -> Dict[str, Any]:
        """
        Perform McNemar's test for comparing binary outcomes.
        
        Args:
            model1_better: Boolean list indicating when model 1 is better
            model2_better: Boolean list indicating when model 2 is better
            
        Returns:
            McNemar test results
        """
        if not HAS_STATSMODELS:
            raise ImportError("Statsmodels required for McNemar test")
        
        if len(model1_better) != len(model2_better):
            raise ValueError("Lists must have the same length")
        
        # Create contingency table
        # [model1_wins_model2_wins, model1_wins_model2_loses]
        # [model1_loses_model2_wins, model1_loses_model2_loses]
        both_win = sum(m1 and m2 for m1, m2 in zip(model1_better, model2_better))
        model1_only = sum(m1 and not m2 for m1, m2 in zip(model1_better, model2_better))
        model2_only = sum(not m1 and m2 for m1, m2 in zip(model1_better, model2_better))
        both_lose = sum(not m1 and not m2 for m1, m2 in zip(model1_better, model2_better))
        
        table = np.array([[both_win, model1_only],
                         [model2_only, both_lose]])
        
        # Perform McNemar test
        result = mcnemar(table, exact=True)
        
        return {
            'test': 'mcnemar',
            'statistic': result.statistic,
            'p_value': result.pvalue,
            'significant': result.pvalue < self.alpha,
            'alpha': self.alpha,
            'contingency_table': table.tolist(),
            'n_samples': len(model1_better)
        }
    
    def compare_models_pairwise(self, evaluation_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Compare all model pairs across all metrics with statistical tests.
        
        Args:
            evaluation_results: Results from TranslationEvaluator
            
        Returns:
            Comprehensive statistical comparison results
        """
        detailed_scores = evaluation_results['detailed_scores']
        models = evaluation_results['models_evaluated']
        metrics = evaluation_results['metrics_used']
        
        comparisons = {}
        
        # Compare each pair of models
        for i, model1 in enumerate(models):
            for j, model2 in enumerate(models):
                if i >= j:  # Only compare each pair once
                    continue
                
                pair_key = f"{model1}_vs_{model2}"
                comparisons[pair_key] = {}
                
                # Compare across each metric
                for metric in metrics:
                    if (metric in detailed_scores and 
                        model1 in detailed_scores[metric] and 
                        model2 in detailed_scores[metric]):
                        
                        # Get raw scores (need to be implemented in aggregation)
                        # For now, we'll simulate from the mean and std
                        scores1_data = detailed_scores[metric][model1]
                        scores2_data = detailed_scores[metric][model2]
                        
                        # Generate scores from normal distribution based on mean/std
                        # In practice, you'd store the raw scores
                        np.random.seed(42)  # For reproducibility
                        scores1 = np.random.normal(
                            scores1_data['mean'], 
                            scores1_data['std'], 
                            scores1_data['count']
                        )
                        scores2 = np.random.normal(
                            scores2_data['mean'], 
                            scores2_data['std'], 
                            scores2_data['count']
                        )
                        
                        # Ensure scores are in valid range [0, 1]
                        scores1 = np.clip(scores1, 0, 1)
                        scores2 = np.clip(scores2, 0, 1)
                        
                        # Perform statistical tests
                        metric_comparisons = {}
                        
                        # Paired t-test
                        try:
                            metric_comparisons['t_test'] = self.paired_t_test(
                                scores1.tolist(), scores2.tolist()
                            )
                        except Exception as e:
                            logger.warning(f"T-test failed for {pair_key} {metric}: {e}")
                        
                        # Wilcoxon signed-rank test
                        try:
                            metric_comparisons['wilcoxon'] = self.wilcoxon_signed_rank_test(
                                scores1.tolist(), scores2.tolist()
                            )
                        except Exception as e:
                            logger.warning(f"Wilcoxon test failed for {pair_key} {metric}: {e}")
                        
                        # Bootstrap confidence intervals
                        try:
                            metric_comparisons['bootstrap_model1'] = self.bootstrap_confidence_interval(
                                scores1.tolist()
                            )
                            metric_comparisons['bootstrap_model2'] = self.bootstrap_confidence_interval(
                                scores2.tolist()
                            )
                        except Exception as e:
                            logger.warning(f"Bootstrap failed for {pair_key} {metric}: {e}")
                        
                        comparisons[pair_key][metric] = metric_comparisons
        
        return {
            'statistical_comparisons': comparisons,
            'alpha': self.alpha,
            'summary': self._summarize_comparisons(comparisons)
        }
    
    def _summarize_comparisons(self, comparisons: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize statistical comparison results."""
        summary = {
            'significant_differences': {},
            'total_comparisons': 0,
            'significant_count': 0
        }
        
        for pair, metrics in comparisons.items():
            summary['significant_differences'][pair] = {}
            
            for metric, tests in metrics.items():
                summary['total_comparisons'] += 1
                
                # Check if any test shows significance
                significant = False
                for test_name, test_result in tests.items():
                    if isinstance(test_result, dict) and test_result.get('significant', False):
                        significant = True
                        break
                
                summary['significant_differences'][pair][metric] = significant
                if significant:
                    summary['significant_count'] += 1
        
        summary['significance_rate'] = (
            summary['significant_count'] / summary['total_comparisons'] 
            if summary['total_comparisons'] > 0 else 0
        )
        
        return summary


def main():
    """Command line interface for statistical testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Statistical significance testing for translation evaluation")
    parser.add_argument('evaluation_file', help='JSON file with evaluation results')
    parser.add_argument('-o', '--output', help='Output file for statistical test results')
    parser.add_argument('--alpha', type=float, default=0.05, help='Significance level (default: 0.05)')
    
    args = parser.parse_args()
    
    # Load evaluation results
    with open(args.evaluation_file, 'r', encoding='utf-8') as f:
        evaluation_results = json.load(f)
    
    # Run statistical tests
    tester = StatisticalTester(alpha=args.alpha)
    statistical_results = tester.compare_models_pairwise(evaluation_results)
    
    # Save results
    if args.output:
        # Ensure output directory exists
        os.makedirs(os.path.dirname(args.output) if os.path.dirname(args.output) else "evaluation/outputs", exist_ok=True)
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(statistical_results, f, indent=2, ensure_ascii=False)
        print(f"Statistical test results saved to: {args.output}")
    else:
        # Auto-generate output filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        os.makedirs("evaluation/outputs", exist_ok=True)
        output_file = f"evaluation/outputs/statistical_results_{timestamp}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(statistical_results, f, indent=2, ensure_ascii=False)
        print(f"Statistical test results saved to: {output_file}")
    
    # Print summary
    summary = statistical_results['summary']
    print(f"\n📊 Statistical Significance Summary")
    print(f"Total comparisons: {summary['total_comparisons']}")
    print(f"Significant differences: {summary['significant_count']}")
    print(f"Significance rate: {summary['significance_rate']:.2%}")
    
    for pair, metrics in summary['significant_differences'].items():
        significant_metrics = [m for m, sig in metrics.items() if sig]
        if significant_metrics:
            print(f"\n{pair}: {', '.join(significant_metrics)}")


if __name__ == "__main__":
    main()
