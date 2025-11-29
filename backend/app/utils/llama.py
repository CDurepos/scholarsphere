import os
import re
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

_model = None
_tokenizer = None


def _load_model():
    """Lazy load the Llama model and tokenizer."""
    global _model, _tokenizer

    if _model is None or _tokenizer is None:
        try:
            model_name = os.getenv(
                "LLAMA_MODEL_NAME", "meta-llama/Meta-Llama-3-8B-Instruct"
            )
            _tokenizer = AutoTokenizer.from_pretrained(model_name)
            _model = AutoModelForCausalLM.from_pretrained(
                model_name,
                torch_dtype=torch.bfloat16,
                device_map="auto",
            )

        except Exception as e:
            raise RuntimeError(f"Failed to load Llama model: {str(e)}")

    return _model, _tokenizer


def generate_keywords_with_llama(biography: str, num_keywords: int = 5) -> list[str]:
    """
    Generate keywords for a faculty member's biography using llama.

    Args:
        biography (str): The biography of the faculty member.
        num_keywords (int): The number of keywords to generate.

    Returns:
        list[str]: A list of keywords generated from the biography.
    """
    if not biography or not biography.strip():
        return []

    try:
        model, tokenizer = _load_model()

        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant that generates only research keywords separated by commas and no extra text based on a faculty member's biography.",
            },
            {
                "role": "user",
                "content": f"Based on the following biography, generate exactly {num_keywords} research keywords that best describe this faculty member's work and expertise. Return only the keywords, separated by commas, with no additional text.\n\nBiography:\n{biography}\n\nKeywords:",
            },
        ]

        input_ids = tokenizer.apply_chat_template(
            messages, add_generation_prompt=True, return_tensors="pt"
        ).to(model.device)

        terminators = [
            tokenizer.eos_token_id,
            tokenizer.convert_tokens_to_ids("<|eot_id|>"),
        ]

        # Generate keywords
        with torch.no_grad():
            outputs = model.generate(
                input_ids,
                eos_token_ids=terminators,
                max_new_tokens=100,
                temperature=0.6,
                do_sample=True,
                top_p=0.9,
            )

        # Decode only the newly generated tokens (excluding the input prompt)
        response = outputs[0][input_ids.shape[-1] :]
        keywords_text = tokenizer.decode(response, skip_special_tokens=True).strip()

        # Parse keywords from the response
        keywords = _parse_keywords(keywords_text, num_keywords)
        return keywords[:num_keywords]

    except Exception as e:
        raise RuntimeError(f"Error generating keywords with Llama: {str(e)}")


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
