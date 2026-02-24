"""
Galen Translation Evaluation Pipeline

A streamlined system for translating Ancient Greek texts and evaluating
translation quality using state-of-the-art NLP metrics.
"""

from .parser import InputParser, ParsedChunk
from .translator import Translator, Translation
from .evaluator import Evaluator, EvaluationScore, ChunkEvaluation
from .reporter import Reporter

__all__ = [
    'InputParser',
    'ParsedChunk',
    'Translator',
    'Translation',
    'Evaluator',
    'EvaluationScore',
    'ChunkEvaluation',
    'Reporter'
]

