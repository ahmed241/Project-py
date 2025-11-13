from PIL import Image
import os

def create_pdf_from_sections(sections_folder, output_pdf):
    # Get all PNG files
    png_files = sorted([f for f in os.listdir(sections_folder) if f.endswith('.png')])
    
    if not png_files:
        print("No PNG files found!")
        return
    
    # Open images
    images = []
    for png_file in png_files:
        img_path = os.path.join(sections_folder, png_file)
        img = Image.open(img_path).convert('RGB')
        images.append(img)
    
    # Save as PDF
    if images:
        images[0].save(
            output_pdf,
            save_all=True,
            append_images=images[1:],
            resolution=100.0
        )
        print(f"PDF created: {output_pdf}")

sections_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), "images")
output_pdf = "MODI_Steps.pdf"
create_pdf_from_sections(sections_folder, output_pdf)