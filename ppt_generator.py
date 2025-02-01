from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
import re
from typing import Dict, Optional, List

def format_bullet_points(text: str) -> List[str]:
    """Convert text into well-formatted bullet points"""
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    # Remove any empty strings and clean up
    return [s.strip() for s in sentences if s.strip()]

def create_ppt(summary: str) -> Optional[str]:
    """
    Create a structured PowerPoint presentation from research paper summary
    
    Args:
        summary (str): Processed text containing different sections
    Returns:
        str: Path to the generated PowerPoint file
    """
    try:
        # Initialize presentation
        prs = Presentation()
        
        # Set 16:9 aspect ratio
        prs.slide_width = Inches(13.333)
        prs.slide_height = Inches(7.5)

        # Title Slide
        title_slide = prs.slides.add_slide(prs.slide_layouts[0])
        title = title_slide.shapes.title
        subtitle = title_slide.placeholders[1]
        
        title.text = "Research Paper Analysis"
        title.text_frame.paragraphs[0].font.size = Pt(44)
        
        subtitle.text = "Summary and Key Findings"
        subtitle.text_frame.paragraphs[0].font.size = Pt(32)

        # Abstract Slide
        if "Abstract:" in summary:
            abstract_slide = prs.slides.add_slide(prs.slide_layouts[1])
            title = abstract_slide.shapes.title
            content = abstract_slide.placeholders[1]
            
            title.text = "Abstract"
            abstract_text = re.search(r"Abstract:(.*?)(?=\w+:|\Z)", summary, re.DOTALL)
            if abstract_text:
                content.text = abstract_text.group(1).strip()

        # Introduction Slides
        if "Introduction:" in summary:
            intro_text = re.search(r"Introduction:(.*?)(?=\w+:|\Z)", summary, re.DOTALL)
            if intro_text:
                # Main Introduction
                intro_slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = intro_slide.shapes.title
                content = intro_slide.placeholders[1]
                
                title.text = "Introduction"
                bullet_points = format_bullet_points(intro_text.group(1))
                
                # Split into multiple slides if needed
                for i in range(0, len(bullet_points), 5):
                    if i > 0:
                        intro_slide = prs.slides.add_slide(prs.slide_layouts[1])
                        title = intro_slide.shapes.title
                        content = intro_slide.placeholders[1]
                        title.text = "Introduction (continued)"
                    
                    text_frame = content.text_frame
                    text_frame.clear()
                    
                    for point in bullet_points[i:i+5]:
                        p = text_frame.add_paragraph()
                        p.text = point
                        p.level = 0
                        p.font.size = Pt(18)

        # Methodology Section
        if "Methods:" in summary:
            methods_text = re.search(r"Methods:(.*?)(?=\w+:|\Z)", summary, re.DOTALL)
            if methods_text:
                methods_slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = methods_slide.shapes.title
                content = methods_slide.placeholders[1]
                
                title.text = "Methodology"
                bullet_points = format_bullet_points(methods_text.group(1))
                
                text_frame = content.text_frame
                text_frame.clear()
                
                for point in bullet_points:
                    p = text_frame.add_paragraph()
                    p.text = point
                    p.level = 0
                    p.font.size = Pt(18)

        # Results Section
        if "Results:" in summary:
            results_text = re.search(r"Results:(.*?)(?=\w+:|\Z)", summary, re.DOTALL)
            if results_text:
                results_slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = results_slide.shapes.title
                content = results_slide.placeholders[1]
                
                title.text = "Key Findings"
                bullet_points = format_bullet_points(results_text.group(1))
                
                text_frame = content.text_frame
                text_frame.clear()
                
                for point in bullet_points:
                    p = text_frame.add_paragraph()
                    p.text = point
                    p.level = 0
                    p.font.size = Pt(18)

        # Discussion Section
        if "Discussion:" in summary:
            discussion_text = re.search(r"Discussion:(.*?)(?=\w+:|\Z)", summary, re.DOTALL)
            if discussion_text:
                discussion_slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = discussion_slide.shapes.title
                content = discussion_slide.placeholders[1]
                
                title.text = "Discussion"
                bullet_points = format_bullet_points(discussion_text.group(1))
                
                text_frame = content.text_frame
                text_frame.clear()
                
                for point in bullet_points:
                    p = text_frame.add_paragraph()
                    p.text = point
                    p.level = 0
                    p.font.size = Pt(18)

        # Conclusion Section
        if "Conclusion:" in summary:
            conclusion_text = re.search(r"Conclusion:(.*?)(?=\w+:|\Z)", summary, re.DOTALL)
            if conclusion_text:
                conclusion_slide = prs.slides.add_slide(prs.slide_layouts[1])
                title = conclusion_slide.shapes.title
                content = conclusion_slide.placeholders[1]
                
                title.text = "Conclusions"
                bullet_points = format_bullet_points(conclusion_text.group(1))
                
                text_frame = content.text_frame
                text_frame.clear()
                
                for point in bullet_points:
                    p = text_frame.add_paragraph()
                    p.text = point
                    p.level = 0
                    p.font.size = Pt(18)

        # Save presentation
        output_filename = "output.pptx"
        prs.save(output_filename)
        return output_filename

    except Exception as e:
        print(f"Error generating presentation: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the generator
    test_summary = """
    Title: Research Analysis
    Abstract: This is the abstract section with key points.
    Introduction: First introduction point. Second introduction point. Third point.
    Methods: First methodology point. Second methodology point.
    Results: First result. Second result. Third result.
    Discussion: First discussion point. Second discussion point.
    Conclusion: First conclusion. Second conclusion.
    """
    result = create_ppt(test_summary)
    print(f"Presentation generated: {result}")
