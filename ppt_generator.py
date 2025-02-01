from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
import re
from typing import Dict, Optional

class PresentationGenerator:
    def __init__(self):
        self.prs = Presentation()
        self.set_slide_dimensions(13.333, 7.5)  # 16:9 aspect ratio
        
        # Define consistent formatting
        self.title_font = "Calibri"
        self.body_font = "Calibri"
        self.title_size = Pt(44)
        self.subtitle_size = Pt(32)
        self.body_size = Pt(18)
        
        # Define colors
        self.primary_color = RGBColor(0, 255, 157)  # Cyber green
        self.secondary_color = RGBColor(0, 204, 255)  # Cyber blue
        self.text_color = RGBColor(224, 224, 255)  # Light purple
    
    def set_slide_dimensions(self, width: float, height: float):
        """Set presentation dimensions in inches"""
        self.prs.slide_width = Inches(width)
        self.prs.slide_height = Inches(height)
    
    def create_title_slide(self, title: str) -> None:
        """Create an attractive title slide"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[0])
        
        # Add title
        title_shape = slide.shapes.title
        title_shape.text = title
        title_shape.text_frame.paragraphs[0].alignment = PP_ALIGN.CENTER
        
        # Format title
        title_frame = title_shape.text_frame.paragraphs[0]
        title_frame.font.name = self.title_font
        title_frame.font.size = self.title_size
        title_frame.font.color.rgb = self.primary_color
        
        # Add subtitle
        subtitle = slide.placeholders[1]
        subtitle.text = "Research Paper Analysis"
        subtitle_frame = subtitle.text_frame.paragraphs[0]
        subtitle_frame.font.name = self.body_font
        subtitle_frame.font.size = self.subtitle_size
        subtitle_frame.font.color.rgb = self.secondary_color
    
    def create_section_slide(self, title: str, content: str) -> None:
        """Create a slide for a specific section"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[1])
        
        # Add and format title
        title_shape = slide.shapes.title
        title_shape.text = title
        title_frame = title_shape.text_frame.paragraphs[0]
        title_frame.font.name = self.title_font
        title_frame.font.size = self.subtitle_size
        title_frame.font.color.rgb = self.primary_color
        
        # Add and format content
        content_shape = slide.placeholders[1]
        content_frame = content_shape.text_frame
        
        # Split content into bullet points if it's too long
        sentences = re.split(r'(?<=[.!?])\s+', content)
        
        for i, sentence in enumerate(sentences):
            if i == 0:
                paragraph = content_frame.paragraphs[0]
            else:
                paragraph = content_frame.add_paragraph()
            
            paragraph.text = sentence
            paragraph.font.name = self.body_font
            paragraph.font.size = self.body_size
            paragraph.font.color.rgb = self.text_color
    
    def add_summary_slide(self, key_points: Dict[str, float]) -> None:
        """Add a summary slide with key points"""
        slide = self.prs.slides.add_slide(self.prs.slide_layouts[1])
        
        title_shape = slide.shapes.title
        title_shape.text = "Key Takeaways"
        title_frame = title_shape.text_frame.paragraphs[0]
        title_frame.font.name = self.title_font
        title_frame.font.size = self.subtitle_size
        title_frame.font.color.rgb = self.primary_color
        
        content_shape = slide.placeholders[1]
        content_frame = content_shape.text_frame
        
        for point, score in list(key_points.items())[:5]:  # Top 5 key points
            paragraph = content_frame.add_paragraph()
            paragraph.text = f"• {point}"
            paragraph.font.name = self.body_font
            paragraph.font.size = self.body_size
            paragraph.font.color.rgb = self.text_color

def create_ppt(summary: str) -> Optional[str]:
    """
    Create a PowerPoint presentation from the research paper summary
    
    Args:
        summary (str): Processed text from the PDF processor
        
    Returns:
        str: Path to the generated PowerPoint file
    """
    try:
        # Initialize presentation generator
        generator = PresentationGenerator()
        
        # Extract title from summary (first line of Title section)
        title_match = re.search(r"Title:\s*([^\n]+)", summary)
        title = title_match.group(1) if title_match else "Research Paper Summary"
        
        # Create title slide
        generator.create_title_slide(title)
        
        # Process each section
        sections = {
            "Abstract": "Research Overview",
            "Introduction": "Background",
            "Methods": "Methodology",
            "Results": "Key Findings",
            "Discussion": "Analysis",
            "Conclusion": "Conclusions"
        }
        
        for section_marker, slide_title in sections.items():
            section_match = re.search(f"{section_marker}:\s*([^\n]+(?:\n[^\n]+)*)", summary)
            if section_match:
                content = section_match.group(1).strip()
                if content:
                    generator.create_section_slide(slide_title, content)
        
        # Save the presentation
        output_filename = "output.pptx"
        generator.prs.save(output_filename)
        return output_filename
    
    except Exception as e:
        print(f"Error generating presentation: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the generator
    test_summary = """
    Title: Analysis of Advanced Machine Learning Techniques
    Abstract: This paper presents a comprehensive review...
    Introduction: Machine learning has revolutionized...
    Methods: We employed various techniques...
    Results: Our findings indicate...
    Discussion: The results suggest...
    Conclusion: We have demonstrated...
    """
    result = create_ppt(test_summary)
    if result:
        print(f"Presentation generated successfully: {result}")
    else:
        print("Failed to generate presentation")
