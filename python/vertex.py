import vertexai
from vertexai.language_models import TextGenerationModel

def summarize(
    text_to_summarize: str, 
    temperature: float = 0.95, 
    max_output_tokens: int = 256,
    max_retries: int = 3
) -> str:
    """Enhanced Summarization Example with a Large Language Model using Vertex AI"""
    
    # Initialize Vertex AI with the project and location
    vertexai.init()

    # Define the parameters for the model
    parameters = {
        "temperature": temperature,  # Controls the randomness in token selection.
        "max_output_tokens": max_output_tokens,  # Sets the maximum output size.
        "top_p": 0.95,  # Selects tokens based on probability sum.
        "top_k": 40,  # Limits the selection to the top k tokens.
    }

    # The prompt that asks for text summarization
    prompt = f"""Provide a summary with about two sentences for the following article:\n{text_to_summarize}\nSummary:"""

    # Load the model
    model = TextGenerationModel.from_pretrained("text-bison")
    attempts = 0
    response = None
    
    while attempts < max_retries:
        response = model.predict(prompt, **parameters)
        response_text = response.text.strip()
        if response_text:
            return response_text
        else:
            attempts += 1
            print(f"Attempt {attempts} failed, retrying...")
    
    print("Failed to get a non-empty response after maximum retries.")
    return ""