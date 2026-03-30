#!/usr/bin/env python3
"""
Generate Training Data for Nmap LLM Fine-tuning
Generates multiple formats for different fine-tuning frameworks
"""

import json
import os
import re
from pathlib import Path

def load_training_data(data_dir):
    """Load base training data"""
    with open(data_dir / 'training_data.json') as f:
        return json.load(f)

def augment_with_ip_variations(data):
    """Augment training data with different IP variations"""
    augmented = []
    
    ip_mappings = [
        ('192.168.1.1', '10.10.10.10'),
        ('192.168.1.0/24', '172.16.0.0/16'),
        ('10.0.0.1', '192.168.50.50'),
        ('192.168.2.0/24', '10.20.30.0/24'),
        ('10.10.10.5', '172.20.0.50'),
        ('10.10.10.10', '192.168.100.100'),
    ]
    
    for item in data['instructions']:
        augmented.append(item)
        
        text = item['input'] + ' ' + item['output']
        
        for orig_ip, new_ip in ip_mappings:
            if orig_ip in text:
                new_item = {
                    'instruction': item['instruction'],
                    'input': item['input'].replace(orig_ip, new_ip),
                    'output': item['output'].replace(orig_ip, new_ip)
                }
                augmented.append(new_item)
    
    return augmented

def generate_qwen_format(data, output_path):
    """Generate training data for Qwen model"""
    with open(output_path, 'w') as f:
        for item in data:
            prompt = f"""<|im_start|>system
You are an expert penetration tester AI specialized in nmap scanning. Output the nmap commands for the given scan workflow.
<|im_end|>
<|im_start|>user
{item['input']}<|im_end|>
<|im_start|>assistant
{item['output']}<|im_end|>
"""
            f.write(prompt)
    print(f"Generated: {output_path} ({len(data)} examples)")

def generate_ollama_format(data, output_path):
    """Generate training data for Ollama"""
    with open(output_path, 'w') as f:
        for item in data:
            entry = {
                "instruction": item['instruction'],
                "input": item['input'],
                "output": item['output']
            }
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"Generated: {output_path} ({len(data)} examples)")

def generate_llama_format(data, output_path):
    """Generate training data for LLaMA models"""
    with open(output_path, 'w') as f:
        for item in data:
            text = f"""[INST] <<SYS>>
You are an expert penetration tester AI. Provide nmap commands for the given scan workflow.
</SYS>>

{item['input']} [/INST]

{item['output']}
"""
            f.write(json.dumps({"text": text}, ensure_ascii=False) + '\n')
    print(f"Generated: {output_path} ({len(data)} examples)")

def generate_mistral_format(data, output_path):
    """Generate training data for Mistral models"""
    with open(output_path, 'w') as f:
        for item in data:
            text = f"""<s>
[INST] You are an expert penetration tester. {item['instruction']} [/INST]
[INST] {item['input']} [/INST]

{item['output']}
</s>
"""
            f.write(json.dumps({"text": text}, ensure_ascii=False) + '\n')
    print(f"Generated: {output_path} ({len(data)} examples)")

def generate_system_format(data, output_path):
    """Generate with system messages for fine-tuning"""
    system_msg = """You are an expert penetration tester AI specialized in nmap network scanning and security assessment. Your role is to:
1. Execute systematic scan workflows (host discovery, port scan, service detection, OS detection, vulnerability scan)
2. Choose appropriate nmap commands based on target type and phase
3. Handle errors and provide fallback commands
4. Generate complete penetration testing workflows

When given a target and phase, output the appropriate nmap command(s). For full workflows, output all commands in order."""
    
    with open(output_path, 'w') as f:
        for item in data:
            entry = {
                "messages": [
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": item['input']},
                    {"role": "assistant", "content": item['output']}
                ]
            }
            f.write(json.dumps(entry, ensure_ascii=False) + '\n')
    print(f"Generated: {output_path} ({len(data)} examples)")

def generate_all_formats(data, output_dir):
    """Generate all format files"""
    generate_qwen_format(data, output_dir / 'training_qwen.txt')
    generate_ollama_format(data, output_dir / 'training_ollama.jsonl')
    generate_llama_format(data, output_dir / 'training_llama.jsonl')
    generate_mistral_format(data, output_dir / 'training_mistral.jsonl')
    generate_system_format(data, output_dir / 'training_chatml.jsonl')

def main():
    # Determine data directory
    import __main__
    if hasattr(__main__, '__file__') and __main__.__file__:
        data_dir = Path(__main__.__file__).parent
    else:
        # Jupyter/Colab environment
        data_dir = Path('/content/nmap-llama/finetune')
    
    data_dir = data_dir.resolve()
    
    print(f"Loading training data from: {data_dir}")
    
    data = load_training_data(data_dir)
    print(f"Loaded {len(data['instructions'])} base training examples")
    
    print("\nAugmenting data with IP variations...")
    augmented = augment_with_ip_variations(data)
    print(f"Augmented to {len(augmented)} examples")
    
    output_dir = data_dir / 'data'
    output_dir.mkdir(exist_ok=True)
    
    print("\nGenerating training formats...")
    generate_all_formats(augmented, output_dir)
    
    print("\n" + "="*50)
    print("Training data generation complete!")
    print("="*50)
    print(f"\nFiles in {output_dir}:")
    for f in sorted(output_dir.iterdir()):
        print(f"  - {f.name} ({f.stat().st_size // 1024} KB)")

if __name__ == "__main__":
    main()
