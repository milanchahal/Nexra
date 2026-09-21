# app/services/pdf_service.py
"""
PDF Generation Service for Resumes
Creates professional, ATS-friendly 1-page PDF resumes
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from io import BytesIO
import re
from typing import Optional

class PDFResumeGenerator:
    """Generate professional PDF resumes"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for resume"""
        # Name/Header style
        if 'ResumeName' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeName',
                parent=self.styles['Heading1'],
                fontSize=18,
                fontName='Helvetica-Bold',
                spaceAfter=2,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#1a1a1a')
            ))
        
        # Contact info
        if 'ResumeContact' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeContact',
                parent=self.styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                spaceAfter=8,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#4a4a4a')
            ))
        
        # Section headers
        if 'ResumeSection' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeSection',
                parent=self.styles['Heading2'],
                fontSize=11,
                fontName='Helvetica-Bold',
                spaceBefore=10,
                spaceAfter=4,
                textColor=colors.HexColor('#2563eb'),
                borderWidth=0,
                borderColor=colors.HexColor('#2563eb'),
                borderPadding=0
            ))
        
        # Job title
        if 'ResumeJobTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeJobTitle',
                parent=self.styles['Normal'],
                fontSize=10,
                fontName='Helvetica-Bold',
                spaceAfter=1,
                textColor=colors.HexColor('#1a1a1a')
            ))
        
        # Company/Date line
        if 'ResumeCompany' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeCompany',
                parent=self.styles['Normal'],
                fontSize=9,
                fontName='Helvetica-Oblique',
                spaceAfter=3,
                textColor=colors.HexColor('#4a4a4a')
            ))
        
        # Bullet points
        if 'ResumeBullet' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeBullet',
                parent=self.styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                leftIndent=15,
                spaceAfter=2,
                textColor=colors.HexColor('#333333'),
                leading=12
            ))
        
        # Skills
        if 'ResumeSkills' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeSkills',
                parent=self.styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                spaceAfter=3,
                textColor=colors.HexColor('#333333')
            ))
        
        # Summary
        if 'ResumeSummary' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='ResumeSummary',
                parent=self.styles['Normal'],
                fontSize=9,
                fontName='Helvetica',
                spaceAfter=6,
                textColor=colors.HexColor('#333333'),
                alignment=TA_JUSTIFY,
                leading=12
            ))

    def parse_resume_text(self, resume_text: str) -> dict:
        """Parse resume text into sections"""
        sections = {
            'name': '',
            'contact': '',
            'summary': '',
            'experience': [],
            'education': [],
            'skills': [],
            'projects': [],
            'certifications': []
        }
        
        lines = resume_text.strip().split('\n')
        current_section = None
        
        # First line is usually the name
        if lines:
            sections['name'] = lines[0].strip()
        
        # Second line is usually contact info
        if len(lines) > 1 and ('|' in lines[1] or '@' in lines[1]):
            sections['contact'] = lines[1].strip()
            lines = lines[2:]
        else:
            lines = lines[1:]
        
        section_markers = {
            'summary': ['summary', 'objective', 'profile', 'professional summary'],
            'experience': ['experience', 'work experience', 'employment', 'professional experience'],
            'education': ['education', 'academic'],
            'skills': ['skills', 'technical skills', 'technologies', 'competencies'],
            'projects': ['projects', 'academic project', 'personal projects'],
            'certifications': ['certifications', 'achievements', 'awards', 'honors']
        }
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            line_lower = line.lower()
            found_section = None
            for section, markers in section_markers.items():
                if any(marker in line_lower for marker in markers):
                    found_section = section
                    break
            
            if found_section:
                current_section = found_section
                continue
            
            # Add content to current section
            if current_section == 'summary':
                sections['summary'] += line + ' '
            elif current_section in ['experience', 'education', 'projects', 'certifications']:
                sections[current_section].append(line)
            elif current_section == 'skills':
                sections['skills'].append(line)
        
        return sections

    def generate_pdf(self, resume_text: str, filename: Optional[str] = None) -> BytesIO:
        """Generate PDF from resume text"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.4*inch,
            bottomMargin=0.4*inch
        )
        
        story = []
        sections = self.parse_resume_text(resume_text)
        
        # Name
        if sections['name']:
            story.append(Paragraph(sections['name'], self.styles['ResumeName']))
        
        # Contact
        if sections['contact']:
            story.append(Paragraph(sections['contact'], self.styles['ResumeContact']))
        
        # Horizontal line
        story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb')))
        story.append(Spacer(1, 6))
        
        # Summary
        if sections['summary']:
            story.append(Paragraph("PROFESSIONAL SUMMARY", self.styles['ResumeSection']))
            story.append(Paragraph(sections['summary'].strip(), self.styles['ResumeSummary']))
        
        # Experience
        if sections['experience']:
            story.append(Paragraph("EXPERIENCE", self.styles['ResumeSection']))
            for line in sections['experience']:
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    clean_line = re.sub(r'^[•\-\*]\s*', '', line)
                    story.append(Paragraph(f"• {clean_line}", self.styles['ResumeBullet']))
                elif '|' in line or any(year in line for year in ['2020', '2021', '2022', '2023', '2024', '2025', '2026']):
                    story.append(Paragraph(line, self.styles['ResumeCompany']))
                else:
                    story.append(Paragraph(line, self.styles['ResumeJobTitle']))
        
        # Education
        if sections['education']:
            story.append(Paragraph("EDUCATION", self.styles['ResumeSection']))
            for line in sections['education']:
                if line.startswith('•') or line.startswith('-'):
                    clean_line = re.sub(r'^[•\-]\s*', '', line)
                    story.append(Paragraph(f"• {clean_line}", self.styles['ResumeBullet']))
                else:
                    story.append(Paragraph(line, self.styles['ResumeSkills']))
        
        # Skills
        if sections['skills']:
            story.append(Paragraph("TECHNICAL SKILLS", self.styles['ResumeSection']))
            for line in sections['skills']:
                story.append(Paragraph(line, self.styles['ResumeSkills']))
        
        # Projects
        if sections['projects']:
            story.append(Paragraph("PROJECTS", self.styles['ResumeSection']))
            for line in sections['projects']:
                if line.startswith('•') or line.startswith('-'):
                    clean_line = re.sub(r'^[•\-]\s*', '', line)
                    story.append(Paragraph(f"• {clean_line}", self.styles['ResumeBullet']))
                else:
                    story.append(Paragraph(line, self.styles['ResumeJobTitle']))
        
        # Certifications
        if sections['certifications']:
            story.append(Paragraph("ACHIEVEMENTS & CERTIFICATIONS", self.styles['ResumeSection']))
            for line in sections['certifications']:
                if line.startswith('•') or line.startswith('-'):
                    clean_line = re.sub(r'^[•\-]\s*', '', line)
                    story.append(Paragraph(f"• {clean_line}", self.styles['ResumeBullet']))
                else:
                    story.append(Paragraph(line, self.styles['ResumeSkills']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer

    def generate_simple_pdf(self, resume_text: str) -> BytesIO:
        """Generate a simple, clean PDF from resume text - fallback method"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        story = []
        lines = resume_text.strip().split('\n')
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                story.append(Spacer(1, 6))
                continue
            
            # First line = name (larger)
            if i == 0:
                story.append(Paragraph(line, self.styles['ResumeName']))
            # Contact line
            elif i == 1 and ('|' in line or '@' in line):
                story.append(Paragraph(line, self.styles['ResumeContact']))
                story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb')))
            # Section headers (all caps or contains keywords)
            elif line.isupper() or any(kw in line.upper() for kw in ['EXPERIENCE', 'EDUCATION', 'SKILLS', 'PROJECTS', 'SUMMARY', 'CERTIFICATIONS']):
                story.append(Spacer(1, 8))
                story.append(Paragraph(line, self.styles['ResumeSection']))
            # Bullet points
            elif line.startswith('•') or line.startswith('-') or line.startswith('*'):
                clean_line = re.sub(r'^[•\-\*]\s*', '', line)
                story.append(Paragraph(f"• {clean_line}", self.styles['ResumeBullet']))
            # Regular text
            else:
                story.append(Paragraph(line, self.styles['ResumeSkills']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer


# Create service on-demand to avoid import errors
_pdf_service = None

def get_pdf_service() -> PDFResumeGenerator:
    global _pdf_service
    if _pdf_service is None:
        _pdf_service = PDFResumeGenerator()
    return _pdf_service
