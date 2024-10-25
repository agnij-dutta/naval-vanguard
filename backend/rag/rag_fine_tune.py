from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration, Trainer, TrainingArguments, GenerationConfig
import torch
import json
from datasets import Dataset

with open(r'..\backend\scripts\parsed_maritime_data.json', 'r') as infile:
    parsed_data = json.load(infile)

# Load pre-trained RAG model and tokenizer
model_name = "facebook/rag-token-nq"  
tokenizer = RagTokenizer.from_pretrained(model_name)
model = RagSequenceForGeneration.from_pretrained(model_name)

# Initialize the retriever with the loaded passages
retriever = RagRetriever.from_pretrained(model_name, index_name="exact", use_dummy_dataset=True, trust_remote_code=True)
dataset = Dataset.from_dict(parsed_data)

model.set_retriever(retriever)

# Tokenize and prepare inputs
def tokenize_function(examples):
    return tokenizer(examples['message'], padding="max_length", truncation=True, return_tensors="pt")

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Initialize model and tokenizer
model_name = "facebook/rag-token-nq"
tokenizer = RagTokenizer.from_pretrained(model_name)
model = RagSequenceForGeneration.from_pretrained(model_name)

# Fine-tuning settings
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    logging_dir="./logs",
)

# Custom Trainer class to handle fine-tuning with RAG
class MaritimeRagTrainer(Trainer):
    def compute_loss(self, model, inputs, return_outputs=False):
        input_ids = inputs["input_ids"]
        labels = inputs["labels"]
        outputs = model(input_ids=input_ids, labels=labels)
        loss = outputs.loss
        return (loss, outputs) if return_outputs else loss

# Initialize trainer
trainer = MaritimeRagTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# Fine-tune the model
trainer.train()

save_directory = "./fine_tuned_rag_model"

# Save the fine-tuned model
model.save_pretrained(save_directory)

# Save the tokenizer
tokenizer.save_pretrained(save_directory)

# Save the retriever (index) if needed (assumes retriever is already fine-tuned)
retriever.save_pretrained(save_directory)
