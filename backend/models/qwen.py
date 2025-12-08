"""
Author: Aidan Bell
"""

import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


class QwenModel:
    """
    Encapsulates the Qwen model, tokenizer, and related functionality.
    Handles lazy loading and configuration from backend or scraping contexts.
    """

    def __init__(self):
        self._model = None
        self._tokenizer = None
        self._load_failed = False
        self._warning_printed = False
        self._failure_reason = None

    def _load_model(self) -> tuple[AutoModelForCausalLM | None, AutoTokenizer | None]:
        """
        Lazy load the Qwen model and tokenizer.
        Only loads if CUDA is available.
        Tries to load in 4-bit first, then 8-bit, then full precision.

        Returns:
            tuple: (model, tokenizer) or (None, None) if loading fails
        """
        # Check if CUDA is available
        if not torch.cuda.is_available():
            if not self._load_failed:
                self._load_failed = True
                self._failure_reason = "cuda"
            return None, None

        if self._model is None or self._tokenizer is None:
            try:
                model_name = os.getenv("QWEN_MODEL_NAME", "Qwen/Qwen3-1.7B")

                # Load tokenizer
                self._tokenizer = AutoTokenizer.from_pretrained(model_name)

                # Set pad_token_id if not already set (to avoid attention mask warnings)
                if self._tokenizer.pad_token_id is None:
                    self._tokenizer.pad_token_id = self._tokenizer.eos_token_id

                # Try to load model with quantization (4-bit, then 8-bit, then full precision)
                load_kwargs = {
                    "torch_dtype": "auto",
                    "device_map": "auto",
                }

                # Check if bitsandbytes is available for quantization
                try:
                    import bitsandbytes as bnb

                    # Try 4-bit first
                    try:
                        load_kwargs["load_in_4bit"] = True
                        self._model = AutoModelForCausalLM.from_pretrained(
                            model_name, **load_kwargs
                        )
                        print("[INFO] Qwen model loaded in 4-bit quantization")
                        self._load_failed = False  # Reset on successful load
                    except Exception as e:
                        print(f"[INFO] Failed to load in 4-bit: {e}. Trying 8-bit...")
                        # Try 8-bit
                        load_kwargs.pop("load_in_4bit", None)
                        load_kwargs["load_in_8bit"] = True
                        self._model = AutoModelForCausalLM.from_pretrained(
                            model_name, **load_kwargs
                        )
                        print("[INFO] Qwen model loaded in 8-bit quantization")
                        self._load_failed = False  # Reset on successful load

                except ImportError:
                    # bitsandbytes not available, load in full precision
                    print(
                        "[INFO] bitsandbytes not available. Loading model in full precision."
                    )
                    self._model = AutoModelForCausalLM.from_pretrained(
                        model_name, **load_kwargs
                    )
                    self._load_failed = False  # Reset on successful load

            except Exception as e:
                if not self._load_failed:
                    self._load_failed = True
                    self._failure_reason = "load_error"
                raise RuntimeError(f"Failed to load Qwen model: {str(e)}")

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
        messages: list[dict],
        num_keywords: int = 5,
        max_new_tokens: int = 50,
        **kwargs,
    ) -> list[str]:
        """
        Generate keywords using Qwen with customizable messages.

        Args:
            messages (list[dict]): Messages to send to the model.
                Each message should have 'role' and 'content' keys.
                The 'content' can contain format placeholders (e.g., {text}, {count})
                that will be filled using kwargs.
            num_keywords (int): The number of keywords to return.
            max_new_tokens (int): Maximum number of tokens to generate.
            **kwargs: Keyword arguments used to format the message content strings.
                For example, if a message content contains "{text}", pass text="some value".

        Returns:
            list[str]: A list of keywords generated from the input.

        Examples:
            custom_messages = [
                {"role": "system", "content": "Generate {count} keywords from the text."},
                {"role": "user", "content": "Text: {text}\\nKeywords:"}
            ]
            keywords = model.generate_keywords(
                messages=custom_messages,
                num_keywords=5,
                count=5,
                text="Machine learning and data science..."
            )
        """
        if not messages:
            return []

        # Ensure model is loaded
        model, tokenizer = self._load_model()
        if model is None or tokenizer is None:
            # Only print warning once
            if not self._warning_printed:
                if self._failure_reason == "cuda":
                    print(
                        "[WARNING] CUDA is not available. Qwen model cannot be loaded."
                    )
                else:
                    print(
                        "[WARNING] Qwen model or tokenizer is not loaded. Keywords could not be generated."
                    )
                self._warning_printed = True
            return []

        try:
            for msg in messages:
                # Format the content with provided kwargs
                if kwargs:
                    msg["content"] = msg["content"].format(**kwargs)

            # Apply chat template (thinking mode disabled)
            text = tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=False,
            )

            # Tokenize the text
            model_inputs = tokenizer([text], return_tensors="pt").to(model.device)

            # Generate keywords
            with torch.no_grad():
                generated_ids = model.generate(
                    **model_inputs,
                    eos_token_id=tokenizer.eos_token_id,
                    pad_token_id=tokenizer.pad_token_id,
                    max_new_tokens=max_new_tokens,
                    do_sample=False,
                )

            # Extract only the newly generated tokens (excluding the input prompt)
            input_length = model_inputs.input_ids.shape[-1]
            output_ids = generated_ids[0][input_length:]

            # Decode the generated content
            keywords_text = tokenizer.decode(
                output_ids, skip_special_tokens=True
            ).strip()

            # Parse keywords from the response
            keywords = self._parse_keywords(keywords_text, num_keywords)
            return keywords[:num_keywords]

        except KeyError as e:
            raise ValueError(f"Missing format argument for message template: {e}")
        except Exception as e:
            raise RuntimeError(f"Error generating keywords with Qwen: {str(e)}")

    def generate_faculty_keywords(
        self, biography: str, num_keywords: int = 5, biography_length_limit: int = 2000
    ) -> list[str]:
        """
        Generate keywords for a faculty member's biography using Qwen.

        Args:
            biography (str): The biography of the faculty member.
            num_keywords (int): The number of keywords to generate.
            biography_length_limit (int): The maximum length of the biography to use.

        Returns:
            list[str]: A list of keywords generated from the biography.
        """
        if not biography or not biography.strip():
            return []

        biography = biography[:biography_length_limit]

        messages = [
            {
                "role": "system",
                "content": (
                    f"You generate exactly {num_keywords} research keywords about a faculty member. "
                    "Output MUST be only the keywords separated by commas. "
                    "No explanations, no extra text, no quotes, no numbering."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Biography:\n"
                    "Professor Alice Zhang studies machine learning fairness, "
                    "algorithmic transparency, neural network interpretability, and "
                    "applied ethics in AI systems."
                ),
            },
            {
                "role": "assistant",
                "content": (
                    "machine learning fairness, algorithmic transparency, neural network interpretability, "
                    "applied AI ethics, explainable AI"
                ),
            },
            {
                "role": "user",
                "content": f"Biography:\n{biography}",
            },
        ]

        return self.generate_keywords(messages=messages, num_keywords=num_keywords)

    def generate_publication_keywords(
        self, abstract: str, num_keywords: int = 5, abstract_length_limit: int = 2000
    ) -> list[str]:
        """
        Generate keywords for a publication using Qwen.

        Args:
            abstract (str): The abstract of the publication.
            num_keywords (int): The number of keywords to generate.
            abstract_length_limit (int): The maximum length of the abstract to use.

        Returns:
            list[str]: A list of keywords generated from the publication.
        """
        if not abstract or not abstract.strip():
            return []

        abstract = abstract[:abstract_length_limit]

        messages = [
            {
                "role": "system",
                "content": (
                    f"You generate exactly {num_keywords} research keywords about a publication, based on the abstract. "
                    "Output MUST be only the keywords separated by commas. "
                    "No explanations, no extra text, no quotes, no numbering."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Abstract:\n"
                    "Multimodal Large Language Models (MLLMs) connect and interpret different data types, "
                    "making them suitable for various vision-language tasks. Despite the rapid advancements in MLLMs, "
                    "their effectiveness for specialized cross-modal retrieval tasks remains underexplored. A challenging "
                    "example is art retrieval, where the task is to find visually and conceptually relevant artwork corresponding to a textual description. "
                    "This paper investigates the effects of fine-tuning cross-modal retrieval models using both human-annotated and MLLM-generated captions for "
                    "artistic paintings. To this end, two cross-modal retrieval models, Long-CLIP and BLIP, are studied. Experimental results show that models "
                    "fine-tuned on MLLM-generated captions achieve search effectiveness comparable to those fine-tuned on human-annotated captions."
                ),
            },
            {
                "role": "assistant",
                "content": "artwork retrieval, image captioning, multimodal llms, cross-modal retrieval, fine-tuning",
            },
            {
                "role": "user",
                "content": f"Abstract:\n{abstract}",
            },
        ]

        return self.generate_keywords(messages=messages, num_keywords=num_keywords)

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

            if (
                keyword and len(keyword) > 1
            ):  # Ignore empty or single character keywords
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
_model_instance = QwenModel()


