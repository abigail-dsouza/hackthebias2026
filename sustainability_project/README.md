# Sustainability Word Game Generator

This project allows you to extract information from corporate sustainability reports (PDFs) and generate a "Fill in the blank" game based on facts and biases found in the text.

## Features
- Downloads sustainability reports (defaulting to Google and Microsoft examples).
- Extracts text from PDFs.
- Analyzes text for sustainability keywords (e.g., "Carbon", "Water").
- Categorizes sentences as "Facts" (containing data/numbers) or "Biases" (subjective language).
- Generates 5 random clues for the game.

## Setup

1.  Open your terminal.
2.  Navigate to this directory:
    ```bash
    cd sustainability_project
    ```
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

Run the script:

```bash
python3 main.py
```

## Customization

You can add more URLs to the `DEFAULT_URLS` list in `main.py` to analyze other companies.
