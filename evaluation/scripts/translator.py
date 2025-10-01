#!/usr/bin/env python3
"""
Main Ancient Greek Translator

Streamlined script to translate Ancient Greek texts using GPT-5, Claude 4.1, and Gemini 2.5 Pro.
Automatically processes all texts in the texts/inputs/ folder and outputs to outputs/.

Features:
- Automatic input folder processing
- Three chunking modes: sentence (1 sentence), short (1-2 sentences), or medium (paragraphs)
- All three AI models (GPT-5, Claude 4.1, Gemini 2.5 Pro)
- No artificial limits on translation length
- Comprehensive logging and analytics
- Clean output structure
"""

import os
import json
import time
import re
import argparse
from datetime import datetime
from typing import List, Dict, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('translation_progress.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Import AI libraries
openai = None
anthropic = None
genai = None

try:
    import openai
except ImportError:
    logger.warning("OpenAI library not installed. Run: pip install openai")

try:
    import anthropic
except ImportError:
    logger.warning("Anthropic library not installed. Run: pip install anthropic")

try:
    import google.genai as genai
except ImportError:
    logger.warning("Google GenAI library not installed. Run: pip install google-genai")
    genai = None


class MainTranslator:
    """
    Main translator class for processing Ancient Greek texts with all three AI models.
    """
    
    def __init__(self, chunking_mode: str = 'short'):
        """
        Initialize the translator.
        
        Args:
            chunking_mode: Either 'sentence' (1 sentence), 'short' (1-2 sentences), or 'medium' (paragraphs)
        """
        self.chunking_mode = chunking_mode
        self.models = ['openai', 'claude', 'gemini']
        self.clients = {}
        self.setup_clients()
        
        # Configure chunking based on mode
        if chunking_mode == 'sentence':
            self.chunk_config = {
                'max_sentences': 1,
                'prefer_single': True,
                'description': 'Sentence mode - exactly 1 sentence for maximum precision'
            }
        elif chunking_mode == 'short':
            self.chunk_config = {
                'max_sentences': 2,
                'prefer_single': True,
                'description': 'Short mode - 1-2 sentences for precise translation'
            }
        else:  # medium/paragraph mode
            self.chunk_config = {
                'max_sentences': 8,
                'prefer_single': False, 
                'description': 'Medium mode - full paragraphs for context'
            }
        
        logger.info(f"Initialized translator with {chunking_mode} chunking: {self.chunk_config['description']}")
    
    def setup_clients(self):
        """Set up API clients for all three models."""
        
        # OpenAI setup (GPT-5)
        if openai is not None:
            openai_key = os.getenv('OPENAI_API_KEY')
            if openai_key:
                try:
                    self.clients['openai'] = openai.OpenAI(api_key=openai_key)
                    logger.info("✓ OpenAI client initialized (GPT-5)")
                except Exception as e:
                    logger.error(f"Failed to initialize OpenAI client: {e}")
                    self.models.remove('openai')
            else:
                logger.error("OPENAI_API_KEY environment variable not set")
                self.models.remove('openai')
        else:
            logger.error("OpenAI library not available")
            self.models.remove('openai')
        
        # Claude setup (Claude 4.1)
        if anthropic is not None:
            claude_key = os.getenv('ANTHROPIC_API_KEY')
            if claude_key:
                try:
                    self.clients['claude'] = anthropic.Anthropic(api_key=claude_key)
                    logger.info("✓ Claude client initialized (Claude 4.1)")
                except Exception as e:
                    logger.error(f"Failed to initialize Claude client: {e}")
                    self.models.remove('claude')
            else:
                logger.error("ANTHROPIC_API_KEY environment variable not set")
                self.models.remove('claude')
        else:
            logger.error("Anthropic library not available")
            self.models.remove('claude')
        
        # Gemini setup (Gemini 2.5 Pro)
        if genai is not None:
            gemini_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
            if gemini_key:
                try:
                    self.clients['gemini'] = genai.Client(api_key=gemini_key)
                    logger.info("✓ Gemini client initialized (Gemini 2.5 Pro)")
                except Exception as e:
                    logger.error(f"Failed to initialize Gemini client: {e}")
                    self.models.remove('gemini')
            else:
                logger.error("GOOGLE_API_KEY or GEMINI_API_KEY environment variable not set")
                self.models.remove('gemini')
        else:
            logger.error("Google GenAI library not available")
            self.models.remove('gemini')
        
        if not self.models:
            logger.error("No models available! Please check your API keys and installations.")
            exit(1)
        
        logger.info(f"Active models: {', '.join(self.models)}")
    
    def find_input_files(self, input_dir: str = "texts/inputs") -> List[str]:
        """Find all text files in the input directory."""
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.error(f"Input directory not found: {input_dir}")
            return []
        
        text_files = list(input_path.glob("*.txt"))
        if not text_files:
            logger.warning(f"No .txt files found in {input_dir}")
            return []
        
        file_paths = [str(f) for f in text_files]
        logger.info(f"Found {len(file_paths)} text files: {[f.name for f in text_files]}")
        return file_paths
    
    def parse_text_into_chunks(self, text: str, filename: str) -> List[Dict[str, str]]:
        """
        Parse text into chunks based on the configured chunking mode.
        
        Args:
            text: The text to parse
            filename: Source filename for reference
            
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # First try numbered sections (1., 2., 3., etc.)
        numbered_pattern = r'^(\d+)\.\s+'
        sections = re.split(numbered_pattern, text, flags=re.MULTILINE)
        sections = [s.strip() for s in sections if s.strip()]
        
        if len(sections) > 2:  # Found numbered sections
            logger.info(f"Found numbered sections in {filename}")
            i = 0
            while i < len(sections) - 1:
                if sections[i].isdigit():
                    section_num = sections[i]
                    content = sections[i + 1].strip()
                    content = re.sub(r'\s+', ' ', content)
                    
                    if content:
                        section_chunks = self._chunk_content(content, section_num, filename)
                        chunks.extend(section_chunks)
                    i += 2
                else:
                    i += 1
        else:
            # Fall back to natural paragraph breaks
            logger.info(f"Using paragraph breaks for {filename}")
            paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
            
            for i, para in enumerate(paragraphs, 1):
                para = para.strip()
                if para and len(para) > 20:  # Skip very short fragments
                    para = re.sub(r'\s+', ' ', para)
                    para_chunks = self._chunk_content(para, str(i), filename)
                    chunks.extend(para_chunks)
        
        logger.info(f"Created {len(chunks)} chunks from {filename} using {self.chunking_mode} mode")
        return chunks
    
    def _chunk_content(self, content: str, base_number: str, filename: str) -> List[Dict[str, str]]:
        """Chunk content based on the current chunking mode."""
        
        if self.chunking_mode == 'sentence':
            return self._create_sentence_chunks(content, base_number, filename)
        elif self.chunking_mode == 'short':
            return self._create_short_chunks(content, base_number, filename)
        else:
            return self._create_medium_chunks(content, base_number, filename)
    
    def _create_sentence_chunks(self, content: str, base_number: str, filename: str) -> List[Dict[str, str]]:
        """Create sentence chunks (exactly 1 sentence per chunk)."""
        # Split into sentences using terminal punctuation only
        # Ancient Greek terminal punctuation: . (period), ; (question mark)
        # Note: · (ano teleia/high dot) is medial punctuation, not terminal
        sentence_pattern = r'[.;]\s+'
        sentences = re.split(sentence_pattern, content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
        
        if not sentences:
            # Return original content if can't split into sentences
            return [{
                'id': base_number,
                'content': content,
                'source_file': filename,
                'chunk_type': 'unsplittable',
                'word_count': len(content.split())
            }]
        
        chunks = []
        for i, sentence in enumerate(sentences, 1):
            chunk_id = f"{base_number}.{i}" if i > 1 else base_number
            chunks.append({
                'id': chunk_id,
                'content': sentence.strip(),
                'source_file': filename,
                'chunk_type': 'sentence',
                'word_count': len(sentence.split()),
                'sentence_count': 1
            })
        
        return chunks
    
    def _create_short_chunks(self, content: str, base_number: str, filename: str) -> List[Dict[str, str]]:
        """Create short chunks (1-2 sentences)."""
        # Split into sentences using terminal punctuation only
        # Ancient Greek terminal punctuation: . (period), ; (question mark)
        # Note: · (ano teleia/high dot) is medial punctuation, not terminal
        sentence_pattern = r'[.;]\s+'
        sentences = re.split(sentence_pattern, content)
        sentences = [s.strip() for s in sentences if s.strip() and len(s.split()) >= 3]
        
        if not sentences:
            # Return original content if can't split into sentences
            return [{
                'id': base_number,
                'content': content,
                'source_file': filename,
                'chunk_type': 'unsplittable',
                'word_count': len(content.split())
            }]
        
        chunks = []
        i = 0
        chunk_index = 1
        
        while i < len(sentences):
            current_chunk = sentences[i]
            sentence_count = 1
            
            # Try to add one more sentence if it keeps us reasonable
            if (i + 1 < len(sentences) and 
                sentence_count < self.chunk_config['max_sentences']):
                
                combined = current_chunk + " " + sentences[i + 1]
                # No word limit - just use sentence limit
                current_chunk = combined
                sentence_count = 2
                i += 2
            else:
                i += 1
            
            chunk_id = f"{base_number}.{chunk_index}" if chunk_index > 1 else base_number
            chunks.append({
                'id': chunk_id,
                'content': current_chunk.strip(),
                'source_file': filename,
                'chunk_type': 'short',
                'word_count': len(current_chunk.split()),
                'sentence_count': sentence_count
            })
            chunk_index += 1
        
        return chunks
    
    def _create_medium_chunks(self, content: str, base_number: str, filename: str) -> List[Dict[str, str]]:
        """Create medium chunks (full paragraphs or logical sections)."""
        # For medium chunks, we keep larger sections together for context
        word_count = len(content.split())
        
        # If it's reasonable size, keep as one chunk
        if word_count <= 300:  # Generous limit for context
            return [{
                'id': base_number,
                'content': content,
                'source_file': filename,
                'chunk_type': 'medium',
                'word_count': word_count
            }]
        
        # For very long content, split at natural breaks
        # Look for sentence boundaries using terminal punctuation only
        # Ancient Greek terminal punctuation: . (period), ; (question mark)
        sentences = re.split(r'[.;]\s+', content)
        
        if len(sentences) <= self.chunk_config['max_sentences']:
            # If sentence count is reasonable, keep together
            return [{
                'id': base_number,
                'content': content,
                'source_file': filename,
                'chunk_type': 'medium',
                'word_count': word_count
            }]
        
        # Split into smaller medium chunks
        chunks = []
        current_chunk = ""
        current_sentences = 0
        chunk_index = 1
        
        for sentence in sentences:
            if (current_sentences < self.chunk_config['max_sentences'] and
                len((current_chunk + " " + sentence).split()) <= 300):
                
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
                current_sentences += 1
            else:
                # Save current chunk
                if current_chunk.strip():
                    chunk_id = f"{base_number}.{chunk_index}" if chunk_index > 1 else base_number
                    chunks.append({
                        'id': chunk_id,
                        'content': current_chunk.strip(),
                        'source_file': filename,
                        'chunk_type': 'medium',
                        'word_count': len(current_chunk.split()),
                        'sentence_count': current_sentences
                    })
                    chunk_index += 1
                
                # Start new chunk
                current_chunk = sentence
                current_sentences = 1
        
        # Add final chunk
        if current_chunk.strip():
            chunk_id = f"{base_number}.{chunk_index}" if chunk_index > 1 else base_number
            chunks.append({
                'id': chunk_id,
                'content': current_chunk.strip(),
                'source_file': filename,
                'chunk_type': 'medium',
                'word_count': len(current_chunk.split()),
                'sentence_count': current_sentences
            })
        
        return chunks
    
    def create_translation_prompt(self, text: str, chunk_id: str) -> str:
        """Create a clean, unlimited prompt for translation."""
        return f"""You are an expert translator of Ancient Greek, specializing in classical texts including philosophical, medical, and literary works.

Please translate this Ancient Greek text:

**Text {chunk_id}:**
{text}

Guidelines:
- Provide a clear, accurate English translation
- Maintain the meaning, structure, and style of the original Greek
- Use appropriate terminology for the subject matter
- Preserve the logical flow and argumentation
- Include brief explanatory notes in [brackets] for technical terms if helpful
- Aim for accuracy while ensuring natural English

Translate only the Greek text provided. Do not add commentary beyond the translation itself."""
    
    def translate_with_openai(self, chunk: Dict[str, str]) -> Dict[str, str]:
        """Translate using OpenAI GPT-5 with no artificial limits."""
        prompt = self.create_translation_prompt(chunk['content'], chunk['id'])
        
        try:
            # Use the new Responses API for GPT-5
            response = self.clients['openai'].responses.create(
                model="gpt-5",
                input=prompt,
                reasoning={"effort": "medium"},  # Balanced effort for quality
                text={"verbosity": "medium"},
                max_output_tokens=8000,  # Generous limit to avoid artificial constraints
            )
            
            translation = response.output_text.strip()
            
            if not translation:
                translation = "ERROR: Empty translation returned"
            
            result = chunk.copy()
            result['openai_translation'] = translation
            result['openai_model'] = "gpt-5"
            result['openai_translated_at'] = datetime.now().isoformat()
            result['openai_status'] = 'completed'
            
            return result
            
        except Exception as e:
            logger.error(f"OpenAI error for chunk {chunk['id']}: {e}")
            result = chunk.copy()
            result['openai_translation'] = f"ERROR: {str(e)}"
            result['openai_model'] = "gpt-5"
            result['openai_translated_at'] = datetime.now().isoformat()
            result['openai_status'] = 'error'
            return result
    
    def translate_with_claude(self, chunk: Dict[str, str]) -> Dict[str, str]:
        """Translate using Claude 4.1 with no artificial limits."""
        prompt = self.create_translation_prompt(chunk['content'], chunk['id'])
        
        try:
            response = self.clients['claude'].messages.create(
                model="claude-sonnet-4-5-20250929",  # Latest Claude 4.1 equivalent
                max_tokens=8000,  # Generous limit to avoid artificial constraints
                temperature=0.3,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            translation = response.content[0].text.strip()
            
            if not translation:
                translation = "ERROR: Empty translation returned"
            
            result = chunk.copy()
            result['claude_translation'] = translation
            result['claude_model'] = "claude-sonnet-4-5-20250929"
            result['claude_translated_at'] = datetime.now().isoformat()
            result['claude_status'] = 'completed'
            
            return result
            
        except Exception as e:
            logger.error(f"Claude error for chunk {chunk['id']}: {e}")
            result = chunk.copy()
            result['claude_translation'] = f"ERROR: {str(e)}"
            result['claude_model'] = "claude-sonnet-4-5-20250929"
            result['claude_translated_at'] = datetime.now().isoformat()
            result['claude_status'] = 'error'
            return result
    
    def translate_with_gemini(self, chunk: Dict[str, str]) -> Dict[str, str]:
        """Translate using Gemini 2.5 Pro with no artificial limits."""
        prompt = self.create_translation_prompt(chunk['content'], chunk['id'])
        
        try:
            from google.genai import types
            
            response = self.clients['gemini'].models.generate_content(
                model="gemini-2.5-pro",
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.3,
                    max_output_tokens=8000,  # Generous limit to avoid artificial constraints
                )
            )
            
            if hasattr(response, 'text') and response.text:
                translation = response.text.strip()
            else:
                translation = "ERROR: Unable to extract text from response"
            
            if not translation:
                translation = "ERROR: Empty translation returned"
            
            result = chunk.copy()
            result['gemini_translation'] = translation
            result['gemini_model'] = "gemini-2.5-pro"
            result['gemini_translated_at'] = datetime.now().isoformat()
            result['gemini_status'] = 'completed'
            
            return result
            
        except Exception as e:
            logger.error(f"Gemini error for chunk {chunk['id']}: {e}")
            result = chunk.copy()
            result['gemini_translation'] = f"ERROR: {str(e)}"
            result['gemini_model'] = "gemini-2.5-pro"
            result['gemini_translated_at'] = datetime.now().isoformat()
            result['gemini_status'] = 'error'
            return result
    
    def translate_chunk(self, chunk: Dict[str, str]) -> Dict[str, str]:
        """Translate a single chunk with all available models."""
        logger.info(f"Translating chunk {chunk['id']} ({chunk['word_count']} words)")
        
        result = chunk.copy()
        
        # Translate with all models in parallel
        with ThreadPoolExecutor(max_workers=len(self.models)) as executor:
            futures = {}
            
            for model in self.models:
                if model == 'openai':
                    futures[executor.submit(self.translate_with_openai, chunk)] = 'openai'
                elif model == 'claude':
                    futures[executor.submit(self.translate_with_claude, chunk)] = 'claude'
                elif model == 'gemini':
                    futures[executor.submit(self.translate_with_gemini, chunk)] = 'gemini'
            
            # Collect results
            for future in as_completed(futures):
                model = futures[future]
                try:
                    translation_result = future.result()
                    # Update result with model-specific fields
                    result.update({k: v for k, v in translation_result.items() 
                                 if k.startswith(f'{model}_')})
                except Exception as e:
                    logger.error(f"Parallel translation error for {model}: {e}")
                    result[f'{model}_translation'] = f"ERROR: {str(e)}"
                    result[f'{model}_status'] = 'error'
                    result[f'{model}_translated_at'] = datetime.now().isoformat()
        
        logger.info(f"✓ Completed chunk {chunk['id']}")
        return result
    
    def calculate_analytics(self, results: List[Dict]) -> Dict:
        """Calculate success rates and analytics."""
        analytics = {
            'total_chunks': len(results),
            'total_source_words': sum(r.get('word_count', 0) for r in results),
            'models': {}
        }
        
        for model in self.models:
            completed = sum(1 for r in results if r.get(f'{model}_status') == 'completed')
            errors = sum(1 for r in results if r.get(f'{model}_status') == 'error')
            total_words = sum(len(r.get(f'{model}_translation', '').split()) 
                            for r in results if r.get(f'{model}_status') == 'completed')
            
            analytics['models'][model] = {
                'completed': completed,
                'errors': errors,
                'success_rate': round((completed / len(results)) * 100, 1) if results else 0,
                'total_translation_words': total_words,
                'avg_words_per_chunk': round(total_words / completed, 1) if completed > 0 else 0
            }
        
        return analytics
    
    def translate_file(self, file_path: str) -> Dict:
        """Translate a single file."""
        logger.info(f"🔄 Processing file: {file_path}")
        
        # Read file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return {}
        
        # Parse into chunks
        filename = os.path.basename(file_path)
        chunks = self.parse_text_into_chunks(text, filename)
        
        if not chunks:
            logger.warning(f"No chunks created from {file_path}")
            return {}
        
        # Translate all chunks
        translated_chunks = []
        for chunk in chunks:
            translated = self.translate_chunk(chunk)
            translated_chunks.append(translated)
            time.sleep(0.5)  # Brief delay between chunks
        
        # Calculate analytics
        analytics = self.calculate_analytics(translated_chunks)
        
        # Create results structure
        results = {
            'metadata': {
                'source_file': file_path,
                'processed_at': datetime.now().isoformat(),
                'chunking_mode': self.chunking_mode,
                'models_used': self.models,
                'analytics': analytics
            },
            'chunks': translated_chunks
        }
        
        logger.info(f"✅ Completed {file_path}: {len(translated_chunks)} chunks, "
                   f"{analytics['total_source_words']} source words")
        
        return results
    
    def translate_all_inputs(self, input_dir: str = "texts/inputs", output_dir: str = "outputs") -> List[str]:
        """Translate all files in the input directory."""
        # Find input files
        input_files = self.find_input_files(input_dir)
        if not input_files:
            logger.error("No input files found!")
            return []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        output_files = []
        
        for file_path in input_files:
            # Translate file
            results = self.translate_file(file_path)
            
            if results:
                # Generate output filename
                filename = os.path.splitext(os.path.basename(file_path))[0]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"{filename}_{self.chunking_mode}_{timestamp}.json"
                output_path = os.path.join(output_dir, output_filename)
                
                # Save results
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(results, f, indent=2, ensure_ascii=False)
                    
                    logger.info(f"💾 Saved results: {output_path}")
                    output_files.append(output_path)
                    
                except Exception as e:
                    logger.error(f"Failed to save {output_path}: {e}")
        
        return output_files


def main():
    parser = argparse.ArgumentParser(
        description="Main Ancient Greek Translator - Process texts/inputs/ with all three AI models"
    )
    parser.add_argument(
        '--chunking',
        choices=['sentence', 'short', 'medium'],
        default='short',
        help='Chunking mode: sentence (1 sentence), short (1-2 sentences), or medium (paragraphs)'
    )
    parser.add_argument(
        '--input-dir',
        default='texts/inputs',
        help='Input directory (default: texts/inputs)'
    )
    parser.add_argument(
        '--output-dir',
        default='outputs',
        help='Output directory (default: outputs)'
    )
    parser.add_argument(
        '--list-files',
        action='store_true',
        help='List available input files and exit'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize translator
    translator = MainTranslator(chunking_mode=args.chunking)
    
    if args.list_files:
        files = translator.find_input_files(args.input_dir)
        print(f"\n📁 Found {len(files)} files in {args.input_dir}:")
        for file_path in files:
            print(f"  • {os.path.basename(file_path)}")
        print(f"\nTo translate all files, run without --list-files")
        return 0
    
    # Print startup info
    print(f"\n🏛️  Main Ancient Greek Translator")
    print(f"═══════════════════════════════════")
    print(f"📁 Input: {args.input_dir}")
    print(f"💾 Output: {args.output_dir}")
    print(f"📝 Chunking: {args.chunking}")
    print(f"🤖 Models: GPT-5, Claude 4.1, Gemini 2.5 Pro")
    print(f"")
    
    # Translate all files
    start_time = time.time()
    output_files = translator.translate_all_inputs(args.input_dir, args.output_dir)
    end_time = time.time()
    
    # Summary
    print(f"\n🎉 Translation Complete!")
    print(f"⏱️  Total time: {end_time - start_time:.1f} seconds")
    print(f"📄 Files processed: {len(output_files)}")
    print(f"")
    print(f"📊 Output files:")
    for output_file in output_files:
        print(f"  • {output_file}")
    print(f"")
    print(f"💡 Tips:")
    print(f"  • View results: cat outputs/filename.json | jq")
    print(f"  • Try different chunking: --chunking medium")
    print(f"  • For evaluation, use the short mode for expert ranking")
    
    return 0 if output_files else 1


if __name__ == "__main__":
    exit(main())
