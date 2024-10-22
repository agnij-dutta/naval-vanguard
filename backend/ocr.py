import os
import cv2
import pytesseract
from PIL import Image
from transformers import pipeline

def extract_text_from_image(image_path):
    # Read the image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Write the pre-processed image to disk as a temporary file
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, thresh)
    
    # Load the image using pytesseract
    text = pytesseract.image_to_string(Image.open(filename))
    
    # Remove the temporary file
    os.remove(filename)
    return text


# Initialize the RAG model for contextual understanding
rag_pipeline = pipeline("text2text-generation", model="facebook/rag-sequence-nq")

def generate_questions_and_answers_from_text(text):
    """Generate question-answer pairs from the extracted text using RAG."""
    # Process the text through the RAG pipeline
    response = rag_pipeline(text)
    return response[0]['generated_text']  # Extract the generated text

def process_reconnaissance_image(image_path):
    """Process a reconnaissance image to extract data and generate Q&A."""
    # Step 1: Extract text from the image
    extracted_text = extract_text_from_image(image_path)
    
    # Step 2: Generate questions and answers using RAG
    qa_pairs = generate_questions_and_answers_from_text(extracted_text)
    
    return qa_pairs