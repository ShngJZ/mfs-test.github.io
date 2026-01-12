#!/usr/bin/env python3
"""
PDF to PNG Converter
Converts multiple PDF files to PNG images (one per page).
"""

import fitz  # PyMuPDF
from pathlib import Path

def pdf_to_png(pdf_path, output_dir=None, dpi=200):
    """
    Convert PDF to PNG images.
    
    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save PNG files (default: same as PDF)
        dpi: Resolution of output images (default: 200)
    """
    pdf_path = Path(pdf_path)
    
    if output_dir is None:
        output_dir = pdf_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Converting {pdf_path} to PNG...")
    print(f"Output directory: {output_dir}")
    
    # Open PDF
    pdf_document = fitz.open(pdf_path)
    page_count = len(pdf_document)
    print(f"Found {page_count} page(s)")
    
    # Convert each page to PNG
    base_name = pdf_path.stem
    zoom = dpi / 72  # Convert DPI to zoom factor (72 is default PDF DPI)
    mat = fitz.Matrix(zoom, zoom)
    
    for page_num in range(page_count):
        page = pdf_document[page_num]
        pix = page.get_pixmap(matrix=mat)
        
        output_path = output_dir / f"{base_name}_page_{page_num+1}.png"
        pix.save(output_path)
        print(f"Saved: {output_path}")
    
    pdf_document.close()
    print(f"Done! Converted {page_count} page(s)\n")

if __name__ == "__main__":
    # Convert all PDFs
    pdfs = [
        "eth3d.pdf",
        "imc.pdf",
        "tnt.pdf",
        "scannet.pdf",
        "fastmap.pdf",
        "7scenes.pdf",
        "wayspots.pdf"
    ]
    
    for pdf in pdfs:
        if Path(pdf).exists():
            pdf_to_png(pdf, dpi=200)
        else:
            print(f"Warning: {pdf} not found, skipping...\n")
