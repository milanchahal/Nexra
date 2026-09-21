# app/services/pdf_editor.py
"""
PDF In-Place Editor Service using PyMuPDF
Applies text replacements while preserving layout, fonts, and links
"""
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from io import BytesIO
import re


@dataclass
class Replacement:
    """Represents a text replacement to apply"""
    original: str
    replacement: str
    context: str = ""  # The line/sentence for context
    max_occurrences: int = 1
    applied: bool = False
    

class PDFEditor:
    """
    Edit PDFs in-place while preserving layout, fonts, and formatting.
    Uses the "cover and redraw" technique for text replacement.
    """
    
    def __init__(self, pdf_source):
        """
        Initialize with PDF source (file path, bytes, or BytesIO)
        """
        if isinstance(pdf_source, bytes):
            self.doc = fitz.open(stream=pdf_source, filetype="pdf")
        elif isinstance(pdf_source, BytesIO):
            pdf_source.seek(0)
            self.doc = fitz.open(stream=pdf_source.read(), filetype="pdf")
        else:
            self.doc = fitz.open(pdf_source)
        
        self.original_page_count = len(self.doc)
        self.replacements_applied = []
    
    def close(self):
        """Close the document"""
        self.doc.close()
    
    def apply_replacements(self, replacements: List[Replacement]) -> BytesIO:
        """
        Apply all replacements to the PDF and return new PDF as BytesIO.
        Uses redaction technique: cover old text with white, insert new text.
        """
        for replacement in replacements:
            self._apply_single_replacement(replacement)
        
        # Save to BytesIO
        output = BytesIO()
        self.doc.save(output, garbage=4, deflate=True)
        output.seek(0)
        
        return output
    
    def apply_replacements_simple(self, replacements: List[Dict[str, str]]) -> BytesIO:
        """
        Simplified interface: apply replacements from dict list
        Each dict should have 'original' and 'replacement' keys
        """
        replacement_objects = [
            Replacement(
                original=r.get("original", ""),
                replacement=r.get("replacement", ""),
                context=r.get("context", ""),
                max_occurrences=r.get("max_occurrences", 1)
            )
            for r in replacements
        ]
        return self.apply_replacements(replacement_objects)
    
    def _apply_single_replacement(self, replacement: Replacement) -> int:
        """
        Apply a single replacement across all pages.
        Returns number of occurrences replaced.
        """
        count = 0
        original = replacement.original
        new_text = replacement.replacement
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            
            # Find all occurrences of the original text
            text_instances = page.search_for(original)
            
            for rect in text_instances:
                if count >= replacement.max_occurrences:
                    break
                
                # Get the span info at this location to match font/size
                span_info = self._get_span_at_rect(page, rect)
                font_name = span_info.get("font", "helv")
                font_size = span_info.get("size", 11)
                font_color = span_info.get("color", (0, 0, 0))
                
                # Cover the old text with a white rectangle
                # Expand rect slightly to ensure full coverage
                cover_rect = fitz.Rect(
                    rect.x0 - 1,
                    rect.y0 - 1,
                    rect.x1 + 1,
                    rect.y1 + 1
                )
                
                # Draw white rectangle to cover old text
                shape = page.new_shape()
                shape.draw_rect(cover_rect)
                shape.finish(color=None, fill=(1, 1, 1))  # White fill
                shape.commit()
                
                # Insert new text at the same position
                # Calculate text insertion point (baseline)
                text_point = fitz.Point(rect.x0, rect.y1 - 2)  # Adjust for baseline
                
                # Try to use a similar font
                fontname = self._get_pdf_font(font_name)
                
                # Insert the replacement text
                page.insert_text(
                    text_point,
                    new_text,
                    fontsize=font_size,
                    fontname=fontname,
                    color=font_color if isinstance(font_color, tuple) else (0, 0, 0)
                )
                
                count += 1
                self.replacements_applied.append({
                    "page": page_num,
                    "original": original,
                    "replacement": new_text,
                    "rect": tuple(rect)
                })
        
        replacement.applied = count > 0
        return count
    
    def _get_span_at_rect(self, page, rect: fitz.Rect) -> Dict[str, Any]:
        """
        Get the text span information at a given rectangle position.
        Returns font, size, and color info.
        """
        blocks = page.get_text("dict")["blocks"]
        
        for block in blocks:
            if block.get("type") != 0:
                continue
            
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    span_rect = fitz.Rect(span["bbox"])
                    
                    # Check if rectangles overlap
                    if rect.intersects(span_rect):
                        # Convert color from int to RGB tuple
                        color_int = span.get("color", 0)
                        color = self._int_to_rgb(color_int)
                        
                        return {
                            "font": span.get("font", "helv"),
                            "size": span.get("size", 11),
                            "color": color,
                            "flags": span.get("flags", 0)
                        }
        
        # Default fallback
        return {"font": "helv", "size": 11, "color": (0, 0, 0), "flags": 0}
    
    def _int_to_rgb(self, color_int: int) -> Tuple[float, float, float]:
        """Convert integer color to RGB tuple (0-1 range)"""
        if color_int == 0:
            return (0, 0, 0)  # Black
        
        r = ((color_int >> 16) & 0xFF) / 255.0
        g = ((color_int >> 8) & 0xFF) / 255.0
        b = (color_int & 0xFF) / 255.0
        
        return (r, g, b)
    
    def _get_pdf_font(self, font_name: str) -> str:
        """
        Map font name to PDF base font.
        PyMuPDF has limited built-in fonts, so we map to closest match.
        """
        font_lower = font_name.lower()
        
        # Map common fonts to PDF base fonts
        if "arial" in font_lower or "helvetica" in font_lower or "sans" in font_lower:
            return "helv"
        elif "times" in font_lower or "serif" in font_lower:
            return "tiro"
        elif "courier" in font_lower or "mono" in font_lower or "code" in font_lower:
            return "cour"
        elif "bold" in font_lower:
            return "hebo"  # Helvetica Bold
        else:
            return "helv"  # Default to Helvetica
    
    def validate_output(self) -> Dict[str, Any]:
        """
        Validate the edited PDF.
        Returns validation results including page count check.
        """
        new_page_count = len(self.doc)
        
        return {
            "valid": new_page_count == self.original_page_count,
            "original_pages": self.original_page_count,
            "new_pages": new_page_count,
            "page_count_unchanged": new_page_count == self.original_page_count,
            "replacements_applied": len(self.replacements_applied),
            "details": self.replacements_applied
        }
    
    def get_modified_pdf(self) -> BytesIO:
        """
        Get the current state of the PDF as BytesIO
        """
        output = BytesIO()
        self.doc.save(output, garbage=4, deflate=True)
        output.seek(0)
        return output
    
    def preview_text_diff(self, replacements: List[Dict[str, str]]) -> Dict[str, str]:
        """
        Generate a text diff preview without modifying the PDF.
        Returns original and modified text for comparison.
        """
        original_text = ""
        modified_text = ""
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            page_text = page.get_text("text")
            original_text += page_text
            
            # Apply replacements to text
            modified_page_text = page_text
            for r in replacements:
                original = r.get("original", "")
                replacement = r.get("replacement", "")
                max_occ = r.get("max_occurrences", 1)
                
                # Replace up to max_occurrences
                count = 0
                while original in modified_page_text and count < max_occ:
                    modified_page_text = modified_page_text.replace(original, replacement, 1)
                    count += 1
            
            modified_text += modified_page_text
        
        return {
            "original": original_text,
            "modified": modified_text
        }


def apply_replacements_to_pdf(
    pdf_bytes: bytes, 
    replacements: List[Dict[str, str]]
) -> Tuple[BytesIO, Dict[str, Any]]:
    """
    Convenience function to apply replacements to PDF bytes.
    Returns (modified_pdf_bytes, validation_result)
    """
    editor = PDFEditor(pdf_bytes)
    
    try:
        modified_pdf = editor.apply_replacements_simple(replacements)
        validation = editor.validate_output()
        return modified_pdf, validation
    finally:
        editor.close()


def preview_changes(
    pdf_bytes: bytes, 
    replacements: List[Dict[str, str]]
) -> Dict[str, str]:
    """
    Preview text changes without modifying PDF.
    Returns original and modified text for diff display.
    """
    editor = PDFEditor(pdf_bytes)
    
    try:
        return editor.preview_text_diff(replacements)
    finally:
        editor.close()
