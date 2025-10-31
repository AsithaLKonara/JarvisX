"""
JARVIS AI - Fine-tuning Manager
Handles model fine-tuning with Hugging Face PEFT and LoRA for lightweight training.
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
import subprocess
import tempfile

class FineTuningManager:
    """
    Manages AI model fine-tuning using Hugging Face PEFT and LoRA.
    Provides lightweight training without heavy GPU requirements.
    """
    
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """Initialize fine-tuning manager."""
        self.logger = logging.getLogger(__name__)
        self.model_name = model_name
        self.training_config = {
            'learning_rate': 5e-5,
            'num_epochs': 3,
            'batch_size': 4,
            'max_length': 512,
            'lora_rank': 16,
            'lora_alpha': 32,
            'lora_dropout': 0.1
        }
        
        self.logger.info(f"Fine-tuning Manager initialized for model: {model_name}")
    
    def prepare_training_environment(self) -> bool:
        """Prepare Google Colab Pro environment for training."""
        try:
            self.logger.info("Preparing training environment...")
            
            # Create Colab notebook template
            colab_notebook = self._create_colab_notebook()
            
            # Save notebook
            notebook_path = "training/helagpt_finetuning.ipynb"
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(colab_notebook, f, indent=2)
            
            # Create requirements file
            requirements = self._create_requirements_file()
            with open("training/requirements.txt", 'w') as f:
                f.write(requirements)
            
            # Create training script
            training_script = self._create_training_script()
            with open("training/train_model.py", 'w', encoding='utf-8') as f:
                f.write(training_script)
            
            self.logger.info("Training environment prepared successfully")
            return True
        
        except Exception as e:
            self.logger.error(f"Error preparing training environment: {e}")
            return False
    
    def create_training_dataset(self, dataset_file: str = "training_dataset.json") -> bool:
        """Create training dataset from collected data."""
        try:
            from training.dataset_collector import DatasetCollector
            
            collector = DatasetCollector()
            dataset = collector.create_training_dataset(dataset_file)
            
            if dataset:
                self.logger.info(f"Training dataset created: {dataset_file}")
                return True
            else:
                self.logger.error("Failed to create training dataset")
                return False
        
        except Exception as e:
            self.logger.error(f"Error creating training dataset: {e}")
            return False
    
    def start_finetuning_process(self, dataset_path: str = "training_dataset.json") -> Dict[str, Any]:
        """Start the fine-tuning process."""
        try:
            self.logger.info("Starting fine-tuning process...")
            
            # Validate dataset exists
            if not Path(dataset_path).exists():
                self.logger.error(f"Dataset not found: {dataset_path}")
                return {'success': False, 'error': 'Dataset not found'}
            
            # Create training configuration
            config = {
                'model_name': self.model_name,
                'dataset_path': dataset_path,
                'output_dir': 'helagpt-finetuned',
                'training_config': self.training_config,
                'timestamp': datetime.now().isoformat()
            }
            
            # Save configuration
            config_path = "training/training_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
            
            # Generate training instructions
            instructions = self._generate_training_instructions(config)
            
            self.logger.info("Fine-tuning process prepared")
            return {
                'success': True,
                'config': config,
                'instructions': instructions,
                'next_steps': [
                    "1. Upload training files to Google Colab Pro",
                    "2. Run the provided notebook",
                    "3. Download the fine-tuned model",
                    "4. Integrate with Jarvis AI"
                ]
            }
        
        except Exception as e:
            self.logger.error(f"Error starting fine-tuning process: {e}")
            return {'success': False, 'error': str(e)}
    
    def _create_colab_notebook(self) -> Dict[str, Any]:
        """Create Google Colab notebook for fine-tuning."""
        return {
            "cells": [
                {
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "# HelaGPT Fine-tuning with PEFT and LoRA\n",
                        "\n",
                        "This notebook fine-tunes a language model using Parameter-Efficient Fine-Tuning (PEFT) with LoRA adapters."
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Install required packages\n",
                        "!pip install transformers datasets peft accelerate bitsandbytes\n",
                        "!pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Import libraries\n",
                        "import torch\n",
                        "from transformers import (\n",
                        "    AutoTokenizer, AutoModelForCausalLM,\n",
                        "    TrainingArguments, Trainer, DataCollatorForLanguageModeling\n",
                        ")\n",
                        "from peft import LoraConfig, get_peft_model, TaskType\n",
                        "from datasets import Dataset\n",
                        "import json\n",
                        "import os"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Load training configuration\n",
                        "with open('training_config.json', 'r') as f:\n",
                        "    config = json.load(f)\n",
                        "\n",
                        "model_name = config['model_name']\n",
                        "dataset_path = config['dataset_path']\n",
                        "output_dir = config['output_dir']\n",
                        "training_config = config['training_config']"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Load and prepare dataset\n",
                        "with open(dataset_path, 'r') as f:\n",
                        "    dataset = json.load(f)\n",
                        "\n",
                        "# Convert to Hugging Face format\n",
                        "train_data = []\n",
                        "for example in dataset['examples']:\n",
                        "    train_data.append({\n",
                        "        'text': f\"Human: {example['input']}\\nAssistant: {example['output']}\"\n",
                        "    })\n",
                        "\n",
                        "hf_dataset = Dataset.from_list(train_data)\n",
                        "print(f\"Loaded {len(hf_dataset)} training examples\")"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Load model and tokenizer\n",
                        "tokenizer = AutoTokenizer.from_pretrained(model_name)\n",
                        "model = AutoModelForCausalLM.from_pretrained(\n",
                        "    model_name,\n",
                        "    torch_dtype=torch.float16,\n",
                        "    device_map=\"auto\"\n",
                        ")\n",
                        "\n",
                        "# Add padding token if not present\n",
                        "if tokenizer.pad_token is None:\n",
                        "    tokenizer.pad_token = tokenizer.eos_token"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Configure LoRA\n",
                        "lora_config = LoraConfig(\n",
                        "    task_type=TaskType.CAUSAL_LM,\n",
                        "    r=training_config['lora_rank'],\n",
                        "    lora_alpha=training_config['lora_alpha'],\n",
                        "    lora_dropout=training_config['lora_dropout'],\n",
                        "    target_modules=[\"q_proj\", \"v_proj\"]\n",
                        ")\n",
                        "\n",
                        "# Apply LoRA to model\n",
                        "model = get_peft_model(model, lora_config)\n",
                        "model.print_trainable_parameters()"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Tokenize dataset\n",
                        "def tokenize_function(examples):\n",
                        "    return tokenizer(\n",
                        "        examples['text'],\n",
                        "        truncation=True,\n",
                        "        padding=True,\n",
                        "        max_length=training_config['max_length']\n",
                        "    )\n",
                        "\n",
                        "tokenized_dataset = hf_dataset.map(tokenize_function, batched=True)\n",
                        "data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Training arguments\n",
                        "training_args = TrainingArguments(\n",
                        "    output_dir=output_dir,\n",
                        "    num_train_epochs=training_config['num_epochs'],\n",
                        "    per_device_train_batch_size=training_config['batch_size'],\n",
                        "    learning_rate=training_config['learning_rate'],\n",
                        "    logging_steps=10,\n",
                        "    save_steps=100,\n",
                        "    evaluation_strategy=\"no\",\n",
                        "    save_total_limit=2,\n",
                        "    remove_unused_columns=False,\n",
                        "    push_to_hub=False\n",
                        ")\n",
                        "\n",
                        "# Create trainer\n",
                        "trainer = Trainer(\n",
                        "    model=model,\n",
                        "    args=training_args,\n",
                        "    train_dataset=tokenized_dataset,\n",
                        "    data_collator=data_collator,\n",
                        "    tokenizer=tokenizer\n",
                        ")"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Start training\n",
                        "print(\"Starting training...\")\n",
                        "trainer.train()\n",
                        "print(\"Training completed!\")"
                    ]
                },
                {
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": [
                        "# Save the fine-tuned model\n",
                        "trainer.save_model()\n",
                        "tokenizer.save_pretrained(output_dir)\n",
                        "\n",
                        "# Test the model\n",
                        "def generate_response(prompt, max_length=100):\n",
                        "    inputs = tokenizer.encode(prompt, return_tensors=\"pt\")\n",
                        "    with torch.no_grad():\n",
                        "        outputs = model.generate(\n",
                        "            inputs,\n",
                        "            max_length=max_length,\n",
                        "            num_return_sequences=1,\n",
                        "            temperature=0.7,\n",
                        "            do_sample=True,\n",
                        "            pad_token_id=tokenizer.eos_token_id\n",
                        "        )\n",
                        "    return tokenizer.decode(outputs[0], skip_special_tokens=True)\n",
                        "\n",
                        "# Test with sample prompt\n",
                        "test_prompt = \"Human: Help me organize my files\\nAssistant:\"\n",
                        "response = generate_response(test_prompt)\n",
                        "print(f\"Test response: {response}\")"
                    ]
                }
            ],
            "metadata": {
                "kernelspec": {
                    "display_name": "Python 3",
                    "language": "python",
                    "name": "python3"
                }
            },
            "nbformat": 4,
            "nbformat_minor": 4
        }
    
    def _create_requirements_file(self) -> str:
        """Create requirements file for training."""
        return """transformers>=4.30.0
