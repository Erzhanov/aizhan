import os
import json
from typing import List, Dict, Generator, Optional

try:
    from huggingface_hub import InferenceClient
except Exception:
    InferenceClient = None

# Environment
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

# Default model choice (cloud-friendly, high-quality conversational instruct models)
# The user can change this via function parameter or env var.
DEFAULT_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-Large-Instruct")


def build_prompt(messages: List[Dict[str, str]], system_prompt: Optional[str] = None) -> str:
    """Flatten conversation history into a single prompt string for HF text-generation models.

    messages: list of {role: 'system'|'user'|'assistant', content: str}
    """
    parts = []
    if system_prompt:
        parts.append(f"System: {system_prompt}\n")
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        prefix = "User" if role == "user" else "Assistant" if role == "assistant" else "System"
        parts.append(f"{prefix}: {content}\n")
    parts.append("Assistant:")
    return "\n".join(parts)


class HuggingFaceChat:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or HF_API_KEY
        self.model = model or DEFAULT_MODEL
        self.client = None
        if InferenceClient and self.api_key:
            try:
                self.client = InferenceClient(self.api_key)
            except Exception:
                self.client = None

    def generate(
        self,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 512,
        top_p: float = 1.0,
        stream: bool = False,
    ):
        """Generate a response. If stream=True, returns a generator yielding partial text chunks.

        Returns structure similar to ChatGPT: {'id','object','choices':[{'message':{'role','content'},'finish_reason'}], 'usage':{}}
        """
        prompt = build_prompt(messages, system_prompt)

        parameters = {
            "temperature": float(temperature),
            "top_p": float(top_p),
            "max_new_tokens": int(max_tokens),
        }

        # If we have huggingface_hub client and streaming requested, use it
        if self.client and stream:
            try:
                # huggingface_hub.InferenceClient.text_generation supports streaming
                for chunk in self.client.text_generation(self.model, inputs=prompt, parameters=parameters, stream=True):
                    # chunk is dict with 'generated_text' or token pieces depending on model
                    text = chunk.get("generated_text") or chunk.get("token", "")
                    yield {"delta": text}
                return
            except Exception:
                # fall back to non-streaming path below
                pass

        # Non-streaming path using requests to HF Inference API
        import requests

        url = f"https://api-inference.huggingface.co/models/{self.model}"
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"inputs": prompt, "parameters": parameters}

        # Stream mode via requests streaming (some HF models emit chunks)
        if stream:
            try:
                with requests.post(url, headers=headers, json=payload, stream=True, timeout=120) as resp:
                    resp.raise_for_status()
                    buffer = ""
                    for chunk in resp.iter_content(chunk_size=None):
                        if not chunk:
                            continue
                        part = chunk.decode(errors="ignore")
                        buffer += part
                        # Try to parse newline-delimited JSON or plain text
                        try:
                            data = json.loads(buffer)
                            text = ""
                            if isinstance(data, list) and data:
                                text = data[0].get("generated_text", "")
                            elif isinstance(data, dict):
                                text = data.get("generated_text", "")
                            if text:
                                yield {"delta": text}
                                buffer = ""
                        except Exception:
                            yield {"delta": part}
                    return
            except requests.HTTPError as http_e:
                # If the model is not available via the Inference API, HF returns 410 Gone
                status = None
                try:
                    status = http_e.response.status_code
                except Exception:
                    pass
                if status == 410:
                    raise RuntimeError(
                        f"Model '{self.model}' is not available via the Hugging Face Inference API (HTTP 410 Gone).\n"
                        "Possible fixes:\n"
                        " - Choose a model that supports the Inference API (check the model page on huggingface.co).\n"
                        " - Ensure your HUGGINGFACE_API_KEY has access to the model (private models require proper scopes).\n"
                        " - Or run a local inference server (Ollama, TGI, or transformers) and configure HF_MODEL accordingly."
                    ) from http_e
                raise

        # Non-streaming POST
        resp = requests.post(url, headers=headers, json=payload, timeout=120)
        try:
            resp.raise_for_status()
        except requests.HTTPError as http_e:
            status = None
            try:
                status = resp.status_code
            except Exception:
                pass
            if status == 410:
                raise RuntimeError(
                    f"Model '{self.model}' is not available via the Hugging Face Inference API (HTTP 410 Gone).\n"
                    "Possible fixes:\n"
                    " - Choose a model that supports the Inference API (check the model page on huggingface.co).\n"
                    " - Ensure your HUGGINGFACE_API_KEY has access to the model (private models require proper scopes).\n"
                    " - Or run a local inference server (Ollama, TGI, or transformers) and configure HF_MODEL accordingly."
                ) from http_e
            raise
        data = resp.json()

        # Normalize response into ChatGPT-like structure
        text = ""
        if isinstance(data, list) and data:
            text = data[0].get("generated_text", "")
        elif isinstance(data, dict):
            # some models return {'generated_text': '...'}
            text = data.get("generated_text") or data.get("text") or ""

        result = {
            "id": None,
            "object": "chat.completion",
            "choices": [
                {
                    "message": {"role": "assistant", "content": text},
                    "finish_reason": "stop",
                }
            ],
            "usage": {},
        }
        return result


def chat_completion(
    messages: List[Dict[str, str]],
    system_prompt: Optional[str] = None,
    model: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 512,
    top_p: float = 1.0,
    stream: bool = False,
):
    client = HuggingFaceChat(model=model)
    return client.generate(messages, system_prompt, temperature, max_tokens, top_p, stream)
