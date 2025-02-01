from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import tempfile
import os
from typing import Dict, Optional

class PresentationGenerator:
    """Class to generate clean, minimal PowerPoint presentations from research paper summaries."""
    
    def __init__(self):
        self.prs = Presentation()
        self.title_slide_layout = self.prs.slide_layouts[0]  # Title slide
        self.content_slide_layout = self.prs.slide_layouts[1]  # Content slide
        
        # Define simpler text styles
        self.title_font_size = Pt(32)  # Reduced from 44
        self.subtitle_font_size = Pt(24)  # Reduced from 32
        self.body_font_size = Pt(18)
        
        # Simple black and white colors
        self.colors = {
            'black': RGBColor(0, 0, 0),
            'white': RGBColor(255, 255, 255)
        }
    
    def _add_title_slide(self, title: str) -> None:
        """Add title slide with minimal styling."""
        slide = self.prs.slides.add_slide(self.title_slide_layout)
        
        # Add title
        title_shape = slide.shapes.title
        title_shape.text = title
        title_frame = title_shape.text_frame
        paragraph = title_frame.paragraphs[0]
        paragraph.font.size = self.title_font_size
        paragraph.font.color.rgb = self.colors['black']
        paragraph.alignment = PP_ALIGN.CENTER
        
        # Add subtitle
        subtitle_shape = slide.placeholders[1]
        subtitle_shape.text = "Research Paper Summary"
        subtitle_frame = subtitle_shape.text_frame
        paragraph = subtitle_frame.paragraphs[0]
        paragraph.font.size = self.subtitle_font_size
        paragraph.font.color.rgb = self.colors['black']
        paragraph.alignment = PP_ALIGN.CENTER
    
    def _add_section_slide(self, title: str, content: str) -> None:
        """Add content slide with clean, minimal design."""
        slide = self.prs.slides.add_slide(self.content_slide_layout)
        
        # Add section title
        title_shape = slide.shapes.title
        title_shape.text = title
        title_frame = title_shape.text_frame
        paragraph = title_frame.paragraphs[0]
        paragraph.font.size = self.subtitle_font_size
        paragraph.font.color.rgb = self.colors['black']
        paragraph.alignment = PP_ALIGN.LEFT
        
        # Add content
        content_shape = slide.placeholders[1]
        content_frame = content_shape.text_frame
        
        # Clear any existing paragraphs
        for _ in range(len(content_frame.paragraphs) - 1):
            p = content_frame.paragraphs[-1]
            tr = p._element
            tr.getparent().remove(tr)
        
        # Add new content
        p = content_frame.paragraphs[0]
        p.text = content
        p.font.size = self.body_font_size
        p.font.color.rgb = self.colors['black']
        p.alignment = PP_ALIGN.LEFT
        
        # Add comfortable spacing
        p.space_before = Pt(6)
        p.space_after = Pt(6)
    
    def generate_presentation(self, sections: Dict[str, str], output_path: Optional[str] = None) -> str:
        """
        Generate clean PowerPoint presentation from paper sections.
        
        Args:
            sections: Dictionary of section titles and their content
            output_path: Optional path to save the presentation
            
        Returns:
            str: Path to the generated presentation
        """
        # Extract title or use default
        title = sections.get('Title', 'Research Paper Summary').strip()
        if not title:
            title = "Research Paper Summary"
        
        # Add title slide
        self._add_title_slide(title)
        
        # Add content slides in standard academic paper order
        section_order = [
            'Abstract',
            'Introduction',
            'Methods',
            'Results',
            'Discussion',
            'Conclusion'
        ]
        
        for section in section_order:
            if section in sections and sections[section].strip():
                self._add_section_slide(section, sections[section])
        
        # Create temporary file if no output path provided
        if output_path is None:
            temp_dir = tempfile.mkdtemp()
            output_path = os.path.join(temp_dir, "research_summary.pptx")
        
        # Save presentation
        self.prs.save(output_path)
        return output_path

def create_ppt(sections: Dict[str, str], output_path: Optional[str] = None) -> str:
    """
    Create simple, clean PowerPoint presentation from paper sections.
    
    Args:
        sections: Dictionary of section titles and their content
        output_path: Optional path to save the presentation
        
    Returns:
        str: Path to the generated presentation
    """
    generator = PresentationGenerator()
    return generator.generate_presentation(sections, output_path)
