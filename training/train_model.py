"""
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
            'text': f"Human: {example['input']}\nAssistant: {example['output']}"
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
