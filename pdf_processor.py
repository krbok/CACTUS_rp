import fitz
import re
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from typing import Dict, Optional

# Download required NLTK data
nltk.download("punkt", quiet=True)

class PDFProcessor:
    """A class to handle PDF text extraction and processing."""
    
    def __init__(self):
        """Initialize the processor with required models."""
        try:
            self.nlp = spacy.load('en_core_web_sm')
        except OSError:
            # If model not found, download it
            spacy.cli.download('en_core_web_sm')
            self.nlp = spacy.load('en_core_web_sm')
    
    def clean_text(self, text: str) -> str:
        """Clean extracted text by removing metadata and formatting."""
        # Remove journal metadata
        text = re.sub(r'eISSN:\s*\d+|pISSN:\s*\d+|Impact Factor.*?\d+\.\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Volume:\s*\d+\s*Issue:\s*\d+', '', text, flags=re.IGNORECASE)
        text = re.sub(r'ISO\s*\d{4,}', '', text, flags=re.IGNORECASE)
        
        # Remove citations
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\(.*?\d{4}.*?\)', '', text)
        
        # Remove figure and table references
        text = re.sub(r'Fig\s*\d+|Table\s*\d+', '', text)
        text = re.sub(r'References|Bibliography', '', text, flags=re.IGNORECASE)
        
        # Clean special characters while preserving essential punctuation
        text = re.sub(r'[^a-zA-Z0-9.,!?;:()\s]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def split_into_sections(self, text: str) -> Dict[str, str]:
        """Split text into logical sections based on common research paper headers."""
        section_headers = {
            "Title": ["title"],
            "Abstract": ["abstract"],
            "Introduction": ["introduction"],
            "Methods": ["methods", "methodology", "materials & methods"],
            "Results": ["results", "findings"],
            "Discussion": ["discussion", "analysis"],
            "Conclusion": ["conclusion", "summary", "final thoughts"]
        }
        
        sections = {key: "" for key in section_headers}
        sentences = sent_tokenize(text)
        current_section = "Title"
        
        for sentence in sentences:
            for section, keywords in section_headers.items():
                if any(keyword in sentence.lower() for keyword in keywords):
                    current_section = section
                    break
            sections[current_section] += sentence + " "
        
        return sections
    
    def extract_key_information(self, text: str) -> Dict[str, str]:
        """Extract key information using spaCy NLP."""
        doc = self.nlp(text)
        
        # Extract entities
        entities = {ent.label_: ent.text for ent in doc.ents}
        
        # Extract key sentences using basic frequency
        vectorizer = TfidfVectorizer(max_features=100)
        tfidf_matrix = vectorizer.fit_transform([sent.text for sent in doc.sents])
        
        important_words = dict(zip(
            vectorizer.get_feature_names_out(),
            tfidf_matrix.sum(axis=0).A1
        ))
        
        return {
            "entities": entities,
            "key_terms": {k: v for k, v in sorted(
                important_words.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]}
        }

def extract_text_from_pdf(pdf_path: str) -> Optional[str]:
    """
    Extract and process text from a PDF file.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        str: Processed text from the PDF, or None if extraction fails
    """
    try:
        processor = PDFProcessor()
        
        # Open and extract text from PDF
        doc = fitz.open(pdf_path)
        raw_text = ""
        
        for page in doc:
            raw_text += page.get_text("text") + "\n"
        
        # Clean and process the text
        cleaned_text = processor.clean_text(raw_text)
        
        # Split into sections
        sections = processor.split_into_sections(cleaned_text)
        
        # Extract key information
        key_info = processor.extract_key_information(cleaned_text)
        
        # Combine all processed text
        final_text = "\n\n".join([
            f"{section}:\n{content}"
            for section, content in sections.items()
            if content.strip()
        ])
        
        return final_text

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

if __name__ == "__main__":
    # Test the processor
    test_pdf = "sample.pdf"
    try:
        result = extract_text_from_pdf(test_pdf)
        if result:
            print("PDF processed successfully!")
            print(result[:500] + "...")
        else:
            print("Failed to process PDF")
    except Exception as e:
        print(f"Error during testing: {str(e)}")
