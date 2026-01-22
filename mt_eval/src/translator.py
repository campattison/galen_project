#!/usr/bin/env python3
"""
Translation Module

Translates Ancient Greek text using three AI models:
- OpenAI (GPT-5)
- Anthropic (Claude 4.5)
- Google (Gemini 2.5 Pro)
"""

import os
import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import hashlib

# Load environment variables
try:
    from dotenv import load_dotenv
    # Try project root first (two levels up from src/)
    import os
    root_env = os.path.join(os.path.dirname(__file__), '..', '..', '.env')
    if os.path.exists(root_env):
        load_dotenv(root_env)
    # Fall back to config/.env
    elif os.path.exists(os.path.join(os.path.dirname(__file__), '..', 'config', '.env')):
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', 'config', '.env'))
except ImportError:
    pass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Translation:
    """A translation result from a single model."""
    chunk_id: str
    model_name: str
    translation: str
    raw_response: str  # Full response
    timestamp: str
    status: str  # 'success' or 'error'
    error_message: Optional[str] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Translator:
    """Translate Ancient Greek using multiple AI models."""
    
    def __init__(self, models: List[str] = None):
        """
        Initialize translator with API clients.
        
        Args:
            models: List of models to use ['openai', 'claude', 'gemini']
                   If None, uses all available models
        """
        if models is None:
            models = ['openai', 'claude', 'gemini']
        
        self.models = models
        self.clients = {}
        self._setup_clients()
        # Enable extra diagnostics via env flag
        self.debug_diagnostics = os.getenv('GALEN_DIAGNOSTICS', '0') in ('1', 'true', 'True')

    def _hash_text(self, text: str, prefix_len: int = 16) -> str:
        """Return a short, stable hash of text for privacy-safe correlation in logs."""
        try:
            digest = hashlib.sha256(text.encode('utf-8')).hexdigest()
            return digest[:prefix_len]
        except Exception:
            return ""
    
    def _setup_clients(self):
        """Set up API clients for requested models."""
        
        # OpenAI
        if 'openai' in self.models:
            try:
                import openai
                api_key = os.getenv('OPENAI_API_KEY')
                if api_key and api_key != 'your_openai_api_key_here':
                    self.clients['openai'] = openai.OpenAI(api_key=api_key)
                    logger.info("✓ OpenAI client initialized (GPT-5)")
                else:
                    logger.warning("OpenAI API key not configured")
                    self.models.remove('openai')
            except ImportError:
                logger.warning("OpenAI library not installed")
                self.models.remove('openai')
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI: {e}")
                self.models.remove('openai')
        
        # Claude
        if 'claude' in self.models:
            try:
                import anthropic
                api_key = os.getenv('ANTHROPIC_API_KEY')
                if api_key and api_key != 'your_anthropic_api_key_here':
                    self.clients['claude'] = anthropic.Anthropic(api_key=api_key)
                    logger.info("✓ Claude client initialized (Claude 4.5)")
                else:
                    logger.warning("Anthropic API key not configured")
                    self.models.remove('claude')
            except ImportError:
                logger.warning("Anthropic library not installed")
                self.models.remove('claude')
            except Exception as e:
                logger.warning(f"Failed to initialize Claude: {e}")
                self.models.remove('claude')
        
        # Gemini
        if 'gemini' in self.models:
            try:
                import google.genai as genai
                api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('GEMINI_API_KEY')
                if api_key and api_key != 'your_google_api_key_here':
                    self.clients['gemini'] = genai.Client(api_key=api_key)
                    logger.info("✓ Gemini client initialized (Gemini 2.5 Pro)")
                else:
                    logger.warning("Google/Gemini API key not configured")
                    self.models.remove('gemini')
            except ImportError:
                logger.warning("Google GenAI library not installed")
                self.models.remove('gemini')
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini: {e}")
                self.models.remove('gemini')
        
        if not self.models:
            logger.error("No models available! Check API keys and installations.")
            raise RuntimeError("No translation models available")
        
        logger.info(f"Active models: {', '.join(self.models)}")
    
    def extract_translation(self, raw_response: str) -> str:
        """
        Return model output cleaned of label prefixes like 'Translation:'.
        We do NOT attempt to split or truncate; this avoids accidental clipping.
        """
        if not raw_response:
            return ''
        text = raw_response.strip()
        # Remove common leading labels and markdown wrappers
        import re
        # Strip leading markdown bold label '**Translation:**' or plain 'Translation:' variants
        text = re.sub(r'^(\*\*\s*)?translation\s*:\s*(\*\*)?\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^(english\s+translation|rendering)\s*:\s*', '', text, flags=re.IGNORECASE)
        # Remove surrounding triple backticks if the whole output is fenced
        fenced = re.match(r'^```[a-zA-Z]*\n([\s\S]*?)\n```\s*$', text)
        if fenced:
            text = fenced.group(1).strip()
        return text
    
    def _create_prompt(self, text: str) -> str:
        """Create specialized prompt for Ancient Greek translation."""
        return f"""You are a Classical philologist specializing in Ancient Greek. Translate the following Ancient Greek text to English.

Context: This is ancient Greek text. Please:
- Preserve technical terminology and scholarly precision
- Maintain the academic tone of the original
- Provide clear, readable English while respecting the ancient context
- Pay attention to classical Greek grammar and syntax

Provide only the English translation, no explanations.

Ancient Greek text:
{text}"""
    
    def translate_openai(self, greek_text: str, chunk_id: str) -> Translation:
        """Translate using OpenAI GPT-5 with the new Responses API."""
        prompt = self._create_prompt(greek_text)
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                start_time = time.time()
                prompt_chars = len(prompt)
                greek_chars = len(greek_text)
                prompt_hash = self._hash_text(prompt)
                if logger.isEnabledFor(logging.DEBUG) or self.debug_diagnostics:
                    logger.debug(
                        f"OpenAI request start | chunk={chunk_id} attempt={attempt + 1}/{max_retries} "
                        f"prompt_chars={prompt_chars} greek_chars={greek_chars} prompt_hash={prompt_hash}"
                    )
                # Use the new Responses API for GPT-5
                response = self.clients['openai'].responses.create(
                    model="gpt-5-2025-08-07",
                    input=prompt,
                    reasoning={"effort": "high"},  
                    text={"verbosity": "medium"},
                    max_output_tokens=16000,  # Increased to avoid truncation
                )
                
                duration_ms = int((time.time() - start_time) * 1000)
                # Extract fields safely; SDKs can change shapes
                response_id = getattr(response, 'id', None)
                usage = getattr(response, 'usage', None)
                input_tokens = getattr(usage, 'input_tokens', None) if usage else None
                output_tokens = getattr(usage, 'output_tokens', None) if usage else None
                
                # Try multiple ways to extract the response text
                raw_response = ''
                if hasattr(response, 'output_text') and response.output_text:
                    raw_response = response.output_text.strip()
                elif hasattr(response, 'output') and hasattr(response.output, 'text'):
                    raw_response = response.output.text.strip()
                elif hasattr(response, 'text') and response.text:
                    raw_response = response.text.strip()
                elif hasattr(response, 'output'):
                    # Try to extract text from output object
                    output = response.output
                    if hasattr(output, 'content') and output.content:
                        raw_response = output.content.strip()
                    elif isinstance(output, str):
                        raw_response = output.strip()
                
                if not raw_response:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Empty response from OpenAI | chunk={chunk_id} attempt={attempt + 1} "
                            f"resp_id={response_id} duration_ms={duration_ms} input_tok={input_tokens} output_tok={output_tokens}"
                        )
                        # brief preview of response structure when empty_text but response exists
                        if (logger.isEnabledFor(logging.DEBUG) or self.debug_diagnostics) and hasattr(response, 'output'):  # type: ignore[attr-defined]
                            try:
                                preview = str(getattr(response, 'output'))[:200]
                                logger.debug(f"OpenAI empty-text output preview | chunk={chunk_id} {preview}")
                            except Exception:
                                pass
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raw_response = "ERROR: Empty response returned after retries"
                        translation = raw_response
                else:
                    translation = self.extract_translation(raw_response)
                    # If translation is too short, might be truncated
                    if len(translation) < 100 and not translation.startswith('ERROR:'):
                        if attempt < max_retries - 1:
                            logger.warning(
                                f"Short translation from OpenAI | chunk={chunk_id} attempt={attempt + 1} "
                                f"resp_id={response_id} duration_ms={duration_ms} out_chars={len(raw_response)}"
                            )
                            time.sleep(2 ** attempt)
                            continue
                # Successful (or terminal) attempt logging
                if logger.isEnabledFor(logging.DEBUG) or self.debug_diagnostics:
                    logger.debug(
                        f"OpenAI response | chunk={chunk_id} attempt={attempt + 1} resp_id={response_id} "
                        f"duration_ms={duration_ms} out_chars={len(raw_response)} input_tok={input_tokens} output_tok={output_tokens}"
                    )
                
                return Translation(
                    chunk_id=chunk_id,
                    model_name='openai',
                    translation=translation,
                    raw_response=raw_response,
                    timestamp=datetime.now().isoformat(),
                    status='success',
                    metadata={
                        'model': 'gpt-5',
                        'reasoning_effort': 'high',
                        'attempt': attempt + 1,
                        'response_id': response_id,
                        'duration_ms': duration_ms,
                        'input_tokens': input_tokens,
                        'output_tokens': output_tokens,
                        'prompt_chars': prompt_chars,
                        'prompt_hash': prompt_hash
                    }
                )
                
            except Exception as e:
                duration_ms = int((time.time() - start_time) * 1000) if 'start_time' in locals() else None
                err_type = type(e).__name__
                if attempt < max_retries - 1:
                    logger.warning(
                        f"OpenAI API error | chunk={chunk_id} attempt={attempt + 1} err_type={err_type} "
                        f"duration_ms={duration_ms} msg={e}"
                    )
                    time.sleep(2 ** attempt)  # Exponential backoff
                    continue
                else:
                    logger.error(
                        f"OpenAI translation failed | chunk={chunk_id} after={max_retries} err_type={err_type} "
                        f"duration_ms={duration_ms} msg={e}"
                    )
                    return Translation(
                        chunk_id=chunk_id,
                        model_name='openai',
                        translation='',
                        raw_response='',
                        timestamp=datetime.now().isoformat(),
                        status='error',
                        error_message=f"Failed after {max_retries} attempts: {str(e)}",
                        metadata={
                            'model': 'gpt-5',
                            'attempt': attempt + 1,
                            'duration_ms': duration_ms,
                            'error_type': err_type,
                            'prompt_chars': len(prompt),
                            'prompt_hash': self._hash_text(prompt)
                        }
                    )
    
    def translate_claude(self, greek_text: str, chunk_id: str) -> Translation:
        """Translate using Claude 4.5 with retry logic for overloads and rate limits."""
        prompt = self._create_prompt(greek_text)

        max_retries = 5
        base_delay = 2

        for attempt in range(max_retries):
            try:
                response = self.clients['claude'].messages.create(
                    model="claude-sonnet-4-5-20250929",  # Latest Claude 4.5
                    max_tokens=8000,  # Generous limit to avoid artificial constraints
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )

                raw_response = response.content[0].text.strip()

                if not raw_response:
                    raw_response = "ERROR: Empty response returned"
                    translation = raw_response
                else:
                    translation = self.extract_translation(raw_response)

                return Translation(
                    chunk_id=chunk_id,
                    model_name='claude',
                    translation=translation,
                    raw_response=raw_response,
                    timestamp=datetime.now().isoformat(),
                    status='success' if not raw_response.startswith('ERROR:') else 'error',
                    metadata={
                        'model': 'claude-sonnet-4-5-20250929',
                        'attempt': attempt + 1,
                        'tokens': response.usage.input_tokens + response.usage.output_tokens if hasattr(response, 'usage') else None
                    }
                )

            except Exception as e:
                msg = str(e)
                lower = msg.lower()
                retryable = any(s in lower for s in ['overloaded', 'rate', 'timeout', 'temporarily unavailable', '503', '429'])
                if retryable and attempt < max_retries - 1:
                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Claude API error (retryable) | chunk={chunk_id} attempt={attempt + 1}/{max_retries} msg={msg}. Retrying after {delay}s"
                    )
                    time.sleep(delay)
                    continue
                logger.error(f"Claude translation failed for chunk {chunk_id} after {attempt + 1} attempts: {msg}")
                return Translation(
                    chunk_id=chunk_id,
                    model_name='claude',
                    translation='',
                    raw_response='',
                    timestamp=datetime.now().isoformat(),
                    status='error',
                    error_message=f"{msg}. {'Not retryable' if not retryable else f'Failed after {attempt + 1} attempts'}",
                    metadata={
                        'model': 'claude-sonnet-4-5-20250929',
                        'attempt': attempt + 1
                    }
                )
    
    def translate_gemini(self, greek_text: str, chunk_id: str) -> Translation:
        """Translate using Gemini 2.5 Pro with retry logic."""
        prompt = self._create_prompt(greek_text)
        
        max_retries = 5  # More retries for 503 errors
        base_delay = 3  # Start with longer delay
        
        # Add initial delay to help with rate limiting
        time.sleep(1.0)
        
        for attempt in range(max_retries):
            try:
                from google.genai import types
                
                # Add delay before request to avoid rate limiting
                if attempt > 0:
                    delay = base_delay * (2 ** attempt)  # Exponential backoff
                    logger.info(f"Retrying Gemini after {delay}s delay (attempt {attempt + 1}/{max_retries})")
                    time.sleep(delay)
                
                response = self.clients['gemini'].models.generate_content(
                    model="gemini-2.5-pro",  # Latest Gemini 2.5 Pro June 17, 2025 release
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0.3,
                        max_output_tokens=16000  # Increased to match OpenAI
                    )
                )
                
                if hasattr(response, 'text') and response.text:
                    raw_response = response.text.strip()
                else:
                    raw_response = "ERROR: Unable to extract text from response"
                    logger.warning(f"Empty response from Gemini for chunk {chunk_id}")
                
                if not raw_response:
                    raw_response = "ERROR: Empty response returned"
                    translation = raw_response
                else:
                    translation = self.extract_translation(raw_response)
                
                return Translation(
                    chunk_id=chunk_id,
                    model_name='gemini',
                    translation=translation,
                    raw_response=raw_response,
                    timestamp=datetime.now().isoformat(),
                    status='success' if raw_response and not raw_response.startswith('ERROR:') else 'error',
                    metadata={
                        'model': 'gemini-2.5-pro',
                        'attempt': attempt + 1
                    }
                )
                
            except Exception as e:
                error_str = str(e)
                # Check if it's a 503 or rate limit error
                is_retryable = '503' in error_str or 'overloaded' in error_str.lower() or 'rate' in error_str.lower()
                
                if is_retryable and attempt < max_retries - 1:
                    logger.warning(f"Gemini API error (retryable) for chunk {chunk_id} (attempt {attempt + 1}/{max_retries}): {error_str}")
                    # Will retry with exponential backoff
                    continue
                else:
                    logger.error(f"Gemini translation failed for chunk {chunk_id} after {attempt + 1} attempts: {e}")
                    return Translation(
                        chunk_id=chunk_id,
                        model_name='gemini',
                        translation='',
                        raw_response='',
                        timestamp=datetime.now().isoformat(),
                        status='error',
                        error_message=f"{error_str}. {'Not retryable' if not is_retryable else f'Failed after {attempt + 1} attempts'}",
                        metadata={
                            'model': 'gemini-2.5-pro',
                            'attempt': attempt + 1
                        }
                    )
    
    def translate_chunk(self, greek_text: str, chunk_id: str, parallel: bool = True) -> Dict[str, Translation]:
        """
        Translate a single chunk with all models.
        
        Args:
            greek_text: The Greek text to translate
            chunk_id: Identifier for this chunk
            parallel: Whether to run translations in parallel (faster but more API load)
            
        Returns:
            Dict mapping model names to Translation objects
        """
        logger.info(f"Translating chunk {chunk_id} with {len(self.models)} models...")
        
        results = {}
        
        if parallel and len(self.models) > 1:
            # Parallel translation
            with ThreadPoolExecutor(max_workers=len(self.models)) as executor:
                futures = {}
                
                for model in self.models:
                    if model == 'openai':
                        future = executor.submit(self.translate_openai, greek_text, chunk_id)
                    elif model == 'claude':
                        future = executor.submit(self.translate_claude, greek_text, chunk_id)
                    elif model == 'gemini':
                        future = executor.submit(self.translate_gemini, greek_text, chunk_id)
                    else:
                        continue
                    
                    futures[future] = model
                
                for future in as_completed(futures):
                    model = futures[future]
                    try:
                        translation = future.result()
                        results[model] = translation
                        status_emoji = "✓" if translation.status == 'success' else "✗"
                        logger.info(f"  {status_emoji} {model}: {translation.status}")
                    except Exception as e:
                        logger.error(f"  ✗ {model}: {e}")
        else:
            # Sequential translation
            for model in self.models:
                if model == 'openai':
                    translation = self.translate_openai(greek_text, chunk_id)
                elif model == 'claude':
                    translation = self.translate_claude(greek_text, chunk_id)
                elif model == 'gemini':
                    translation = self.translate_gemini(greek_text, chunk_id)
                else:
                    continue
                
                results[model] = translation
                status_emoji = "✓" if translation.status == 'success' else "✗"
                logger.info(f"  {status_emoji} {model}: {translation.status}")
                
                # Brief delay between models to avoid rate limits
                if model != self.models[-1]:
                    time.sleep(1)
        
        return results
    
    def translate_chunks(self, chunks: List[Dict], parallel: bool = False) -> Dict[str, Dict[str, Translation]]:
        """
        Translate multiple chunks.
        
        Args:
            chunks: List of chunks with 'chunk_id' and 'greek_text' keys
            parallel: Whether to run model translations in parallel
            
        Returns:
            Dict mapping chunk_id to dict of model translations
        """
        all_results = {}
        
        for i, chunk in enumerate(chunks, 1):
            chunk_id = chunk.get('chunk_id', str(i))
            greek_text = chunk.get('greek_text', '')
            
            if not greek_text:
                logger.warning(f"Chunk {chunk_id} has no Greek text, skipping")
                continue
            
            results = self.translate_chunk(greek_text, chunk_id, parallel=parallel)
            all_results[chunk_id] = results
            
            # Delay between chunks to avoid rate limiting
            if i < len(chunks):
                time.sleep(5.0)  # Longer delay to avoid 503 errors
        
        return all_results
    
    def save_translations(self, translations: Dict[str, Dict[str, Translation]], output_file: str):
        """Save translations to JSON file."""
        import json
        
        # Convert to serializable format
        output_data = {}
        for chunk_id, model_translations in translations.items():
            output_data[chunk_id] = {}
            for model, translation in model_translations.items():
                output_data[chunk_id][model] = {
                    'translation': translation.translation,
                    'raw_response': translation.raw_response,
                    'status': translation.status,
                    'timestamp': translation.timestamp,
                    'error_message': translation.error_message,
                    'metadata': translation.metadata
                }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Translations saved to {output_file}")


