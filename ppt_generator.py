from pptx import Presentation

def create_ppt(summary):
    prs = Presentation()
    slide_layout = prs.slide_layouts[1]

    slide = prs.slides.add_slide(slide_layout)
    title = slide.shapes.title
    content = slide.placeholders[1]

    title.text = "Research Paper Summary"
    content.text = summary

    ppt_filename = "output.pptx"
    prs.save(ppt_filename)
    return ppt_filename