datasets>=2.12.0
peft>=0.4.0
accelerate>=0.20.0
bitsandbytes>=0.39.0
torch>=2.0.0
numpy>=1.24.0
pandas>=2.0.0
scikit-learn>=1.3.0
tqdm>=4.65.0
wandb>=0.15.0
"""
    
    def _create_training_script(self) -> str:
        """Create standalone training script."""
        return '''"""
HelaGPT Fine-tuning Script
Standalone script for fine-tuning with PEFT and LoRA.
"""

import json
import torch
from transformers import (
    AutoTokenizer, AutoModelForCausalLM,
    TrainingArguments, Trainer, DataCollatorForLanguageModeling
)
from peft import LoraConfig, get_peft_model, TaskType
from datasets import Dataset
import os

def load_config(config_path="training_config.json"):
    """Load training configuration."""
    with open(config_path, 'r') as f:
        return json.load(f)

def prepare_dataset(dataset_path):
    """Prepare dataset for training."""
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    
    train_data = []
    for example in dataset['examples']:
        train_data.append({
            'text': f"Human: {example['input']}\\nAssistant: {example['output']}"
        })
    
    return Dataset.from_list(train_data)

def setup_model_and_tokenizer(model_name):
    """Setup model and tokenizer."""
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto"
    )
    
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    return model, tokenizer

def setup_lora(model, config):
    """Setup LoRA configuration."""
    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=config['lora_rank'],
        lora_alpha=config['lora_alpha'],
        lora_dropout=config['lora_dropout'],
        target_modules=["q_proj", "v_proj"]
    )
    
    return get_peft_model(model, lora_config)

def main():
    """Main training function."""
    # Load configuration
    config = load_config()
    model_name = config['model_name']
    dataset_path = config['dataset_path']
    output_dir = config['output_dir']
    training_config = config['training_config']
    
    print(f"Starting fine-tuning for {model_name}")
    
    # Prepare dataset
    dataset = prepare_dataset(dataset_path)
    print(f"Loaded {len(dataset)} training examples")
    
    # Setup model and tokenizer
    model, tokenizer = setup_model_and_tokenizer(model_name)
    
    # Setup LoRA
    model = setup_lora(model, training_config)
    model.print_trainable_parameters()
    
    # Tokenize dataset
    def tokenize_function(examples):
        return tokenizer(
            examples['text'],
            truncation=True,
            padding=True,
            max_length=training_config['max_length']
        )
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    data_collator = DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        num_train_epochs=training_config['num_epochs'],
        per_device_train_batch_size=training_config['batch_size'],
        learning_rate=training_config['learning_rate'],
        logging_steps=10,
        save_steps=100,
        evaluation_strategy="no",
        save_total_limit=2,
        remove_unused_columns=False,
        push_to_hub=False
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        data_collator=data_collator,
        tokenizer=tokenizer
    )
    
    # Start training
    print("Starting training...")
    trainer.train()
    print("Training completed!")
    
    # Save model
    trainer.save_model()
    tokenizer.save_pretrained(output_dir)
    print(f"Model saved to {output_dir}")

if __name__ == "__main__":
    main()
'''
    
    def _generate_training_instructions(self, config: Dict[str, Any]) -> List[str]:
        """Generate step-by-step training instructions."""
        return [
            "🚀 HelaGPT Fine-tuning Instructions",
            "",
            "1. **Setup Google Colab Pro**",
            "   - Open Google Colab Pro (colab.research.google.com)",
            "   - Create a new notebook",
            "   - Enable GPU runtime (Runtime > Change runtime type > GPU)",
            "",
            "2. **Upload Training Files**",
            "   - Upload `helagpt_finetuning.ipynb` to Colab",
            "   - Upload `training_dataset.json` to Colab",
            "   - Upload `training_config.json` to Colab",
            "",
            "3. **Run the Notebook**",
            "   - Execute all cells in sequence",
            "   - Monitor training progress in the output",
            "   - Training will take 30-60 minutes depending on dataset size",
            "",
            "4. **Download Results**",
            "   - Download the `helagpt-finetuned` folder",
            "   - This contains your fine-tuned model and tokenizer",
            "",
            "5. **Integration with Jarvis**",
            "   - Place model files in `models/helagpt-finetuned/`",
            "   - Update AI engine to use the fine-tuned model",
            "",
            f"**Configuration:**",
            f"- Model: {config['model_name']}",
            f"- Epochs: {config['training_config']['num_epochs']}",
            f"- Learning Rate: {config['training_config']['learning_rate']}",
            f"- Batch Size: {config['training_config']['batch_size']}",
            f"- LoRA Rank: {config['training_config']['lora_rank']}"
        ]
    
    def estimate_training_time(self, dataset_size: int) -> Dict[str, Any]:
        """Estimate training time based on dataset size."""
        try:
            # Rough estimates based on typical fine-tuning
            base_time_minutes = 15  # Base time for setup
            time_per_example = 0.1  # Minutes per example
            
            estimated_minutes = base_time_minutes + (dataset_size * time_per_example)
            
            return {
                'dataset_size': dataset_size,
                'estimated_minutes': int(estimated_minutes),
                'estimated_hours': round(estimated_minutes / 60, 1),
                'recommended_gpu': 'T4' if dataset_size < 1000 else 'V100',
                'memory_requirement': '8GB' if dataset_size < 500 else '16GB'
            }
        
        except Exception as e:
            self.logger.error(f"Error estimating training time: {e}")
            return {}
    
    def validate_dataset(self, dataset_path: str) -> Dict[str, Any]:
        """Validate training dataset quality."""
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            examples = dataset.get('examples', [])
            
            # Calculate validation metrics
            total_examples = len(examples)
            avg_input_length = sum(len(ex['input'].split()) for ex in examples) / total_examples if total_examples > 0 else 0
            avg_output_length = sum(len(ex['output'].split()) for ex in examples) / total_examples if total_examples > 0 else 0
            
            quality_scores = [ex.get('quality_score', 0.5) for ex in examples]
            avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
            
            # Validation results
            validation = {
                'total_examples': total_examples,
                'avg_input_length': round(avg_input_length, 1),
                'avg_output_length': round(avg_output_length, 1),
                'avg_quality_score': round(avg_quality, 3),
                'is_valid': total_examples >= 50 and avg_quality > 0.3,
                'recommendations': []
            }
            
            # Add recommendations
            if total_examples < 50:
                validation['recommendations'].append("Dataset too small - collect more examples")
            if avg_quality < 0.3:
                validation['recommendations'].append("Low quality examples - improve data quality")
            if avg_input_length < 5:
                validation['recommendations'].append("Input texts too short - add more context")
            if avg_output_length < 10:
                validation['recommendations'].append("Output texts too short - provide more detailed responses")
            
            return validation
        
        except Exception as e:
            self.logger.error(f"Error validating dataset: {e}")
            return {'is_valid': False, 'error': str(e)}
