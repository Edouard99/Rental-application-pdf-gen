#!/usr/bin/env python3
"""
Enhanced PDF Watermarking and Combination Tool
Creates watermarked PDFs and combines them into a single master document.
"""

import os
import sys
import argparse
from pathlib import Path
import glob
from io import BytesIO
import logging

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.colors import Color
    from reportlab.lib.units import inch
    from PyPDF2 import PdfReader, PdfWriter
except ImportError as e:
    print(f"Required libraries not installed: {e}")
    print("Please run: pip install reportlab PyPDF2")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFWatermarker:
    """Class to handle PDF watermarking and combination operations."""
    
    def __init__(self, watermark_text="DOCUMENT RESERVE A LA LOCATION", opacity=0.3):
        self.watermark_text = watermark_text
        self.opacity = opacity
        self._adjustment_logged = False
        
    def create_watermark_pdf(self, width, height):
        """Create a watermark PDF overlay."""
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(width, height))
        
        # Set watermark properties
        can.setFillColor(Color(1, 0, 0, alpha=self.opacity))  # Red with transparency
        can.setFont("Helvetica-Bold", 24)
        
        # Calculate text dimensions and rotation parameters
        import math
        
        # Start with desired font size and scale down if needed
        max_font_size = 24
        min_font_size = 8
        font_size = max_font_size
        rotation_angle = 30  # degrees
        rotation_rad = math.radians(rotation_angle)
        
        # Calculate maximum allowable text width (considering rotation and page margins)
        # For a 30° rotation, the effective width usage is larger
        margin_factor = 0.1  # 10% margin on each side
        usable_width = width * (1 - 2 * margin_factor)
        
        # Account for rotation - rotated text takes more horizontal space
        rotation_width_factor = abs(math.cos(rotation_rad)) + abs(math.sin(rotation_rad)) * (font_size / width)
        max_allowed_width = usable_width / rotation_width_factor
        
        # Scale down font size if text is too wide
        text_width = can.stringWidth(self.watermark_text, "Helvetica-Bold", font_size)
        while text_width > max_allowed_width and font_size > min_font_size:
            font_size -= 1
            text_width = can.stringWidth(self.watermark_text, "Helvetica-Bold", font_size)
        
        # Log font size adjustment if needed
        if font_size < max_font_size and not self._adjustment_logged:
            logger.info(f"Watermark text scaled down to font size {font_size} to fit page width")
            self._adjustment_logged = True
        
        # If text is still too long even at minimum font size, truncate it
        if text_width > max_allowed_width:
            # Truncate text to fit
            truncated_text = self.watermark_text
            while text_width > max_allowed_width and len(truncated_text) > 10:
                truncated_text = truncated_text[:-3] + "..."
                text_width = can.stringWidth(truncated_text, "Helvetica-Bold", font_size)
            watermark_text = truncated_text
            if not self._adjustment_logged:
                logger.warning(f"Watermark text truncated to '{watermark_text}' to fit page width")
                self._adjustment_logged = True
        else:
            watermark_text = self.watermark_text
        
        # Set the calculated font size
        can.setFont("Helvetica-Bold", font_size)
        text_height = font_size
        
        # Calculate the center position for the rotated text
        # We want the center of the rotated text to be at width/2
        center_x = width / 2
        
        # For a rotated rectangle, we need to account for the rotation
        # The text's center after rotation will be offset from the translation point
        # We calculate the offset needed to center the rotated text
        text_center_offset_x = text_width / 2
        text_center_offset_y = text_height / 2
        
        # Apply rotation transformation to the offset
        rotated_offset_x = (text_center_offset_x * math.cos(rotation_rad) - 
                           text_center_offset_y * math.sin(rotation_rad))
        rotated_offset_y = (text_center_offset_x * math.sin(rotation_rad) + 
                           text_center_offset_y * math.cos(rotation_rad))
        
        # Calculate the translation point that will center the rotated text at center_x
        translate_x = center_x - rotated_offset_x
        
        # Add multiple watermarks across the page height, centered horizontally
        y_positions = [height * 0.2, height * 0.4, height * 0.6, height * 0.8]
        
        for y in y_positions:
            # Adjust y translation for vertical centering at this height
            translate_y = y - rotated_offset_y
            
            can.saveState()
            can.translate(translate_x, translate_y)
            can.rotate(rotation_angle)
            can.drawString(0, 0, watermark_text)
            can.restoreState()
        
        can.save()
        packet.seek(0)
        return PdfReader(packet)
    
    def watermark_pdf(self, input_path, output_path):
        """Apply watermark to a PDF file."""
        try:
            reader = PdfReader(str(input_path))
            writer = PdfWriter()
            
            for page_num, page in enumerate(reader.pages):
                # Get page dimensions
                page_box = page.mediabox
                page_width = float(page_box.width)
                page_height = float(page_box.height)
                
                # Create watermark for this page size
                watermark_pdf = self.create_watermark_pdf(page_width, page_height)
                watermark_page = watermark_pdf.pages[0]
                
                # Merge watermark with original page
                page.merge_page(watermark_page)
                writer.add_page(page)
            
            # Write watermarked PDF
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
                
            logger.info(f"Watermarked: {input_path.name} -> {output_path.name}")
            return True
            
        except Exception as e:
            logger.error(f"Error watermarking {input_path}: {e}")
            return False
    
    def combine_pdfs(self, pdf_paths, output_path):
        """Combine multiple PDFs into a single document."""
        writer = PdfWriter()
        
        for pdf_path in pdf_paths:
            try:
                reader = PdfReader(str(pdf_path))
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Added {pdf_path.name} to combined document")
            except Exception as e:
                logger.error(f"Error adding {pdf_path} to combined document: {e}")
        
        try:
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            logger.info(f"Combined PDF saved: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving combined PDF: {e}")
            return False

