---
name: airllm
description: "Run 70B+ parameter LLMs on a single 4GB GPU via layer-by-layer loading. No quantization required. Use when the user wants to run large language models on consumer hardware, deploy LLMs with minimal VRAM, or needs a drop-in replacement for HuggingFace transformers with low memory footprint. Triggers on: low VRAM LLM, 70B on 4GB, run LLM locally, layer-wise inference, airllm, 大模型低显存, 本地部署大模型."
license: Apache-2.0
compatibility: Python 3.8+, PyTorch, CUDA GPU (4GB+ VRAM) or Apple Silicon. pip install airllm. Drop-in replacement for transformers AutoModel.
metadata:
  author: lyogavin (curated by AthenDrakomin-hub)
  version: "1.0.0"
  category: development
  source: "https://github.com/lyogavin/airllm"
---

# AirLLM

Run 70B+ parameter LLMs on a single 4GB GPU. Layer-by-layer loading means you only need enough VRAM for one layer, not the entire model.

## Role

You are an LLM deployment specialist. Your job is to help users install, configure, and use AirLLM to run large language models on hardware with limited VRAM.

## What It Is

AirLLM enables inference of 70B+ parameter models on a single 4GB GPU by loading model layers one at a time into VRAM, computing, then offloading. No quantization needed — full precision inference.

## How It Works

Traditional inference requires the entire model in VRAM (70B ≈ 140GB in FP16). AirLLM:
1. Loads one transformer layer at a time into VRAM
2. Computes that layer's output
3. Offloads the layer, loads the next
4. Streams through all layers sequentially

Trade-off: speed (~20 seconds per token for 70B on 4GB) for dramatically lower hardware requirements.

## Installation

```bash
pip install airllm
```

Dependencies: PyTorch with CUDA support, HuggingFace hub, safetensors.

## Basic Usage

### Quick Start
```python
from airllm import AutoModel

MAX_LENGTH = 128

# Load model (HuggingFace repo ID or local path)
model = AutoModel.from_pretrained("garage-bAInd/Platypus2-70B-instruct")

# Tokenize
input_text = ["What is the capital of United States?"]
input_tokens = model.tokenizer(
    input_text,
    return_tensors="pt",
    truncation=True,
    max_length=MAX_LENGTH
)

# Generate
output = model.generate(
    input_tokens["input_ids"],
    max_new_tokens=50
)

# Decode
print(model.tokenizer.decode(output[0], skip_special_tokens=True))
```

### Llama 3.3 70B Example
```python
from airllm import AutoModel

model = AutoModel.from_pretrained("meta-llama/Llama-3.3-70B-Instruct")

input_ids = model.tokenizer(
    ["Explain quantum computing in simple terms."],
    return_tensors="pt"
).input_ids

output = model.generate(input_ids, max_new_tokens=100)
print(model.tokenizer.decode(output[0]))
```

### Save Layer Shards Locally
```python
model = AutoModel.from_pretrained(
    "meta-llama/Llama-3.3-70B-Instruct",
    layer_shards_saving_path="./llama70b_shards"
)
# Subsequent loads read from local shards (faster, no re-download)
```

## Supported Models

Any HuggingFace model in safetensors format:
- Llama 2/3/3.1/3.3 (7B to 70B)
- Mistral / Mixtral
- Qwen / Qwen2
- Yi
- DeepSeek
- And most other decoder-only LLMs

## Hardware Requirements

| Model | Min VRAM | Recommended | Speed (tokens/s) |
|---|---|---|---|
| 7B | 2GB | 4GB | ~5-10 |
| 13B | 3GB | 6GB | ~3-6 |
| 34B | 4GB | 8GB | ~1-3 |
| 70B | 4GB | 8GB+ | ~0.05-0.2 |

## Configuration Options

```python
model = AutoModel.from_pretrained(
    "model-name",
    # Device selection
    device="cuda",  # or "mps" for Apple Silicon
    
    # Layer shard caching
    layer_shards_saving_path="./shards",
    
    # Precision
    dtype="float16",  # or "float32"
    
    # Progress bar
    show_progress=True
)
```

## Apple Silicon (MPS)
```python
model = AutoModel.from_pretrained(
    "meta-llama/Llama-3.3-70B-Instruct",
    device="mps"
)
```
Requires macOS 12.3+, PyTorch with MPS backend. Uses unified memory — 16GB+ recommended.

## When to Use AirLLM vs Alternatives

| Scenario | AirLLM | Quantization (GGUF/GPTQ) | Full VRAM |
|---|---|---|---|
| Minimal hardware (4GB) | ✅ Best | ✅ Good | ❌ |
| Maximum quality (no quant loss) | ✅ Full precision | ❌ Lossy | ✅ |
| Interactive speed needed | ❌ Slow | ✅ Fast | ✅ Fastest |
| Batch inference | ❌ Very slow | ✅ OK | ✅ Best |
| One-off analysis / research | ✅ Perfect | ✅ Good | ✅ |

## Troubleshooting

| Problem | Solution |
|---|---|
| CUDA out of memory | Reduce batch size to 1, ensure no other GPU processes |
| Model download slow | Use HF mirror: `export HF_ENDPOINT=https://hf-mirror.com` |
| Tokenizer not found | Install `transformers`: `pip install transformers` |
| Very slow generation | Expected for 70B on 4GB (~20s/token); use smaller model for speed |
| Apple Silicon error | Set `device="mps"`, ensure PyTorch >= 2.0 with MPS |
| safetensors error | `pip install safetensors accelerate` |

## References

- GitHub: https://github.com/lyogavin/airllm
- PyPI: https://pypi.org/project/airllm/
- HuggingFace: https://huggingface.co/models (any safetensors model)
