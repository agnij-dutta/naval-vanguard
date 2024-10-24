from transformers import RagTokenizer, RagRetriever, RagTokenForGeneration, Trainer, TrainingArguments, RagSequenceForGeneration
from datasets import Dataset, load_dataset
import os
from utils import *
import json
import torch

tokenizer = RagTokenizer.from_pretrained("facebook/rag-token-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-token-nq", use_dummy_dataset=True)
model = RagTokenForGeneration.from_pretrained("facebook/rag-token-nq", retriever=retriever)
# data = []

# directory = os.fsencode('/maritime-situational-awareness/data')
    
# for file in os.listdir(directory):
#     filename = os.fsdecode(file)
#     if filename.endswith(".md"): 
#         report = parse_maritime_reports(filename)
#         data.append(report)
#     else:
#         continue
    


def create_knowledge_corpus():
    # Initialize the knowledge corpus
    file_path = r'data/Maritime Situational Awareness/maritime-dataset-v1.md'
    data = read_maritime_data(file_path)
    parsed_data = parse_maritime_data(data)
    
    knowledge_corpus = parsed_data
    
    # Save the knowledge corpus to a JSON file
    with open('knowledge_corpus.json', 'w') as f:
        json.dump(knowledge_corpus, f, indent=4)

# Create the knowledge corpus
create_knowledge_corpus()


def prepare_finetuning_dataset(knowledge_corpus):

    """Prepare the fine-tuning dataset from the knowledge corpus."""

    dataset = []

    # Combine all data into a single dataset for RAG processing
    for report in knowledge_corpus["maritime_reports"]:
       dataset.append(report["report"])

    for note in knowledge_corpus["reconnaissance_notes"]:
        dataset.append(note["note"])

    for message in knowledge_corpus["communication_messages"]:
        dataset.append(" ".join(message["details"]))

    for zone in knowledge_corpus["geographical_data"]["maritime_zones"]:
        dataset.append(zone["description"])

    for lane in knowledge_corpus["geographical_data"]["shipping_lanes"]:
        dataset.append(lane["description"])
        
    return dataset


# Load the knowledge corpus from the JSON file
with open('knowledge_corpus.json', 'r') as f:
    knowledge_corpus = json.load(f)

# Prepare the fine-tuning dataset
finetuning_dataset = prepare_finetuning_dataset(knowledge_corpus)


def fine_tune_rag_model(finetuning_dataset):
    """Fine-tune the RAG model using the prepared dataset."""

    # Convert dataset to a Hugging Face Dataset
    dataset = Dataset.from_list(finetuning_dataset)

    # Tokenize the dataset
    def tokenize_function(examples):
        return tokenizer(examples["question"], padding="max_length", truncation=True)

    tokenized_dataset = dataset.map(tokenize_function, batched=True)

    # Create input and label tensors
    input_ids = tokenized_dataset["input_ids"]
    labels = tokenizer(tokenized_dataset["answer"], padding="max_length", truncation=True).input_ids

    # Create a Trainer instance
    training_args = TrainingArguments(
        output_dir='./results',
        num_train_epochs=3,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=64,
        evaluation_strategy='epoch',
        learning_rate=5e-5,
        save_total_limit=2,
        save_steps=500,
        load_best_model_at_end=True,
        metric_for_best_model='accuracy',
        greater_is_better=True,
        save_strategy='epoch',
        report_to='none'
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
        eval_dataset=tokenized_dataset,
        compute_metrics=lambda pred: {"accuracy": torch.sum(pred.label_ids == pred.predictions.argmax(-1)).item() / len(pred.label_ids)},
        tokenizer=tokenizer
    )

    # Fine-tune the model
    trainer.train()


# Fine-tune the RAG model
fine_tune_rag_model(finetuning_dataset)