def find_pdf_files(folder_path):
    """Find all PDF files in a folder."""
    pdf_files = []
    for ext in ['*.pdf', '*.PDF']:
        pdf_files.extend(glob.glob(str(folder_path / ext)))
    # Remove duplicates by converting to set and back to list
    unique_files = list(set(pdf_files))
    return [Path(f) for f in unique_files]

def process_folder(source_folder, watermark_text="DOCUMENT RESERVE A LA LOCATION"):
    """Process all folders in the source directory."""
    source_path = Path(source_folder)
    if not source_path.exists():
        logger.error(f"Source folder does not exist: {source_folder}")
        return False
    
    # Create temporary directory for watermarked files
    temp_dir = source_path / "temp_watermarked"
    temp_dir.mkdir(exist_ok=True)
    
    # Initialize watermarker
    watermarker = PDFWatermarker(watermark_text)
    
    # List to store all watermarked PDF paths
    watermarked_pdfs = []
    
    # Folders to exclude
    exclude_folders = {"Dossier Location", "protected_files", "temp_watermarked"}
    
    # Process each subfolder
    for folder in source_path.iterdir():
        if folder.is_dir() and folder.name not in exclude_folders:
            logger.info(f"Processing folder: {folder.name}")
            
            # Find all PDF files in this folder
            pdf_files = find_pdf_files(folder)
            
            if not pdf_files:
                logger.info(f"No PDF files found in {folder.name}")
                continue
            
            # Process each PDF file
            for pdf_file in pdf_files:
                # Create output filename with sanitized path
                output_filename = f"{folder.name}_{pdf_file.stem}_watermarked.pdf"
                output_path = temp_dir / output_filename
                
                # Skip if already processed (avoid duplicates)
                if output_path in watermarked_pdfs:
                    continue
                
                # Apply watermark
                if watermarker.watermark_pdf(pdf_file, output_path):
                    watermarked_pdfs.append(output_path)
    
    if watermarked_pdfs:
        # Remove duplicates from the list while preserving order
        unique_watermarked_pdfs = []
        seen = set()
        for pdf_path in watermarked_pdfs:
            if pdf_path not in seen:
                unique_watermarked_pdfs.append(pdf_path)
                seen.add(pdf_path)
        
        # Sort PDFs by folder name and filename for consistent ordering
        unique_watermarked_pdfs.sort(key=lambda x: x.name)
        
        # Combine all watermarked PDFs
        combined_output = source_path / f"Dossier_Location_Complete_{watermark_text.replace(' ', '_')}.pdf"
        if watermarker.combine_pdfs(unique_watermarked_pdfs, combined_output):
            logger.info(f"Successfully created combined document: {combined_output}")
            
            # Clean up temporary files
            for temp_file in unique_watermarked_pdfs:
                try:
                    if temp_file.exists():
                        temp_file.unlink()
                        logger.debug(f"Deleted temporary file: {temp_file}")
                except Exception as e:
                    logger.warning(f"Could not delete temporary file {temp_file}: {e}")
            
            # Remove temporary directory if empty
            try:
                if temp_dir.exists() and not any(temp_dir.iterdir()):
                    temp_dir.rmdir()
                    logger.debug(f"Removed temporary directory: {temp_dir}")
            except Exception as e:
                logger.warning(f"Could not remove temporary directory: {e}")
            
            return True
    else:
        logger.warning("No PDF files were successfully processed")
        # Clean up empty temp directory
        try:
            temp_dir.rmdir()
        except:
            pass
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description="Watermark PDFs and combine them into a single document",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python generate_loc_file.py -s ./Docs
  python generate_loc_file.py -s ./Docs -w "RESERVE POUR LOCATION APPARTEMENT"
  python generate_loc_file.py --source ./Docs --watermark "CONFIDENTIEL - LOCATION"
        """
    )
    
    parser.add_argument(
        "-s", "--source",
        type=Path,
        required=True,
        help="Source folder containing subfolders with PDF files"
    )
    
    parser.add_argument(
        "-w", "--watermark",
        type=str,
        default="DOCUMENT RESERVE A LA LOCATION",
        help="Watermark text to apply to PDFs (default: 'DOCUMENT RESERVE A LA LOCATION')"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting PDF processing...")
    logger.info(f"Source folder: {args.source}")
    logger.info(f"Watermark text: {args.watermark}")
    
    success = process_folder(args.source, args.watermark)
    
    if success:
        logger.info("Processing completed successfully!")
        return 0
    else:
        logger.error("Processing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
