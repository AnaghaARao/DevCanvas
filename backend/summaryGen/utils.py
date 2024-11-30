import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.conf import settings
from datetime import datetime
from reportlab.lib import colors
import google.generativeai as genai

genai.configure(api_key=settings.GENERATIVE_AI_API_KEY)

# Read the additional code file content
def read_code_file(file_path):
    """Read the contents of the code file."""
    with open(file_path, 'r') as file:
        return file.read()

# Generate a single PDF with the combined summary content
def generate_combined_pdf(contents, output_file):
    """Generate a PDF with combined summaries and a header/footer."""

    def create_header_footer(c, width, height):
        """Create a minimalist header and footer with separating lines."""
        c.saveState()
        
        # Header positioning
        header_top = height - 40

        # Add logo if it exists
        logo_path = settings.MEDIA_LOGO
        if os.path.exists(logo_path):
            c.drawImage(
                logo_path,
                72,  # Left margin
                header_top - 35,
                width=40,
                height=40,
                preserveAspectRatio=True,
            )

        # Add DevCanvas text next to logo
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(colors.Color(0.2, 0.2, 0.2))
        c.drawString(120, header_top - 25, "DevCanvas")

        # Add report generation date
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.Color(0.4, 0.4, 0.4))
        date_str = datetime.now().strftime("%B %d, %Y")
        c.drawString(width - 150, header_top - 25, f"Generated: {date_str}")

        # Header separation line
        c.setStrokeColor(colors.Color(0.8, 0.8, 0.8))
        c.line(50, header_top - 45, width - 50, header_top - 45)

        # Footer separation line
        c.line(50, 60, width - 50, 60)

        # Footer text
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.Color(0.4, 0.4, 0.4))
        c.drawString(72, 45, "© Generated by DevCanvas")

        # Add page number
        page_num = c.getPageNumber()
        c.drawRightString(width - 72, 45, f"Page {page_num}")

        c.restoreState()

    c = canvas.Canvas(output_file, pagesize=letter)
    width, height = letter
    left_margin = 72  # 1-inch margin
    right_margin = 72  # 1-inch margin
    usable_width = width - left_margin - right_margin
    header_footer_spacing = 100  # Space for header and footer
    line_height = 20  # Line height for text
    text_y = height - header_footer_spacing  # Adjust start position for text below header

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
                    if text_y < 80 + line_height:  # Ensure space for footer
                        # Add header and footer, then start a new page
                        create_header_footer(c, width, height)
                        c.showPage()
                        text_y = height - header_footer_spacing
                    c.drawString(left_margin, text_y, current_line)
                    text_y -= line_height
                    current_line = word

            if current_line:
                if text_y < 80 + line_height:  # Ensure space for footer
                    # Add header and footer, then start a new page
                    create_header_footer(c, width, height)
                    c.showPage()
                    text_y = height - header_footer_spacing
                c.drawString(left_margin, text_y, current_line)
                text_y -= line_height

        # Ensure enough space between sections
        text_y -= 40
        if text_y < 80 + line_height:  # Ensure space for footer
            create_header_footer(c, width, height)
            c.showPage()
            text_y = height - header_footer_spacing

    # Add header and footer on the last page
    create_header_footer(c, width, height)
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