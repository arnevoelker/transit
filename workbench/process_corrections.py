#!/usr/bin/env python3
"""
Script to apply WIR24 terminology corrections to the screenplay transcript.
"""

import re

def apply_corrections(text):
    """Apply all terminology corrections to the text."""

    # People & Names
    text = re.sub(r'\bRebecca Reef\b', 'Rebecca Reif', text)
    text = re.sub(r'\bDennis\b', 'Denise', text)
    text = re.sub(r'\bTobias Turnherr\b', 'Tobias Thurnherr', text)

    # Standardize names that appear in various forms
    text = re.sub(r'\b(Melek|Medlec|Mellek|Mellec)\b', 'Melek', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(Mat)(?!\w)', 'Matt', text)  # Mat -> Matt (but not in words like Matilda)

    # Organizations & Banks
    text = re.sub(r'\b(Wire Bank|Veer Bank|WER Bank)\b', 'Bank WIR', text, flags=re.IGNORECASE)
    text = re.sub(r'\bRaiffeissen\b', 'Raiffeisen', text)
    text = re.sub(r'\b(Via C|V-I-A-C|Viag|Fiat|FIAK|FIAC)\b', 'VIAC', text, flags=re.IGNORECASE)
    text = re.sub(r'\b(CHW Netzwerk|CHW Network)\b', 'CHW-Netzwerk', text)
    text = re.sub(r'\bCHW Netz\b', 'CHW-Netzwerk', text)
    text = re.sub(r'\bTHW Netzwerk\b', 'CHW-Netzwerk', text)  # THW typo for CHW

    # Products & Services
    text = re.sub(r'\b(Saule 3a|Säule 3 A)\b', 'Säule 3a', text)
    text = re.sub(r'\b(E Banking|eBanking)\b', 'E-Banking', text, flags=re.IGNORECASE)
    text = re.sub(r'\bPrivat Kunden\b', 'Privatkunden', text)
    text = re.sub(r'\bGeschäfts Kunden\b', 'Geschäftskunden', text)
    text = re.sub(r'\b(Fest Geld|Festgeld Konto)\b', 'Festgeldkonto', text)
    text = re.sub(r'\bBeteiligung Scheine\b', 'Beteiligungsscheine', text)
    text = re.sub(r'\bSpar Konto\b', 'Sparkonto', text)
    text = re.sub(r'\bContent und Karte\b', 'Konten & Karten', text)
    text = re.sub(r'\bKonto und Karte\b', 'Konten & Karten', text)
    text = re.sub(r'\bMobile Banking\b', 'Mobile-Banking', text, flags=re.IGNORECASE)
    text = re.sub(r'\bDigital Banking\b', 'Digital-Banking', text, flags=re.IGNORECASE)

    # Technical Terms
    text = re.sub(r'\b(Typo 3|Typo3)\b', 'TYPO3', text)
    text = re.sub(r'\b(mega menu|Mega Menu)\b', 'mega-menu', text)
    text = re.sub(r'\bGA 4\b', 'GA4', text)

    # Swiss German - replace ß with ss
    text = text.replace('ß', 'ss')

    # Navigation & Methodology
    text = re.sub(r'\bTop 3 Principle\b', '"Top 3" principle', text)
    text = re.sub(r'\bGive Ask Ratio\b', 'Give-Ask-Ratio', text)
    text = re.sub(r'\bMobile first\b', 'mobile-first', text, flags=re.IGNORECASE)
    text = re.sub(r'\blifecycle based\b', 'lifecycle-based', text, flags=re.IGNORECASE)

    # Currency
    text = re.sub(r'\b(Fr\.|SFr)\b', 'CHF', text)

    # Abbreviations
    text = re.sub(r'\bUX UI\b', 'UX/UI', text)

    # Remove filler words (German fillers)
    # Be careful with "also" - only remove when it's clearly a filler
    text = re.sub(r'\b(äh|ähm)\b', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[inaudible\]|\[crosstalk\]', '[...]', text, flags=re.IGNORECASE)

    # Clean up multiple spaces that may result from removals
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r' ,', ',', text)
    text = re.sub(r' \.', '.', text)
    text = re.sub(r' \?', '?', text)

    return text

def main():
    input_file = '/Users/av/0-prod/transit/workbench/output/20251021 WIR24 Navigation/20251021 WIR24 Navigation screenplay_aai.md'
    output_file = '/Users/av/0-prod/transit/workbench/output/20251021 WIR24 Navigation/20251021 WIR24 Navigation screenplay_aai_corrected.md'

    # Read the file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Apply corrections
    corrected_content = apply_corrections(content)

    # Write the corrected file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(corrected_content)

    print(f"Corrections applied. Output saved to: {output_file}")
    print(f"Original length: {len(content)} characters")
    print(f"Corrected length: {len(corrected_content)} characters")

if __name__ == '__main__':
    main()
