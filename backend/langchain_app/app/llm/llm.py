import json
from transformers import pipeline, set_seed
from typing import Optional, List, Any
from langchain_core.callbacks import CallbackManagerForLLMRun


class HuggingFaceLLM:
    def __init__(self, model_name: str = "gpt2", seed: Optional[int] = None):
        self.generator = pipeline("text-generation", model=model_name)
        if seed is not None:
            set_seed(seed)

    def _call(
            self,
            prompt: str,
            stop: Optional[List[str]] = None,
            run_manager: Optional[CallbackManagerForLLMRun] = None,
            max_length: int = 200,
            **kwargs: Any
    ) -> str:
        """Return next response"""
        generated_texts = self.generator(prompt, max_length=max_length, num_return_sequences=1)
        response = generated_texts[0]["generated_text"]
        return response


# Create an instance of the real LLM
llm = HuggingFaceLLM(model_name="gpt2", seed=42)
