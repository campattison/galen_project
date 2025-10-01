#!/usr/bin/env python3
"""
Test script for the translation evaluation framework.

Demonstrates usage with demo data and validates the evaluation pipeline.
"""

import os
import sys
import json
from pathlib import Path

# Add evaluation directory to path
sys.path.append(str(Path(__file__).parent))

from demo_data_generator import DemoGoldStandardGenerator
from translation_evaluator import TranslationEvaluator
from statistical_tests import StatisticalTester


def test_evaluation_pipeline():
    """Test the complete evaluation pipeline."""
    
    print("🧪 Testing Translation Evaluation Framework")
    print("=" * 50)
    
    # Step 1: Generate demo data
    print("\n1️⃣ Generating demo data...")
    generator = DemoGoldStandardGenerator()
    ai_file = generator.generate_demo_ai_translations("evaluation/demo_data/test_ai_translations.json")
    gold_file = generator.generate_gold_standard_file("evaluation/demo_data/test_gold_standard.json")
    
    # Step 2: Initialize evaluator
    print("\n2️⃣ Initializing evaluator...")
    evaluator = TranslationEvaluator(use_gpu=False)
    
    # Step 3: Run evaluation
    print("\n3️⃣ Running evaluation...")
    try:
        results = evaluator.evaluate_translation_file(ai_file, gold_file)
        
        # Save results
        results_file = "evaluation/outputs/test_evaluation_results.json"
        evaluator.save_results(results, results_file)
        
        # Print summary
        evaluator.print_summary(results)
        
        # Step 4: Statistical testing
        print("\n4️⃣ Running statistical tests...")
        tester = StatisticalTester(alpha=0.05)
        statistical_results = tester.compare_models_pairwise(results)
        
        # Save statistical results
        stats_file = "evaluation/outputs/test_statistical_results.json"
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(statistical_results, f, indent=2, ensure_ascii=False)
        
        # Print statistical summary
        summary = statistical_results['summary']
        print(f"\n📊 Statistical Testing Summary:")
        print(f"  • Total comparisons: {summary['total_comparisons']}")
        print(f"  • Significant differences: {summary['significant_count']}")
        print(f"  • Significance rate: {summary['significance_rate']:.2%}")
        
        # Step 5: Cleanup test files
        print("\n5️⃣ Cleaning up test files...")
        test_files = [ai_file, gold_file, results_file, stats_file]
        for file in test_files:
            if os.path.exists(file):
                os.remove(file)
                print(f"  ✓ Removed {file}")
        
        print(f"\n✅ Evaluation framework test completed successfully!")
        print(f"\n📋 Available metrics: {', '.join(results['metrics_used'])}")
        print(f"📈 Best performing model: {results['model_rankings'][0][0].upper()}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_metrics():
    """Test individual metric calculations."""
    
    print("\n🔍 Testing Individual Metrics")
    print("=" * 30)
    
    # Sample data
    hypothesis = "The bodies of animals are indeed mixed from hot and cold and dry and wet elements."
    reference = "That the bodies of animals are compounded from hot and cold and dry and moist has been demonstrated."
    chunk_id = "test_1"
    model = "test_model"
    
    evaluator = TranslationEvaluator(use_gpu=False)
    
    # Test each metric type
    metrics_to_test = [
        ("ROUGE", evaluator.evaluate_rouge),
        ("BLEU", evaluator.evaluate_bleu), 
        ("METEOR", evaluator.evaluate_meteor),
        ("chrF", evaluator.evaluate_character_level),
        ("Semantic", evaluator.evaluate_semantic_similarity)
    ]
    
    for metric_name, metric_func in metrics_to_test:
        try:
            results = metric_func(hypothesis, reference, chunk_id, model)
            if results:
                print(f"\n✓ {metric_name}: {len(results)} scores calculated")
                for result in results[:2]:  # Show first 2 scores
                    print(f"  • {result.metric_name}: {result.score:.4f}")
            else:
                print(f"⚠️  {metric_name}: No scores (likely missing dependencies)")
        except Exception as e:
            print(f"❌ {metric_name}: Failed - {e}")


def check_dependencies():
    """Check which evaluation dependencies are available."""
    
    print("🔧 Checking Dependencies")
    print("=" * 25)
    
    dependencies = [
        ("ROUGE", "rouge_score"),
        ("NLTK", "nltk"),
        ("SentenceTransformers", "sentence_transformers"),
        ("BERTScore", "bert_score"),
        ("PyTorch", "torch"),
        ("Statsmodels", "statsmodels"),
        ("NumPy", "numpy"),
        ("Pandas", "pandas"),
        ("SciPy", "scipy")
    ]
    
    available = []
    missing = []
    
    for name, module in dependencies:
        try:
            __import__(module)
            available.append(name)
            print(f"✓ {name}")
        except ImportError:
            missing.append(name)
            print(f"❌ {name}")
    
    print(f"\n📊 Summary:")
    print(f"  • Available: {len(available)}/{len(dependencies)}")
    print(f"  • Missing: {', '.join(missing) if missing else 'None'}")
    
    if missing:
        print(f"\n💡 To install missing dependencies:")
        print(f"pip install -r evaluation/requirements.txt")
    
    return len(missing) == 0


def main():
    """Run all tests."""
    
    print("🎯 Translation Evaluation Framework Testing")
    print("=" * 45)
    
    # Check dependencies first
    all_deps_available = check_dependencies()
    
    if not all_deps_available:
        print(f"\n⚠️  Some dependencies are missing. Tests may be limited.")
        print(f"   Install with: pip install -r evaluation/requirements.txt")
    
    # Test individual metrics
    test_individual_metrics()
    
    # Test full pipeline
    pipeline_success = test_evaluation_pipeline()
    
    if pipeline_success:
        print(f"\n🎉 All tests passed! The evaluation framework is ready to use.")
        print(f"\n📖 Next steps:")
        print(f"  1. Create your gold standard translations")
        print(f"  2. Run evaluation on real translation data") 
        print(f"  3. Use statistical tests to compare models")
    else:
        print(f"\n⚠️  Some tests failed. Check dependencies and error messages.")
    
    return 0 if pipeline_success else 1


if __name__ == "__main__":
    exit(main())
