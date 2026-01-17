import requests
import io
import re
import random
from pypdf import PdfReader

# Example URLs of sustainability reports (found previously)
# We use these as defaults if "finding" programmatically is restricted by lack of custom search API
DEFAULT_URLS = [
    "https://www.gstatic.com/gumdrop/sustainability/google-2024-environmental-report.pdf",
    "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RW1lMj" # Microsoft 2024 Report
]

THEME_WORDS = [
    "CARBON", "EMISSIONS", "WATER", "ENERGY", "WASTE", 
    "CLIMATE", "RENEWABLE", "NET-ZERO", "BIODIVERSITY", "CIRCULAR"
]

BIAS_INDICATORS = [
    "proud", "leader", "committed", "vision", "believe", "dedication", 
    "best", "forefront", "innovative", "unique", "excellence"
]

def download_pdf_text(url):
    """Downloads a PDF from a URL and extracts its text."""
    print(f"Downloading report from {url}...")
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        f = io.BytesIO(response.content)
        reader = PdfReader(f)
        
        text = ""
        # Limit to first 50 pages to save time/memory and usually contains the executive summary
        for page in reader.pages[:50]: 
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text
    except Exception as e:
        print(f"Error processing {url}: {e}")
        return ""

def clean_text(text):
    """Normalizes whitespace."""
    return re.sub(r'\s+', ' ', text).strip()

def split_into_sentences(text):
    """Simple regex-based sentence splitter."""
    # Split on . ? ! followed by a space/end of line. 
    # Lookbehind check to avoid splitting on initials like U.S. might be needed but simple split is okay for this demo.
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if len(s) > 20] # Filter out tiny artifacts

def get_sentence_type(sentence):
    """Heuristic to determine if a sentence mentions facts (numbers) or biases (subjective)."""
    has_number = bool(re.search(r'\d+%|\$\d+|\d{4}', sentence))
    has_bias = any(word in sentence.lower() for word in BIAS_INDICATORS)
    
    types = []
    if has_number:
        types.append("FACT")
    if has_bias:
        types.append("BIAS")
    
    return types

def generate_game_content(urls=DEFAULT_URLS):
    all_text = ""
    for url in urls:
        raw_text = download_pdf_text(url)
        all_text += clean_text(raw_text) + " "
    
    if not all_text.strip():
        print("No text could be extracted.")
        return

    sentences = split_into_sentences(all_text)
    
    found_clues = {} # Map word -> list of (sentence, type)
    
    print("\nAnalyzing text for themes...")
    
    for sentence in sentences:
        sentence_upper = sentence.upper()
        for word in THEME_WORDS:
            # Check if the word is in the sentence (simple boundary check)
            # We want the word to appear clearly
            if re.search(r'\b' + word + r'\b', sentence_upper):
                stypes = get_sentence_type(sentence)
                if stypes:
                    if word not in found_clues:
                        found_clues[word] = []
                    found_clues[word].append((sentence, stypes))

    # Select 5 words
    available_words = [w for w in found_clues.keys() if len(found_clues[w]) > 0]
    
    if len(available_words) < 5:
        print(f"Only found {len(available_words)} theme words. Need more text or more loosely defined keywords.")
        selected_words = available_words
    else:
        selected_words = random.sample(available_words, 5)

    print("\n=== SUSTAINABILITY THEME & CLUES ===")
    print("--------------------------------------")
    
    final_output = []
    
    for word in selected_words:
        # Try to mix facts and biases
        options = found_clues[word]
        # Prefer short succinct sentences for clues, < 200 chars
        short_options = [opt for opt in options if len(opt[0]) < 200]
        if not short_options:
            short_options = options
            
        picked_sentence, picked_types = random.choice(short_options)
        
        # Create fill-in-the-blank
        # Case insensitive replace of the word
        clue = re.sub(r'\b' + word + r'\b', "_______", picked_sentence, flags=re.IGNORECASE)
        
        final_output.append({
            "word": word,
            "clue": clue,
            "types": ", ".join(picked_types),
            "original": picked_sentence
        })

    for item in final_output:
        print(f"WORD: {item['word']}")
        print(f"TYPE: {item['types']}")
        print(f"CLUE: {item['clue']}")
        print("-" * 40)

if __name__ == "__main__":
    generate_game_content()
