import vertexai
from vertexai.language_models import TextGenerationModel

def summarize(
    text_to_summarize: str, 
    temperature: float = 0.95, 
    max_output_tokens: int = 256,
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
    model = TextGenerationModel.from_pretrained("text-bison@001")

    # Get the model's prediction
    response = model.predict(prompt, **parameters)

    return response.text