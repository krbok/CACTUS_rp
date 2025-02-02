import fitz
import re
import spacy
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from typing import Dict, Optional, Tuple
import logging
import torch

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.download("punkt", quiet=True, download_dir="/tmp")
    nltk.data.path.append("/tmp")
except Exception as e:
    logger.warning(f"NLTK download warning: {e}")

class HybridSummarizer:
    """A class to handle both extractive and abstractive summarization."""
    
    def __init__(self, extractive_model='en_core_web_sm', abstractive_model='facebook/bart-large-cnn'):
        # Extractive model setup
        try:
            self.nlp = spacy.load(extractive_model)
        except OSError:
            spacy.cli.download(extractive_model)
            self.nlp = spacy.load(extractive_model)
        
        # Abstractive model setup with error handling
        try:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
            logger.info(f"Using device: {self.device}")
            
            self.tokenizer = AutoTokenizer.from_pretrained(abstractive_model)
            self.abstractive_model = AutoModelForSeq2SeqLM.from_pretrained(abstractive_model).to(self.device)
        except Exception as e:
            logger.error(f"Error loading abstractive model: {e}")
            self.tokenizer = None
            self.abstractive_model = None
        
        # Define summarization strategy
        self.summarization_strategy = {
            'Methods': self.extractive_summary,
            'Results': self.extractive_summary,
            'Introduction': self.fallback_summary,
            'Discussion': self.fallback_summary,
            'Conclusion': self.fallback_summary
        }
    
    def extractive_summary(self, text: str, max_sentences: int = 3) -> str:
        """Generate extractive summary using TF-IDF."""
        try:
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
        except Exception as e:
            logger.error(f"Error in extractive summary: {e}")
            return self.fallback_summary(text)
    
    def abstractive_summary(self, text: str, max_length: int = 150, min_length: int = 50) -> str:
        """Generate abstractive summary using BART."""
        try:
            if not self.abstractive_model or not self.tokenizer:
                return self.fallback_summary(text)
            
            inputs = self.tokenizer(
                text,
                max_length=1024,
                return_tensors='pt',
                truncation=True
            ).to(self.device)
            
            with torch.no_grad():
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
        except Exception as e:
            logger.error(f"Error in abstractive summary: {e}")
            return self.fallback_summary(text)
    
    def fallback_summary(self, text: str) -> str:
        """Fallback method when other summarization methods fail."""
        try:
            sentences = sent_tokenize(text)
            return ' '.join(sentences[:3])
        except Exception as e:
            logger.error(f"Error in fallback summary: {e}")
            return text[:500] + "..."
    
    def summarize_sections(self, sections: Dict[str, str]) -> Dict[str, str]:
        """Generate summaries for different sections using appropriate strategy."""
        summaries = {}
        for section, content in sections.items():
            if content.strip():
                summarizer = self.summarization_strategy.get(
                    section,
                    self.fallback_summary
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
        try:
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
        except Exception as e:
            logger.error(f"Error in clean_text: {e}")
            return text
    
    def split_into_sections(self, text: str) -> Dict[str, str]:
        """Split text into logical sections based on common research paper headers."""
        try:
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
        except Exception as e:
            logger.error(f"Error in split_into_sections: {e}")
            return {"Title": text}

def process_pdf(pdf_path: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """Process a PDF file and return both the original sections and their summaries."""
    try:
        logger.info(f"Starting PDF processing: {pdf_path}")
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
        
        logger.info("PDF processing completed successfully")
        return sections, summaries

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        return None, None
