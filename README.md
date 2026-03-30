# Nmap LLM Fine-tuning

Fine-tune a language model to execute complete nmap scanning workflows for penetration testing.

## Directory Structure

```
finetune/
├── README.md                  # This file
├── training_data.json         # Base training data (36 examples)
├── generate_training_data.py  # Script to generate multiple formats
├── nmap-finetune-colab.ipynb # Google Colab notebook
├── Modelfile                  # Ollama Modelfile template
└── data/
    ├── training_ollama.jsonl    # For Ollama fine-tuning
    ├── training_qwen.txt        # For Qwen models
    ├── training_llama.jsonl     # For LLaMA models
    ├── training_mistral.jsonl   # For Mistral models
    └── training_chatml.jsonl    # ChatML format
```

## Training Data Covers

### Complete Scan Workflows
- Host discovery → Port scanning → Service detection → OS detection → Vulnerability scan
- Multi-host scanning (CIDR ranges)
- Domain name scanning

### Target Types
- Single IP addresses
- CIDR ranges (192.168.1.0/24)
- Domain names (example.com)
- IP ranges (192.168.1.1-20)

### Scan Phases
1. **Host Discovery** - ARP, ICMP, TCP probes
2. **Port Scanning** - Quick, full, stealth scans
3. **Service Detection** - Version detection, default scripts
4. **OS Detection** - Fingerprinting
5. **Vulnerability Scanning** - NSE vuln scripts
6. **Service-Specific** - HTTP, SMB, SSH, MySQL, DNS, etc.

### Error Handling
- Permission denied fallbacks
- Timeout handling
- Alternative scan techniques

## Usage

### 1. Google Colab (Recommended)

1. Open `nmap-finetune-colab.ipynb` in Google Colab
2. Update `MODEL_NAME` to your preferred base model
3. Run all cells
4. Model saved to Google Drive

### 2. Local Training

```bash
# Generate training data
python generate_training_data.py

# Train with Ollama
ollama create nmap-qwen -f Modelfile

# Fine-tune with Axolotl or other frameworks
```

### 3. Use with Ollama

```bash
# After fine-tuning and converting to Ollama format
ollama run nmap-qwen-finetuned

# Example prompt
Target: 192.168.1.0/24
Type: CIDR Range
Goal: Full network assessment
```

## Model Recommendations

| Model | Size | VRAM | Quality |
|-------|------|------|---------|
| Qwen2-0.5B | 500MB | 2GB | Basic |
| Qwen2-1.5B | 1.5GB | 4GB | Good |
| Qwen2-7B | 7GB | 8GB | Excellent |
| Llama-3.2-3B | 3GB | 4GB | Good |

## Tips

1. **More data = better results** - Run actual scans and add outputs
2. **Augmentation** - IP variations included (192.168.1.x → 10.0.0.x)
3. **Epochs** - 3-5 for fine-tuning, more can overfit
4. **Learning rate** - 2e-4 to 3e-4 works well

## Integrating with Scanner

After fine-tuning:

```python
import ollama

response = ollama.generate(
    model='nmap-qwen-finetuned',
    prompt=f"Target: {target}\nType: {target_type}\nGoal: {goal}"
)
# Parse and execute commands
```
