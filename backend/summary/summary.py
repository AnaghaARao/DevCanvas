import google.generativeai as genai

def read_additional_text(file_path):
    """Read additional text from a code file."""
    with open(file_path, 'r') as file:
        return file.read()

def test_text_gen_text_only_prompt():
    # Initialize the Generative AI model
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    # Original prompt
    original_prompt = "Summarise the code:"
    
    # Path to the code file with additional text
    code_file_path = '/content/fib.py'
    
    # Read additional text from the file
    additional_text = read_additional_text(code_file_path)
    
    # Combine the original prompt with additional text
    combined_prompt = f"{original_prompt}\n\n{additional_text}"
    
    # Generate content using the combined prompt
    response = model.generate_content(combined_prompt)
    
    # Print or use the response
    print(response.text)

if _name_ == "_main_":
    test_text_gen_text_only_prompt()
