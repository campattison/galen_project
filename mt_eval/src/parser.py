#!/usr/bin/env python3
"""
Input Document Parser

Parses input documents containing:
- Greek text chunks
- Reference translations (usually 2 per chunk)

Handles the format from 10_chunks.txt and similar documents.
"""

import re
from typing import Dict, List, Tuple
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ParsedChunk:
    """A single parsed chunk with Greek and reference translations."""
    chunk_id: str
    greek_text: str
    reference_translations: List[str]
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class InputParser:
    """Parse input documents into structured chunks."""
    
    def __init__(self):
        self.greek_pattern = re.compile(r'[α-ωΑ-Ωἀ-ἇἰ-ἷὀ-὇ὐ-ὗὠ-ὧᾀ-ᾇᾐ-ᾗᾠ-ᾧᾰ-ᾱῐ-ῑῠ-ῡ]+')
    
    def has_greek_characters(self, text: str) -> bool:
        """Check if text contains Greek characters."""
        return bool(self.greek_pattern.search(text))
    
    def is_substantial_text(self, text: str, min_words: int = 10) -> bool:
        """Check if text is substantial (not just a label or fragment)."""
        words = text.split()
        return len(words) >= min_words and len(text.strip()) > 50
    
    def parse_file(self, file_path: str) -> List[ParsedChunk]:
        """
        Parse a file into structured chunks.
        
        Args:
            file_path: Path to input file
            
        Returns:
            List of ParsedChunk objects
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content)
    
    def parse_content(self, content: str) -> List[ParsedChunk]:
        """
        Parse content into structured chunks.
        
        Expected format:
        Chunk 1
        
        [Greek text]
        
        [Reference translation 1]
        
        [Reference translation 2]
        
        Chunk 2
        ...
        
        Args:
            content: Full document content
            
        Returns:
            List of ParsedChunk objects
        """
        chunks = []
        
        # Split by "Chunk N" markers
        chunk_pattern = r'(?:^|\n)Chunk\s+(\d+)\s*\n'
        parts = re.split(chunk_pattern, content, flags=re.MULTILINE)
        
        # parts will be: ['', '1', content1, '2', content2, ...]
        # Skip first empty element, then process pairs
        i = 1
        while i < len(parts) - 1:
            chunk_number = parts[i]
            chunk_content = parts[i + 1]
            
            parsed = self._parse_chunk_content(chunk_number, chunk_content)
            if parsed:
                chunks.append(parsed)
            
            i += 2
        
        logger.info(f"Parsed {len(chunks)} chunks from document")
        return chunks
    
    def _parse_chunk_content(self, chunk_number: str, content: str) -> ParsedChunk:
        """
        Parse the content of a single chunk.
        
        Strategy:
        1. Split into paragraphs (separated by blank lines)
        2. Identify Greek paragraph (contains Greek characters)
        3. Remaining substantial paragraphs are reference translations
        4. If a paragraph is very long, try to split it (may be multiple references)
        
        Args:
            chunk_number: The chunk identifier
            content: The chunk's content
            
        Returns:
            ParsedChunk object or None if parsing fails
        """
        # Split into paragraphs
        paragraphs = re.split(r'\n\s*\n', content)
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        # Find Greek paragraph
        greek_text = None
        references = []
        
        for para in paragraphs:
            # Clean up the paragraph
            para_clean = re.sub(r'\s+', ' ', para).strip()
            
            if not para_clean:
                continue
            
            # Check if this is the Greek text
            if self.has_greek_characters(para_clean):
                if greek_text is None:
                    greek_text = para_clean
                    logger.debug(f"Chunk {chunk_number}: Found Greek text ({len(para_clean)} chars)")
                else:
                    # Multiple Greek paragraphs - append to first one
                    greek_text += " " + para_clean
            
            # Check if this is a reference translation
            elif self.is_substantial_text(para_clean, min_words=20):
                # Check if this might be multiple references combined (very long paragraph)
                word_count = len(para_clean.split())
                if word_count > 400:  # Suspiciously long - might be 2+ translations
                    # Try to split at sentence boundaries that look like translation restarts
                    split_refs = self._try_split_combined_references(para_clean)
                    if len(split_refs) > 1:
                        logger.debug(f"Chunk {chunk_number}: Split long paragraph into {len(split_refs)} references")
                        references.extend(split_refs)
                    else:
                        references.append(para_clean)
                else:
                    references.append(para_clean)
                logger.debug(f"Chunk {chunk_number}: Found reference translation ({len(para_clean)} chars)")
        
        # Validate we found what we need
        if not greek_text:
            logger.warning(f"Chunk {chunk_number}: No Greek text found")
            return None
        
        if len(references) == 0:
            logger.warning(f"Chunk {chunk_number}: No reference translations found")
            return None
        
        if len(references) > 2:
            logger.warning(f"Chunk {chunk_number}: Found {len(references)} reference translations (expected 1-2)")
        
        return ParsedChunk(
            chunk_id=str(chunk_number),
            greek_text=greek_text,
            reference_translations=references,
            metadata={
                'greek_length': len(greek_text),
                'greek_words': len(greek_text.split()),
                'num_references': len(references),
                'reference_lengths': [len(ref) for ref in references]
            }
        )
    
    def _try_split_combined_references(self, text: str) -> List[str]:
        """
        Try to split a long text that might contain multiple reference translations.
        
        Looks for patterns that indicate the start of a new translation, such as:
        - Sentence starts that mirror the beginning of the passage
        - Multiple very long sections
        
        Args:
            text: Potentially combined reference text
            
        Returns:
            List of split references (or single item if no split found)
        """
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        # If we don't have many sentences, don't try to split
        if len(sentences) < 8:
            return [text]
        
        # Look for natural split points (roughly in the middle)
        # A good split point is usually where a new translation starts with similar wording
        midpoint = len(sentences) // 2
        search_range = range(max(0, midpoint - 2), min(len(sentences), midpoint + 3))
        
        # Look for sentences that start with capital words and look like restart patterns
        # Common patterns: "That the...", "And this...", "In these...", "Therefore...", etc.
        restart_patterns = [
            r'^(That|And|In|For|Therefore|Now|However|But|Of|All|The)\s+',
            r'^[A-Z][a-z]+\s+[a-z]+\s+[a-z]+',  # Normal sentence pattern
        ]
        
        best_split = None
        best_score = 0
        
        for i in search_range:
            sentence = sentences[i]
            # Check if this looks like a restart
            for pattern in restart_patterns:
                if re.match(pattern, sentence):
                    # Score based on proximity to midpoint
                    score = 1.0 - abs(i - midpoint) / len(sentences)
                    if score > best_score:
                        best_score = score
                        best_split = i
                        break
        
        # If we found a good split point, split there
        if best_split and best_score > 0.3:
            first_part = ' '.join(sentences[:best_split]).strip()
            second_part = ' '.join(sentences[best_split:]).strip()
            
            # Make sure both parts are substantial
            if len(first_part.split()) > 50 and len(second_part.split()) > 50:
                return [first_part, second_part]
        
        # No good split found
        return [text]
    
    def validate_parsed_chunks(self, chunks: List[ParsedChunk]) -> bool:
        """
        Validate that parsed chunks are reasonable.
        
        Args:
            chunks: List of parsed chunks
            
        Returns:
            True if validation passes
        """
        if not chunks:
            logger.error("No chunks parsed!")
            return False
        
        all_valid = True
        
        for chunk in chunks:
            # Check Greek text
            if not chunk.greek_text or len(chunk.greek_text) < 50:
                logger.error(f"Chunk {chunk.chunk_id}: Greek text too short or missing")
                all_valid = False
            
            # Check references
            if not chunk.reference_translations:
                logger.error(f"Chunk {chunk.chunk_id}: No reference translations")
                all_valid = False
            
            # Check for at least one substantial reference
            substantial_refs = [r for r in chunk.reference_translations if len(r) > 100]
            if not substantial_refs:
                logger.error(f"Chunk {chunk.chunk_id}: No substantial reference translations")
                all_valid = False
        
        if all_valid:
            logger.info("✓ All chunks validated successfully")
        
        return all_valid
    
    def print_summary(self, chunks: List[ParsedChunk]):
        """Print a human-readable summary of parsed chunks."""
        print(f"\n{'='*80}")
        print(f"PARSED {len(chunks)} CHUNKS")
        print(f"{'='*80}\n")
        
        for chunk in chunks:
            print(f"Chunk {chunk.chunk_id}:")
            print(f"  Greek: {chunk.metadata['greek_words']} words, {chunk.metadata['greek_length']} chars")
            print(f"  References: {chunk.metadata['num_references']}")
            for i, length in enumerate(chunk.metadata['reference_lengths'], 1):
                print(f"    Ref {i}: {length} chars")
            
            # Show preview
            greek_preview = chunk.greek_text[:80] + "..." if len(chunk.greek_text) > 80 else chunk.greek_text
            print(f"  Preview: {greek_preview}")
            print()


def main():
    """Command-line interface for parser."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Parse Ancient Greek text documents")
    parser.add_argument('input_file', help='Input file to parse')
    parser.add_argument('--validate', action='store_true', help='Validate parsed chunks')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse file
    input_parser = InputParser()
    chunks = input_parser.parse_file(args.input_file)
    
    # Print summary
    input_parser.print_summary(chunks)
    
    # Validate if requested
    if args.validate:
        is_valid = input_parser.validate_parsed_chunks(chunks)
        if not is_valid:
            print("⚠️  Validation failed - check warnings above")
            return 1
        else:
            print("✓ Validation passed")
    
    return 0


if __name__ == "__main__":
    exit(main())

