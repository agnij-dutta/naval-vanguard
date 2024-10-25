from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration
from datasets import load_dataset

# Load the dataset directly from Hugging Face with a specified config
# dataset = load_dataset("wiki_dpr", "psgs_w100.nq.exact")

# Load pre-trained RAG model and tokenizer
model_name = "facebook/rag-token-nq"  
tokenizer = RagTokenizer.from_pretrained(model_name)
model = RagSequenceForGeneration.from_pretrained(model_name)

# Initialize the retriever with the loaded passages
retriever = RagRetriever.from_pretrained(model_name, index_name="exact", use_dummy_dataset=True)

def process_message_rag_pipeline(message, detail, tokenizer=tokenizer, model=model, retriever=retriever):
    prompt = f"Extract any detail you find about {detail} from the report field of the given data: {message}"
    # Tokenize the input message
    inputs = tokenizer([prompt], return_tensors="pt")
    
    # Retrieve relevant documents
    input_ids = inputs["input_ids"]
    retrieved_docs = retriever(input_ids.numpy(), return_tensors="pt")

    # Generate the output
    try:
        generated = model.generate(
            input_ids,
            context_input_ids=retrieved_docs['context_input_ids']
        )
        generated_text = tokenizer.batch_decode(generated, skip_special_tokens=True)
        return generated_text[0]
    except TypeError as e:
        print(f"Error in RAG generation: {e}")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return ""