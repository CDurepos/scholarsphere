"""
Author: Aidan Bell
"""

import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class LlamaModel:
    """
    Encapsulates the Llama model, tokenizer, and related functionality.
    Handles lazy loading and configuration from backend or scraping contexts.
    """
    
    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._access_token = None
        self._load_failed = False
        self._warning_printed = False
        self._failure_reason = None
    
    def _get_access_token(self) -> str | None:
        """
        Get the Llama access token from the backend config if available,
        otherwise try scraping config, otherwise return None.
        """
        if self._access_token is not None:
            return self._access_token
        
        # Try to import backend config (only works when imported from backend context)
        try:
            from backend.app.config import Config
            self._access_token = Config.LLAMA_ACCESS_TOKEN
            return self._access_token
        except (ImportError, AttributeError):
            pass
        
        # Try to import scrape config (only works when imported from scraping context)
        try:
            from scraping.scrape_config import ScrapeConfig
            self._access_token = ScrapeConfig.LLAMA_ACCESS_TOKEN
            return self._access_token
        except (ImportError, AttributeError):
            pass
        
        # Don't print here - let generate_keywords handle the warning once
        return None
    
    def _load_model(self) -> tuple[AutoModelForCausalLM | None, AutoTokenizer | None]:
        """
        Lazy load the Llama model and tokenizer.
        Only loads if CUDA is available.
        
        Returns:
            tuple: (model, tokenizer) or (None, None) if loading fails
        """
        # Check if CUDA is available
        if not torch.cuda.is_available():
            if not self._load_failed:
                self._load_failed = True
                self._failure_reason = "cuda"
            return None, None
        
        access_token = self._get_access_token()
        if access_token is None:
            if not self._load_failed:
                self._load_failed = True
                self._failure_reason = "access_token"
            return None, None
        
        if self._model is None or self._tokenizer is None:
            try:
                model_name = os.getenv(
                    "LLAMA_MODEL_NAME", "meta-llama/Meta-Llama-3.1-8B-Instruct"
                )
                self._tokenizer = AutoTokenizer.from_pretrained(
                    model_name, token=access_token
                )
                # Set pad_token_id if not already set (to avoid attention mask warnings)
                if self._tokenizer.pad_token_id is None:
                    self._tokenizer.pad_token_id = self._tokenizer.eos_token_id
                
                self._model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    device_map="auto",
                    token=access_token,
                    load_in_4bit=True
                )
                self._load_failed = False  # Reset on successful load
            except Exception as e:
                if not self._load_failed:
                    self._load_failed = True
                raise RuntimeError(f"Failed to load Llama model: {str(e)}")
        
        return self._model, self._tokenizer
    
    def unload(self):
        """
        Unload the model and tokenizer from memory.
        
        This method deletes the model and tokenizer objects, clears PyTorch cache,
        and resets the instance variables to None. This should be called after
        keyword generation is complete to free up memory.
        """
        if self._model is not None:
            del self._model
            self._model = None
        
        if self._tokenizer is not None:
            del self._tokenizer
            self._tokenizer = None
        
        # Clear PyTorch cache if CUDA is available
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        
        # Force garbage collection
        import gc
        gc.collect()
    
    def generate_keywords(
        self,
        biography: str,
        num_keywords: int = 5,
        biography_length_limit: int = 2000
    ) -> list[str]:
        """
        Generate keywords for a faculty member's biography using llama.
        
        Args:
            biography (str): The biography of the faculty member.
            num_keywords (int): The number of keywords to generate.
            biography_length_limit (int): The maximum length of the biography to use for keyword generation.
        
        Returns:
            list[str]: A list of keywords generated from the biography.
        """
        if not biography or not biography.strip():
            return []
        
        # Ensure model is loaded
        model, tokenizer = self._load_model()
        if model is None or tokenizer is None:
            # Only print warning once
            if not self._warning_printed:
                if self._failure_reason == "cuda":
                    print("[WARNING] CUDA is not available. Llama model cannot be loaded.")
                elif self._failure_reason == "access_token":
                    print("[WARNING] LLAMA_ACCESS_TOKEN is not set. Llama model cannot be loaded.")
                else:
                    print("[WARNING] Llama model or tokenizer is not loaded. Keywords could not be generated.")
                self._warning_printed = True
            return []
        
        biography = biography[:biography_length_limit]
        
        try:
            # Prepare messages
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that generates only research keywords "
                        "separated by commas and no extra text based on a faculty member's biography."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Based on the following biography, generate exactly {num_keywords} research keywords "
                        f"that best describe this faculty member's work and expertise. "
                        f"Return only the keywords, separated by commas.\n\nBiography:\n{biography}\n\nKeywords:"
                    ),
                },
            ]
            
            # Generate input IDs
            input_ids = tokenizer.apply_chat_template(
                messages, add_generation_prompt=True, return_tensors="pt"
            ).to(model.device)
            
            # Create attention mask (all ones since we're not padding)
            attention_mask = torch.ones_like(input_ids)
            
            # Generate keywords
            with torch.no_grad():
                outputs = model.generate(
                    input_ids,
                    attention_mask=attention_mask,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    max_new_tokens=50,
                    do_sample=False,
                )
            
            # Decode only the newly generated tokens (excluding the input prompt)
            response = outputs[0][input_ids.shape[-1]:]
            keywords_text = tokenizer.decode(response, skip_special_tokens=True).strip()
            
            # Parse keywords from the response
            keywords = self._parse_keywords(keywords_text, num_keywords)
            return keywords[:num_keywords]
        
        except Exception as e:
            raise RuntimeError(f"Error generating keywords with Llama: {str(e)}")
    
    @staticmethod
    def _parse_keywords(text: str, expected_count: int) -> list[str]:
        """
        Parse keywords from the generated text.
        
        Args:
            text: The generated text containing keywords.
            expected_count: The expected number of keywords.
        
        Returns:
            A list of cleaned keywords.
        """
        # Remove common prefixes/suffixes that models might add
        text = text.strip()
        
        # Remove quotes if the entire response is quoted
        if text.startswith('"') and text.endswith('"'):
            text = text[1:-1]
        if text.startswith("'") and text.endswith("'"):
            text = text[1:-1]
        
        # Split by common delimiters
        keywords = re.split(r"[,;|\n]", text)
        
        # Clean each keyword
        cleaned_keywords = []
        for keyword in keywords:
            keyword = keyword.strip()
            # Remove quotes, periods, and other punctuation at the end
            keyword = re.sub(r'^["\']|["\']$', "", keyword)
            keyword = keyword.rstrip(".,;!?")
            
            if keyword and len(keyword) > 1:  # Ignore empty or single character keywords
                cleaned_keywords.append(keyword)
        
        # If we got fewer keywords than expected, try to split by spaces as well
        if len(cleaned_keywords) < expected_count and " " in text:
            # Try splitting the original text by spaces and taking meaningful words
            words = text.split()
            for word in words:
                word = word.strip(".,;!?\"'")
                if len(word) > 3 and word.lower() not in [
                    "the",
                    "and",
                    "for",
                    "with",
                    "from",
                ]:
                    if word not in cleaned_keywords:
                        cleaned_keywords.append(word)
                        if len(cleaned_keywords) >= expected_count:
                            break
        
        return cleaned_keywords


# Module-level instance for backward compatibility
_model_instance = LlamaModel()


# Public API functions that delegate to the module-level instance
def generate_keywords_with_llama(
    biography: str,
    num_keywords: int = 5,
    biography_length_limit: int = 2000
) -> list[str]:
    """
    Generate keywords for a faculty member's biography using llama.
    
    This is a convenience function that delegates to the module-level LlamaModel instance.
    
    Args:
        biography (str): The biography of the faculty member.
        num_keywords (int): The number of keywords to generate.
        biography_length_limit (int): The maximum length of the biography to use for keyword generation.
    
    Returns:
        list[str]: A list of keywords generated from the biography.
    """
    return _model_instance.generate_keywords(biography, num_keywords, biography_length_limit)


def unload_model():
    """
    Unload the model and tokenizer from memory.
    
    This is a convenience function that delegates to the module-level LlamaModel instance.
    
    This function deletes the model and tokenizer objects, clears PyTorch cache,
    and resets the instance variables to None. This should be called after
    keyword generation is complete to free up memory.
    """
    _model_instance.unload()
