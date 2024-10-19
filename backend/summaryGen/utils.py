import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import google.generativeai as genai

genai.configure(api_key="AIzaSyA10A05Rg49QOjQXTClE0m-82jNnMudh7k")

# Read the additional code file content
def read_code_file(file_path):
    """Read the contents of the code file."""
    with open(file_path, 'r') as file:
        return file.read()

# Generate a PDF file with the summary content
def generate_pdf(content, output_file):
    """Generate a PDF from the given content."""
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    left_margin = 72  # 1-inch margin
    right_margin = 72  # 1-inch margin
    usable_width = width - left_margin - right_margin
    text_y = height - left_margin  # Start position for text

    lines = content.splitlines()
    for line in lines:
        words = line.split(" ")
        current_line = ""

        for word in words:
            test_line = f"{current_line} {word}".strip()
            if c.stringWidth(test_line, "Helvetica", 12) <= usable_width:
                current_line = test_line
            else:
                c.drawString(left_margin, text_y, current_line)
                text_y -= 20
                current_line = word

        if current_line:
            c.drawString(left_margin, text_y, current_line)
            text_y -= 20

        if text_y < left_margin:  
            c.showPage()
            text_y = height - left_margin

    c.save()

# Generate a summary for any programming language
def generate_summary(file_path, doc_id):
    """Generate a summary based on the file content and language."""
    # Reading the file contents
    code_content = read_code_file(file_path)
    
    # Generating summary based on the programming language
    original_prompt = f"Summarize the code:"
    combined_prompt = f"{original_prompt}\n\n{code_content}"
    
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(combined_prompt)

        # Save the summary to a PDF file
        output_file = f"summary_{os.path.basename(file_path)}.pdf"
        generate_pdf(response.text, output_file)
        
        return output_file
    except Exception as e:
        print(f"Error generating summary for {doc_id}: {str(e)}")
        return None

# Process file for summary generation
def process_file(file_path, language, author, doc_id):
    """Process the file and generate a summary."""
    summary_pdf_path = generate_summary(file_path, doc_id)
    
    if summary_pdf_path:
        return {
            'summary_pdf': summary_pdf_path,
            'doc_id': doc_id,
            'author': author,
            'language': language
        }
    else:
        return {
            'error': f"Failed to generate summary for {doc_id}"
        }