# Public API functions that delegate to the module-level instance
def generate_keywords_with_qwen(
    messages: list[dict], num_keywords: int = 5, max_new_tokens: int = 50, **kwargs
) -> list[str]:
    """
    Generate keywords using Qwen with customizable messages.

    This is a convenience function that delegates to the module-level QwenModel instance.

    Args:
        messages (list[dict]): Messages to send to the model.
            Each message should have 'role' and 'content' keys.
            The 'content' can contain format placeholders (e.g., {text}, {count})
            that will be filled using kwargs.
        num_keywords (int): The number of keywords to return.
        max_new_tokens (int): Maximum number of tokens to generate.
        **kwargs: Keyword arguments used to format the message content strings.

    Returns:
        list[str]: A list of keywords generated from the input.

    Examples:
        custom_messages = [
            {"role": "system", "content": "Generate {count} keywords from the text."},
            {"role": "user", "content": "Text: {text}\\nKeywords:"}
        ]
        keywords = generate_keywords_with_qwen(
            messages=custom_messages,
            num_keywords=5,
            count=5,
            text="Machine learning and data science..."
        )
    """
    return _model_instance.generate_keywords(
        messages=messages,
        num_keywords=num_keywords,
        max_new_tokens=max_new_tokens,
        **kwargs,
    )


