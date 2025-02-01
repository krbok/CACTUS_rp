import fitz
import re
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Dict, Optional, Tuple

# Download required NLTK data
nltk.download("punkt", quiet=True)

class HybridSummarizer:
    """A class to handle both extractive and abstractive summarization."""
    
    def __init__(self, extractive_model='en_core_web_sm', abstractive_model='facebook/bart-large-cnn'):
        # Extractive model setup
        try:
            self.nlp = spacy.load(extractive_model)
        except OSError:
            spacy.cli.download(extractive_model)
            self.nlp = spacy.load(extractive_model)
        
        # Abstractive model setup
        self.tokenizer = AutoTokenizer.from_pretrained(abstractive_model)
        self.abstractive_model = AutoModelForSeq2SeqLM.from_pretrained(abstractive_model)
        
        # Define summarization strategy for different sections
        self.summarization_strategy = {
            'Methods': self.extractive_summary,
            'Results': self.extractive_summary,
            'Introduction': self.abstractive_summary,
            'Discussion': self.abstractive_summary,
            'Conclusion': self.abstractive_summary
        }
    
    def extractive_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate extractive summary using TF-IDF."""
        sentences = [sent.text for sent in self.nlp(text).sents]
        
        if not sentences:
            return ""
            
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(sentences)
        
        sentence_scores = tfidf_matrix.sum(axis=1)
        top_sentence_indices = sorted(
            range(len(sentence_scores)),
            key=lambda i: sentence_scores[i, 0],
            reverse=True
        )[:max_sentences]
        
        return ' '.join([sentences[i] for i in sorted(top_sentence_indices)])
    
    def abstractive_summary(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Generate abstractive summary using BART."""
        inputs = self.tokenizer(
            text,
            max_length=1024,
            return_tensors='pt',
            truncation=True
        )
        
        summary_ids = self.abstractive_model.generate(
            inputs['input_ids'],
            num_beams=4,
            max_length=max_length,
            min_length=min_length,
            early_stopping=True
        )
        
        return self.tokenizer.decode(
            summary_ids[0],
            skip_special_tokens=True
        )
    
    def summarize_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Generate summaries for different sections using appropriate strategy."""
        summaries = {}
        for section, content in sections.items():
            if content.strip():
                summarizer = self.summarization_strategy.get(
                    section,
                    self.extractive_summary
                )
                summaries[section] = summarizer(content)
        
        return summaries

class PDFProcessor:
    """A class to handle PDF text extraction and processing."""
    
    def __init__(self):
        """Initialize the processor with required models."""
        self.summarizer = HybridSummarizer()
    
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

def process_pdf(pdf_path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Process a PDF file and return both the original sections and their summaries.
    
    Args:
        pdf_path (str): Path to the PDF file
        
    Returns:
        Tuple[Dict[str, str], Dict[str, str]]: Original sections and their summaries
    """
    try:
        processor = PDFProcessor()
        
        # Extract text from PDF
        doc = fitz.open(pdf_path)
        raw_text = ""
        
        for page in doc:
            raw_text += page.get_text("text") + "\n"
        
        # Clean and process the text
        cleaned_text = processor.clean_text(raw_text)
        
        # Split into sections
        sections = processor.split_into_sections(cleaned_text)
        
        # Generate summaries
        summaries = processor.summarizer.summarize_sections(sections)
        
        return sections, summaries

    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None, None
