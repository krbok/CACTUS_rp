from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(text):
    max_length = 1024
    chunks = [text[i : i + max_length] for i in range(0, len(text), max_length)]
    summary = " ".join([summarizer(chunk)[0]["summary_text"] for chunk in chunks])
    return summary
