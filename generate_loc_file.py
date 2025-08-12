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
    from reportlab.lib.colors import Color, black, blue
    from reportlab.lib.units import inch
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from PyPDF2 import PdfReader, PdfWriter
    from PyPDF2.generic import AnnotationBuilder
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
    
    
    def create_title_page(self, title_text, output_path):
        """Create a title page PDF."""
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        width, height = A4
        
        # Set title
        can.setFont("Helvetica-Bold", 24)
        title_width = can.stringWidth(title_text, "Helvetica-Bold", 24)
        can.drawString((width - title_width) / 2, height * 0.7, title_text)
        
        # Add date
        from datetime import datetime
        date_text = f"Généré le {datetime.now().strftime('%d/%m/%Y')}"
        can.setFont("Helvetica", 12)
        date_width = can.stringWidth(date_text, "Helvetica", 12)
        can.drawString((width - date_width) / 2, height * 0.3, date_text)
        
        can.save()
        packet.seek(0)
        
        # Save title page
        with open(output_path, 'wb') as f:
            f.write(packet.getvalue())
        
        return output_path
    
    def create_table_of_contents(self, document_info, output_path):
        """Create a table of contents PDF with clickable links."""
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        width, height = A4
        y_position = height - 50
        page_num = 0
        
        # Store link information for later processing
        self._toc_links = []
        self._toc_pages = 0
        
        # Title
        can.setFont("Helvetica-Bold", 18)
        title = "Table des Matières"
        title_width = can.stringWidth(title, "Helvetica-Bold", 18)
        can.drawString((width - title_width) / 2, y_position, title)
        y_position -= 40
        
        # Group by person (folder name)
        current_person = None
        
        for info in document_info:
            folder_name = info['folder']
            doc_name = info['document']
            target_page = info['page']
            
            # Check if we need a new person header
            if current_person != folder_name:
                current_person = folder_name
                y_position -= 20
                
                # Person name (folder name)
                can.setFont("Helvetica-Bold", 14)
                can.setFillColor(black)
                can.drawString(50, y_position, folder_name)
                y_position -= 25
            
            # Document entry
            can.setFont("Helvetica", 11)
            can.setFillColor(blue)
            
            # Create dots for alignment
            doc_text = f"    {doc_name}"
            page_text = f"page {target_page}"
            
            # Calculate positions
            doc_width = can.stringWidth(doc_text, "Helvetica", 11)
            page_width = can.stringWidth(page_text, "Helvetica", 11)
            
            # Draw document name (this will be the clickable area)
            can.drawString(50, y_position, doc_text)
            
            # Draw dots
            dots_start = 50 + doc_width + 10
            dots_end = width - 50 - page_width - 10
            dots_length = dots_end - dots_start
            num_dots = int(dots_length / 4)  # Approximate spacing
            
            can.setFillColor(black)
            dot_text = "." * max(0, num_dots)
            can.drawString(dots_start, y_position, dot_text)
            
            # Draw page number
            can.setFillColor(blue)
            can.drawString(width - 50 - page_width, y_position, page_text)
            
            # Store link information (coordinates are in ReportLab coordinates)
            # We'll convert to PDF coordinates later
            self._toc_links.append({
                'rect': [50, y_position - 2, width - 50, y_position + 13],
                'target_page': target_page,
                'toc_page': page_num  # Current TOC page
            })
            
            y_position -= 18
            
            # Start new page if needed
            if y_position < 100:
                can.showPage()
                page_num += 1
                y_position = height - 50
        
        self._toc_pages = page_num + 1  # Total TOC pages
        
        can.save()
        packet.seek(0)
        
        # Save TOC
        with open(output_path, 'wb') as f:
            f.write(packet.getvalue())
        
        return output_path
    
    def add_links_to_pdf(self, pdf_path, output_path):
        """Add clickable links to the table of contents."""
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        # Copy all pages first
        for page in reader.pages:
            writer.add_page(page)
        
        # Add links to TOC pages (pages 1 to self._toc_pages, since page 0 is title)
        if hasattr(self, '_toc_links') and self._toc_links:
            for link_info in self._toc_links:
                toc_page_idx = 1 + link_info['toc_page']  # +1 because title page is first
                target_page_idx = link_info['target_page'] - 1  # Convert to 0-based indexing
                
                # Make sure the target page exists
                if target_page_idx < len(writer.pages) and toc_page_idx < len(writer.pages):
                    rect = link_info['rect']
                    
                    # Convert ReportLab coordinates to PDF coordinates
                    # ReportLab: (0,0) at bottom-left, PDF: (0,0) at bottom-left but different scale
                    page_height = float(writer.pages[toc_page_idx].mediabox.height)
                    pdf_rect = [
                        rect[0],  # x1
                        page_height - rect[3],  # y1 (flip Y coordinate)
                        rect[2],  # x2  
                        page_height - rect[1]   # y2 (flip Y coordinate)
                    ]
                    
                    try:
                        # Create link annotation
                        annotation = AnnotationBuilder.link(
                            rect=pdf_rect,
                            target_page_index=target_page_idx
                        )
                        
                        # Add annotation to the TOC page
                        writer.add_annotation(page_number=toc_page_idx, annotation=annotation)
                        
                    except Exception as e:
                        logger.warning(f"Could not add link annotation: {e}")
        
        # Write the PDF with links
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    
    def add_bookmarks_to_pdf(self, pdf_path, document_info, output_path):
        """Add PDF bookmarks (signets) to the combined PDF."""
        reader = PdfReader(str(pdf_path))
        writer = PdfWriter()
        
        # Copy all pages
        for page in reader.pages:
            writer.add_page(page)
        
        # Add bookmarks
        # First, add main sections
        title_bookmark = writer.add_outline_item("Page de Titre", 0)
        toc_bookmark = writer.add_outline_item("Table des Matières", 1)
        
        # Group documents by person and add bookmarks
        current_person = None
        person_bookmark = None
        
        for info in document_info:
            folder_name = info['folder']
            doc_name = info['document']
            page_num = info['page'] - 1  # Convert to 0-based indexing
            
            # Create person bookmark if new person
            if current_person != folder_name:
                current_person = folder_name
                person_bookmark = writer.add_outline_item(folder_name, page_num)
            
            # Add document bookmark under the person
            if person_bookmark is not None:
                writer.add_outline_item(doc_name, page_num, person_bookmark)
        
        # Write the PDF with bookmarks
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True

    def combine_pdfs_with_toc(self, pdf_paths, output_path, title_text="Dossier de Location"):
        """Combine multiple PDFs with title page and table of contents."""
        # First, analyze the documents to build TOC info
        document_info = []
        current_page = 1  # Start after title page
        
        # Title page will be page 1
        current_page += 1  # TOC will start at page 2
        
        # Calculate TOC pages needed (estimate)
        total_docs = len(pdf_paths)
        estimated_toc_pages = max(1, (total_docs * 2) // 40)  # Rough estimate
        current_page += estimated_toc_pages
        
        # Analyze each PDF to build document info
        for pdf_path in pdf_paths:
            try:
                reader = PdfReader(str(pdf_path))
                folder_name = pdf_path.name.split('_')[0]  # Extract folder name
                
                # Extract document name (before first -)
                filename = pdf_path.stem
                # Remove folder prefix and _watermarked suffix
                clean_name = filename.replace(f"{folder_name}_", "").replace("_watermarked", "")
                
                # Improve document name extraction
                if '-' in clean_name:
                    doc_name = clean_name.split('-')[0]
                else:
                    doc_name = clean_name
                
                doc_name = doc_name.replace('_', ' ').title()
                document_info.append({
                    'folder': folder_name,
                    'document': doc_name,
                    'page': current_page,
                    'num_pages': len(reader.pages)
                })
                
                current_page += len(reader.pages)
                
            except Exception as e:
                logger.error(f"Error analyzing {pdf_path}: {e}")
        
        # Create title page
        title_temp = output_path.parent / "temp_title.pdf"
        self.create_title_page(title_text, title_temp)
        
        # Create table of contents
        toc_temp = output_path.parent / "temp_toc.pdf"
        self.create_table_of_contents(document_info, toc_temp)
        
        # Combine everything
        writer = PdfWriter()
        
        # Add title page
        try:
            title_reader = PdfReader(str(title_temp))
            for page in title_reader.pages:
                writer.add_page(page)
            logger.info("Added title page to combined document")
        except Exception as e:
            logger.error(f"Error adding title page: {e}")
        
        # Add table of contents
        try:
            toc_reader = PdfReader(str(toc_temp))
            for page in toc_reader.pages:
                writer.add_page(page)
            logger.info("Added table of contents to combined document")
        except Exception as e:
            logger.error(f"Error adding table of contents: {e}")
        
        # Add all document PDFs
        for pdf_path in pdf_paths:
            try:
                reader = PdfReader(str(pdf_path))
                for page in reader.pages:
                    writer.add_page(page)
                logger.info(f"Added {pdf_path.name} to combined document")
            except Exception as e:
                logger.error(f"Error adding {pdf_path} to combined document: {e}")
        
        # Write final combined PDF (without links first)
        temp_combined = output_path.parent / "temp_combined.pdf"
        try:
            with open(temp_combined, 'wb') as output_file:
                writer.write(output_file)
            logger.info(f"Combined PDF (without links) saved temporarily")
            
            # Now add clickable links to the combined PDF
            if hasattr(self, '_toc_links') and self._toc_links:
                logger.info("Adding clickable links to table of contents...")
                temp_with_links = output_path.parent / "temp_with_links.pdf"
                self.add_links_to_pdf(temp_combined, temp_with_links)
                
                # Now add bookmarks (signets) to the PDF
                logger.info("Adding bookmarks (signets) to PDF...")
                self.add_bookmarks_to_pdf(temp_with_links, document_info, output_path)
                logger.info(f"Combined PDF with clickable TOC and bookmarks saved: {output_path}")
                
                # Clean up the intermediate file
                try:
                    temp_with_links.unlink()
                except Exception as e:
                    logger.warning(f"Could not clean up intermediate file: {e}")
                    
            else:
                # If no links, just add bookmarks
                logger.info("Adding bookmarks (signets) to PDF...")
                self.add_bookmarks_to_pdf(temp_combined, document_info, output_path)
                logger.info(f"Combined PDF with bookmarks saved: {output_path}")
            
            # Clean up temporary files
            try:
                title_temp.unlink()
                toc_temp.unlink()
                if temp_combined.exists():
                    temp_combined.unlink()
            except Exception as e:
                logger.warning(f"Could not clean up temporary files: {e}")
            
            return True
        except Exception as e:
            logger.error(f"Error saving combined PDF: {e}")
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

def process_folder(source_folder, watermark_text="DOCUMENT RESERVE A LA LOCATION", title_text="Dossier de Location"):
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
        
        # Combine all watermarked PDFs with title page and TOC
        combined_output = source_path / f"Dossier_Location_Complete_{watermark_text.replace(' ', '_')}.pdf"
        if watermarker.combine_pdfs_with_toc(unique_watermarked_pdfs, combined_output, title_text):
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
  python generate_loc_file.py -s ./Docs -t "Dossier Famille Dupont"
  python generate_loc_file.py -s ./Docs -w "CONFIDENTIEL" -t "Documents Location Appartement"
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
    
    parser.add_argument(
        "-t", "--title",
        type=str,
        default="Dossier de Location",
        help="Title for the document (default: 'Dossier de Location')"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting PDF processing...")
    logger.info(f"Source folder: {args.source}")
    logger.info(f"Watermark text: {args.watermark}")
    logger.info(f"Document title: {args.title}")
    
    success = process_folder(args.source, args.watermark, args.title)
    
    if success:
        logger.info("Processing completed successfully!")
        return 0
    else:
        logger.error("Processing failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