def generate_faculty_keywords_with_qwen(
    biography: str, num_keywords: int = 5, biography_length_limit: int = 2000
) -> list[str]:
    """
    Generate keywords for a faculty member's biography using Qwen.

    This is a convenience function that delegates to the module-level QwenModel instance.

    Args:
        biography (str): The biography of the faculty member.
        num_keywords (int): The number of keywords to generate.
        biography_length_limit (int): The maximum length of the biography to use.

    Returns:
        list[str]: A list of keywords generated from the biography.
    """
    return _model_instance.generate_faculty_keywords(
        biography=biography,
        num_keywords=num_keywords,
        biography_length_limit=biography_length_limit,
    )


def generate_publication_keywords_with_qwen(
    abstract: str, num_keywords: int = 5, abstract_length_limit: int = 2000
) -> list[str]:
    """
    Generate keywords for a publication using Qwen.

    This is a convenience function that delegates to the module-level QwenModel instance.

    Args:
        abstract (str): The abstract of the publication.
        num_keywords (int): The number of keywords to generate.
        abstract_length_limit (int): The maximum length of the abstract to use.

    Returns:
        list[str]: A list of keywords generated from the publication.
    """
    return _model_instance.generate_publication_keywords(
        abstract=abstract,
        num_keywords=num_keywords,
        abstract_length_limit=abstract_length_limit,
    )


def unload_qwen_model():
    """
    Unload the model and tokenizer from memory.

    This is a convenience function that delegates to the module-level QwenModel instance.

    This function deletes the model and tokenizer objects, clears PyTorch cache,
    and resets the instance variables to None. This should be called after
    keyword generation is complete to free up memory.
    """
    _model_instance.unload()
