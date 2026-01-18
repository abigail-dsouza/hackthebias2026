
import requests
import io
import re
import random
from pypdf import PdfReader
from gri_standards import GRI_STANDARDS, BIAS_FLUFF_WORDS

# Example URLs of sustainability reports
DEFAULT_URLS = [
    "https://www.gstatic.com/gumdrop/sustainability/google-2024-environmental-report.pdf",
    "https://query.prod.cms.rt.microsoft.com/cms/api/am/binary/RW1lMj" 
]

class SustainabilityAuditor:
    def __init__(self):
        self.pdfs_processed = 0

    def download_pdf_text(self, url):
        """Downloads a PDF from a URL and extracts its text (all pages)."""
        print(f"Downloading report from {url}...")
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            
            f = io.BytesIO(response.content)
            reader = PdfReader(f)
            
            text = ""
            print(f"Extracting text from {len(reader.pages)} pages...")
            for page in reader.pages: # No limit for deep audit
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            self.pdfs_processed += 1
            return text
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return ""

    def clean_text(self, text):
        # Remove multiple spaces and newlines for regex safety
        return re.sub(r'\s+', ' ', text).strip()

    def split_into_sentences(self, text):
        # Simple split, but effective for this scale
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if len(s) > 30]

    def audit_report(self, text, report_name="Unknown Report"):
        """Audits a single report against GRI standards."""
        print(f"\nScanning {report_name} against GRI Standards...")
        text_lower = text.lower()
        sentences = self.split_into_sentences(text)
        
        findings = []

        # 1. CHECK GRI COVERAGE
        for gri_code, data in GRI_STANDARDS.items():
            found_keywords = False
            found_metrics = False
            
            # Check for explicitly labeled GRI content first (high confidence)
            if gri_code.lower() in text_lower:
                confidence = "High"
                findings.append({
                    "type": "GRI_MENTION",
                    "code": gri_code,
                    "clue": f"The report explicitly cites {gri_code} ({data['title']}).",
                    "original": f"Explicit mention of {gri_code}"
                })
                continue # Skip to next standard if explicitly found to avoid duplicates

            # Check for keyword coverage
            for kw in data['keywords']:
                if kw in text_lower:
                    found_keywords = True
                    break
            
            # Check for required metrics (quantitative)
            # We look for the metric unit near the keyword? Or just presence of the unit globally?
            # Let's check globally first for simplicity.
            for metric in data['required_metrics']:
                 if re.search(r'\b' + metric + r'\b', text_lower):
                     found_metrics = True
                     break
            
            if found_keywords and found_metrics:
                # Add a positive finding
                # We need to find a sentence that proves this.
                relevant_sentences = [s for s in sentences if any(kw in s.lower() for kw in data['keywords']) and any(char.isdigit() for char in s)]
                if relevant_sentences:
                    s = random.choice(relevant_sentences)
                    # Clean up sentence for clue
                    clue = s
                    for kw in data['keywords']:
                         clue = re.sub(r'\b' + kw + r'\b', "_______", clue, flags=re.IGNORECASE)
                    
                    findings.append({
                        "type": "FACT",
                        "code": gri_code,
                        "clue": clue,
                        "original": s,
                        "citation": "Report Text"
                    })
            elif not found_keywords:
                # OMISSION DETECTED
                 findings.append({
                    "type": "OMISSION",
                    "code": gri_code,
                    "clue": f"The report does not significantly disclose information aligned with GRI {gri_code} ({data['title']}).",
                    "original": "N/A",
                    "citation": "Gap Analysis",
                    "details": f"Missing keywords like '{data['keywords'][0]}'"
                })

        # 2. DETECT BIAS (in sentences that lack numbers but use fluff words)
        bias_sentences = []
        for s in sentences:
            has_number = bool(re.search(r'\d', s))
            has_fluff = any(w in s.lower() for w in BIAS_FLUFF_WORDS)
            
            if has_fluff and not has_number:
                bias_sentences.append(s)
        
        if bias_sentences:
            # Pick a few biases
            for _ in range(min(3, len(bias_sentences))):
                s = random.choice(bias_sentences)
                # Hide the fluff word
                found_fluff = [w for w in BIAS_FLUFF_WORDS if w in s.lower()][0]
                clue = re.sub(r'\b' + found_fluff + r'\b', "_______", s, flags=re.IGNORECASE)
                findings.append({
                    "type": "BIAS",
                    "code": "Marketing",
                    "clue": clue,
                    "original": s,
                    "citation": "Sentiment Analysis"
                })

        return findings

    def generate_game(self, urls=DEFAULT_URLS):
        all_findings = []
        
        for i, url in enumerate(urls):
            name = f"Report {i+1}"
            raw_text = self.download_pdf_text(url)
            if not raw_text: continue
            
            clean = self.clean_text(raw_text)
            report_findings = self.audit_report(clean, name)
            all_findings.extend(report_findings)

        # SELECT FINAL CLUES
        # Criteria: 5 clues total.
        # Mix: 2 Omissions (if any), 2 Facts, 1 Bias.
        
        omissions = [f for f in all_findings if f['type'] == "OMISSION"]
        facts = [f for f in all_findings if f['type'] == "FACT"]
        biases = [f for f in all_findings if f['type'] == "BIAS"]
        
        final_clues = []
        
        # Add Omissions
        if omissions:
            final_clues.extend(random.sample(omissions, min(2, len(omissions))))
            
        # Add Bias
        if biases:
            final_clues.extend(random.sample(biases, min(1, len(biases))))
            
        # Fill rest with Facts
        needed = 5 - len(final_clues)
        if facts and needed > 0:
            final_clues.extend(random.sample(facts, min(needed, len(facts))))
            
        # If still need more, take from any pile
        while len(final_clues) < 5 and (omissions or facts or biases):
             if omissions: final_clues.append(omissions.pop())
             elif facts: final_clues.append(facts.pop())
             elif biases: final_clues.append(biases.pop())
             else: break

        print("\n=== ESG AUDITOR: GENERATED CLUES ===")
        print("------------------------------------")
        for item in final_clues:
            print(f"TYPE     : {item['type']}")
            print(f"TOPIC    : {item['code']}")
            print(f"CLUE     : {item['clue']}")
            if 'citation' in item:
                print(f"CITATION : {item['citation']}")
            if 'details' in item:
                print(f"DETAILS  : {item['details']}")
            print("-" * 50)

if __name__ == "__main__":
    auditor = SustainabilityAuditor()
    auditor.generate_game()
