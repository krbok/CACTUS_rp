import re
import nltk
from svgwrite import Drawing
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from collections import defaultdict
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import io
import networkx as nx
from sklearn.feature_extraction.text import TfidfVectorizer
import matplotlib.pyplot as plt
import base64
import os

def setup_nltk():
    """
    Ensures all required NLTK data is downloaded.
    Returns True if successful, False otherwise.
    """
    try:
        # Create nltk_data directory in user's home if it doesn't exist
        nltk_data_dir = os.path.expanduser('~/nltk_data')
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)

        # List of required NLTK packages
        required_packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger']
        
        # Download required packages
        for package in required_packages:
            try:
                nltk.data.find(f'tokenizers/{package}')
            except LookupError:
                print(f"Downloading {package}...")
                nltk.download(package, quiet=True)
        
        return True
    
    except Exception as e:
        print(f"Error setting up NLTK: {str(e)}")
        return False

def generate_graphical_abstract(summary):
    """
    Generates a graphical abstract from a research paper summary using
    text analysis and SVG visualization.
    """
    # Setup NLTK first
    if not setup_nltk():
        raise Exception("Failed to setup required NLTK data. Please ensure you have internet connection and proper permissions.")
    
    try:
        # Initialize NLTK components
        stop_words = set(stopwords.words('english'))
        
        def preprocess_text(text):
            # Tokenize and clean text
            tokens = word_tokenize(text.lower())
            tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
            return tokens
        
        def extract_key_concepts(text, num_concepts=5):
            try:
                # Use TF-IDF to extract key concepts
                vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2))
                tfidf_matrix = vectorizer.fit_transform([text])
                feature_names = vectorizer.get_feature_names_out()
                scores = zip(feature_names, np.asarray(tfidf_matrix.sum(axis=0)).ravel())
                sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
                return sorted_scores[:num_concepts]
            except Exception as e:
                print(f"Error in concept extraction: {str(e)}")
                return []
        
        def create_concept_graph(concepts):
            # Create a network graph of concepts
            G = nx.Graph()
            for i, (concept, score) in enumerate(concepts):
                G.add_node(concept, weight=score)
                for j in range(i):
                    G.add_edge(concept, concepts[j][0], weight=min(score, concepts[j][1]))
            return G
        
        def generate_svg(G, width=800, height=600):
            # Create SVG drawing
            dwg = Drawing('abstract.svg', size=(width, height))
            
            # Add gradient background
            gradient = dwg.defs.add(dwg.linearGradient(id='background_grad'))
            gradient.add_stop_color(0, '#1a1a2e')
            gradient.add_stop_color(1, '#16213e')
            dwg.add(dwg.rect((0, 0), (width, height), fill='url(#background_grad)'))
            
            # Calculate node positions using spring layout
            pos = nx.spring_layout(G)
            
            # Scale positions to fit SVG dimensions
            scale_x = width * 0.8
            scale_y = height * 0.8
            margin_x = width * 0.1
            margin_y = height * 0.1
            
            try:
                # Draw edges
                for edge in G.edges():
                    start = pos[edge[0]]
                    end = pos[edge[1]]
                    x1 = start[0] * scale_x + margin_x
                    y1 = start[1] * scale_y + margin_y
                    x2 = end[0] * scale_x + margin_x
                    y2 = end[1] * scale_y + margin_y
                    
                    # Create gradient for edge
                    edge_gradient = dwg.defs.add(dwg.linearGradient(
                        id=f'edge_grad_{hash(edge[0])}_{hash(edge[1])}',
                        x1=x1, y1=y1, x2=x2, y2=y2
                    ))
                    edge_gradient.add_stop_color(0, '#4a90e2', opacity=0.3)
                    edge_gradient.add_stop_color(1, '#4a90e2', opacity=0.1)
                    
                    dwg.add(dwg.line(
                        (x1, y1), (x2, y2),
                        stroke=f'url(#edge_grad_{hash(edge[0])}_{hash(edge[1])})',
                        stroke_width=2
                    ))
                
                # Draw nodes and labels
                for node in G.nodes():
                    x = pos[node][0] * scale_x + margin_x
                    y = pos[node][1] * scale_y + margin_y
                    
                    # Add node circle
                    dwg.add(dwg.circle(
                        center=(x, y),
                        r=30,
                        fill='#4a90e2',
                        stroke='white',
                        stroke_width=2,
                        opacity=0.8
                    ))
                    
                    # Add text label
                    text = dwg.text(
                        node,
                        insert=(x, y),
                        fill='white',
                        font_size='14px',
                        font_family='Arial',
                        text_anchor='middle',
                        dominant_baseline='middle'
                    )
                    dwg.add(text)
                
                return dwg
            
            except Exception as e:
                print(f"Error generating SVG elements: {str(e)}")
                return None

        # Main execution flow
        key_concepts = extract_key_concepts(summary)
        if not key_concepts:
            raise Exception("No key concepts could be extracted from the summary")
        
        G = create_concept_graph(key_concepts)
        if not G or G.number_of_nodes() == 0:
            raise Exception("Failed to create concept graph")
        
        svg = generate_svg(G)
        if svg is None:
            raise Exception("Failed to generate SVG visualization")
        
        # Save SVG to file
        output_path = 'graphical_abstract.svg'
        svg.save(output_path)
        
        return output_path
        
    except Exception as e:
        print(f"Error in graphical abstract generation: {str(e)}")
        raise

if __name__ == "__main__":
    # Example usage with error handling
    try:
        summary = "Example research paper summary..."
        output_path = generate_graphical_abstract(summary)
        print(f"Successfully generated graphical abstract: {output_path}")
    except Exception as e:
        print(f"Failed to generate graphical abstract: {str(e)}")
        