def main():
    """Command-line interface for translator."""
    import argparse
    import json
    from parser import InputParser
    
    parser = argparse.ArgumentParser(description="Translate Ancient Greek texts")
    parser.add_argument('input_file', help='Input file (parsed chunks JSON or raw text)')
    parser.add_argument('-o', '--output', help='Output file for translations')
    parser.add_argument('--models', nargs='+', choices=['openai', 'claude', 'gemini'],
                       default=['openai', 'claude', 'gemini'], help='Models to use')
    parser.add_argument('--parallel', action='store_true', help='Run models in parallel (faster)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Parse input file
    input_parser = InputParser()
    parsed_chunks = input_parser.parse_file(args.input_file)
    
    if not parsed_chunks:
        logger.error("No chunks to translate!")
        return 1
    
    # Convert to format expected by translator
    chunks = [
        {'chunk_id': chunk.chunk_id, 'greek_text': chunk.greek_text}
        for chunk in parsed_chunks
    ]
    
    # Translate
    translator = Translator(models=args.models)
    translations = translator.translate_chunks(chunks, parallel=args.parallel)
    
    # Save
    if args.output:
        output_file = args.output
    else:
        output_file = 'output/translations/translations.json'
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    translator.save_translations(translations, output_file)
    
    # Summary
    total_chunks = len(translations)
    successful = sum(
        1 for chunk_translations in translations.values()
        for translation in chunk_translations.values()
        if translation.status == 'success'
    )
    total_attempts = sum(len(chunk_translations) for chunk_translations in translations.values())
    
    print(f"\n✓ Translation complete!")
    print(f"  Chunks: {total_chunks}")
    print(f"  Success rate: {successful}/{total_attempts} ({100*successful/total_attempts:.1f}%)")
    print(f"  Output: {output_file}")
    
    return 0


if __name__ == "__main__":
    exit(main())
