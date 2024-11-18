import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
import google.generativeai as genai

genai.configure(api_key=settings.GENERATIVE_AI_API_KEY)

# Read the additional code file content
def read_code_file(file_path):
    """Read the contents of the code file."""
    with open(file_path, 'r') as file:
        return file.read()

# Generate a single PDF with the combined summary content
def generate_combined_pdf(contents, output_file):
    """Generate a PDF with combined summaries."""
    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    left_margin = 72  # 1-inch margin
    right_margin = 72  # 1-inch margin
    usable_width = width - left_margin - right_margin
    text_y = height - left_margin  # Start position for text

    for content in contents:
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

        # Add a page break between summaries
        c.showPage()

    c.save()

# Generate a summary for a single file
def generate_file_summary(file_path):
    """Generate a summary for a single file."""
    try:
        code_content = read_code_file(file_path)
        combined_prompt = f"Summarize the code:\n\n{code_content}"
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(combined_prompt)

        if hasattr(response, 'text'):
            return response.text
        else:
            return f"Summary not generated for {file_path}"
    except Exception as e:
        return f"Error summarizing {file_path}: {str(e)}"

# Process a directory of files
def process_directory(directory, author):
    dir_path = f"{settings.MEDIA_ROOT}/{author}/{directory}"
    """Process a directory and generate a combined summary PDF."""
    summaries = []
    for root, _, files in os.walk(dir_path):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            summary = generate_file_summary(file_path)
            summaries.append(f"File: {file_name}\n\n{summary}")

    output_dir = os.path.join(settings.MEDIA_ROOT, author, "results")
    os.makedirs(output_dir, exist_ok=True)

    output_file_name = f"summary_{directory}.pdf"
    output_file_path = os.path.join(output_dir, output_file_name)
    generate_combined_pdf(summaries, output_file_path)

    return output_file_path,output_file_name

# Example function to handle a request
def process_file(directory, author):
    """Handle a directory upload and generate a combined summary."""
    try:
        output_path, output_file_name = process_directory(directory, author)
        return {
            'summary_path': output_path,
            'summary_file_name': output_file_name}
    except Exception as e:
        return {'error': str(e)}