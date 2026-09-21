# app/services/pdf_extractor.py
"""
PDF Text Extraction Service using PyMuPDF
Extracts text spans with bounding boxes, fonts, colors, and links
"""
import fitz  # PyMuPDF
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from io import BytesIO
import re


@dataclass
class TextSpan:
    """Represents a text span with position and formatting"""
    text: str
    page: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    font: str
    size: float
    color: int
    flags: int  # bold, italic, etc.
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LinkInfo:
    """Represents a hyperlink in the PDF"""
    page: int
    bbox: Tuple[float, float, float, float]
    uri: str
    link_type: str  # 'uri', 'goto', etc.


class PDFExtractor:
    """Extract structured text data from PDFs using PyMuPDF"""
    
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
    
    def close(self):
        """Close the document"""
        self.doc.close()
    
    def get_page_count(self) -> int:
        """Get number of pages"""
        return len(self.doc)
    
    def extract_all_spans(self) -> List[TextSpan]:
        """
        Extract all text spans from all pages with formatting info
        """
        all_spans = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            
            for block in blocks:
                if block.get("type") != 0:  # Skip non-text blocks (images)
                    continue
                    
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span.get("text", "").strip()
                        if not text:
                            continue
                            
                        all_spans.append(TextSpan(
                            text=span["text"],
                            page=page_num,
                            bbox=tuple(span["bbox"]),
                            font=span.get("font", ""),
                            size=span.get("size", 11),
                            color=span.get("color", 0),
                            flags=span.get("flags", 0)
                        ))
        
        return all_spans
    
    def extract_spans_by_page(self) -> Dict[int, List[TextSpan]]:
        """
        Extract spans organized by page number
        """
        spans_by_page = {}
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            blocks = page.get_text("dict", flags=fitz.TEXT_PRESERVE_WHITESPACE)["blocks"]
            
            page_spans = []
            for block in blocks:
                if block.get("type") != 0:
                    continue
                    
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        if not span.get("text", "").strip():
                            continue
                            
                        page_spans.append(TextSpan(
                            text=span["text"],
                            page=page_num,
                            bbox=tuple(span["bbox"]),
                            font=span.get("font", ""),
                            size=span.get("size", 11),
                            color=span.get("color", 0),
                            flags=span.get("flags", 0)
                        ))
            
            spans_by_page[page_num] = page_spans
        
        return spans_by_page
    
    def extract_links(self) -> List[LinkInfo]:
        """
        Extract all hyperlinks from the PDF
        """
        links = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            
            for link in page.get_links():
                link_type = link.get("kind", 0)
                uri = link.get("uri", "")
                
                # Map link kinds to types
                if link_type == fitz.LINK_URI:
                    link_type_str = "uri"
                elif link_type == fitz.LINK_GOTO:
                    link_type_str = "goto"
                else:
                    link_type_str = "other"
                
                if uri or link_type_str == "goto":
                    links.append(LinkInfo(
                        page=page_num,
                        bbox=tuple(link.get("from", (0, 0, 0, 0))),
                        uri=uri,
                        link_type=link_type_str
                    ))
        
        return links
    
    def get_full_text(self) -> str:
        """
        Extract plain text from all pages
        """
        text_parts = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            text_parts.append(page.get_text("text"))
        
        return "\n".join(text_parts)
    
    def get_text_by_page(self) -> Dict[int, str]:
        """
        Get plain text organized by page
        """
        return {
            page_num: self.doc[page_num].get_text("text")
            for page_num in range(len(self.doc))
        }
    
    def find_text_positions(self, search_text: str, case_sensitive: bool = False) -> List[Dict[str, Any]]:
        """
        Find all occurrences of text and return their positions
        """
        results = []
        
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            
            # Search for text instances
            text_instances = page.search_for(search_text)
            
            for rect in text_instances:
                results.append({
                    "page": page_num,
                    "bbox": tuple(rect),
                    "text": search_text
                })
        
        return results
    
    def get_spans_containing_text(self, search_text: str) -> List[TextSpan]:
        """
        Find spans that contain the search text
        """
        matching_spans = []
        all_spans = self.extract_all_spans()
        
        search_lower = search_text.lower()
        
        for span in all_spans:
            if search_lower in span.text.lower():
                matching_spans.append(span)
        
        return matching_spans
    
    def extract_sections(self) -> Dict[str, List[str]]:
        """
        Try to identify resume sections (Skills, Experience, Education, etc.)
        """
        section_markers = {
            'summary': ['summary', 'objective', 'profile', 'about'],
            'experience': ['experience', 'work experience', 'employment', 'professional experience'],
            'education': ['education', 'academic', 'qualifications'],
            'skills': ['skills', 'technical skills', 'technologies', 'competencies'],
            'projects': ['projects', 'academic projects', 'personal projects'],
            'certifications': ['certifications', 'certificates', 'achievements', 'awards']
        }
        
        full_text = self.get_full_text()
        lines = full_text.split('\n')
        
        sections = {key: [] for key in section_markers.keys()}
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this line is a section header
            line_lower = line.lower()
            found_section = None
            
            for section, markers in section_markers.items():
                if any(marker in line_lower for marker in markers):
                    found_section = section
                    break
            
            if found_section:
                current_section = found_section
                continue
            
            # Add line to current section
            if current_section and line:
                sections[current_section].append(line)
        
        return sections


def extract_resume_data(pdf_bytes: bytes) -> Dict[str, Any]:
    """
    Convenience function to extract all resume data from PDF bytes
    """
    extractor = PDFExtractor(pdf_bytes)
    
    try:
        data = {
            "page_count": extractor.get_page_count(),
            "full_text": extractor.get_full_text(),
            "spans": [span.to_dict() for span in extractor.extract_all_spans()],
            "links": [asdict(link) for link in extractor.extract_links()],
            "sections": extractor.extract_sections()
        }
        return data
    finally:
        extractor.close()


def get_extractor(pdf_source) -> PDFExtractor:
    """Factory function to create PDFExtractor"""
    return PDFExtractor(pdf_source)
