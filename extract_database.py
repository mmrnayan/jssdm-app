import zipfile
import xml.etree.ElementTree as ET
import json
import re
import sys
from unicodeconverter import convert_bijoy_to_unicode

# Ensure console/file writing is encoded as UTF-8
sys.stdout.reconfigure(encoding='utf-8')

# Namespaces for parsing docx XML
namespaces = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# Complete AdarshaLipi to Unicode map
lipi_map = {
    # Vowels
    'A': 'অ', 'B': 'আ', 'C': 'ই', 'D': 'ঈ', 'E': 'উ', 'F': 'ঊ', 'G': 'ঋ', 'H': 'এ', 'I': 'ঐ', 'J': 'ও', 'K': 'ঔ',
    # Consonants
    'L': 'ক', 'M': 'খ', 'N': 'গ', 'O': 'ঘ', 'P': 'ঙ', 'Q': 'চ', 'R': 'ছ', 'S': 'জ', 'T': 'ঝ', 'U': 'ঞ',
    'V': 'ট', 'W': 'ঠ', 'X': 'ড', 'Y': 'ঢ', 'Z': 'ণ',
    'a': 'ত', 'b': 'থ', 'c': 'দ', 'd': 'ধ', 'e': 'ন', 'f': 'প', 'g': 'ফ', 'h': 'ব', 'i': 'ভ', 'j': 'ম',
    'k': 'য', 'l': 'র', 'm': 'ল', 'n': 'শ', 'o': 'ষ', 'p': 'স', 'q': 'হ',
    'r': 'ক্ষ', 's': 'ড়', 't': 'ঢ়', 'u': 'য়', 'v': 'ৎ',
    
    # Diacritics
    chr(161): 'া', # ¡
    chr(162): 'ি', # ¢
    chr(163): 'ী', # £
    chr(164): 'ু', # ¤
    chr(165): 'ূ', # ¥
    chr(166): 'ু', # ¦ -> 'ু' (specifically for 'র' + 'ু' = 'রু')
    chr(167): 'ূ', # §
    chr(168): 'ূ', # ¨ -> 'ূ' (specifically for 'ভ' + 'ূ' = 'ভূ')
    chr(171): 'ৃ', # « -> 'ৃ' (ri-kar)
    chr(173): 'ে', # \xad (soft hyphen)
    chr(174): 'ে', # ® -> E-kar
    chr(177): 'ো', # ±
    chr(178): 'ৌ', # ²
    chr(119): 'ং', # w
    chr(124): '।', # |
    'z': '।',
    '&': '্',
    
    # Numbers
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪', '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
    
    # Conjuncts
    chr(231): 'প্ত', # ç
    chr(249): 'ষ্ঠ', # ù
    chr(248): 'ষ্ট', # ø
    chr(230): 'ন্ন', # æ
    chr(216): 'স্', # Ø -> স্
    chr(210): 'ল্', # Ò -> ল্
    chr(217): 'স্', # Ù -> স্
    chr(218): 'থ',  # Û -> থ
    chr(339): 'ত্র', # œ -> ত্র
    chr(353): 'ক্', # š -> ক্
    chr(250): 'স্', # ú -> স্
    chr(170): 'কৃ', # ª -> কৃ
    chr(209): 'র্', # Ñ -> reph
    chr(203): '্র', # Ë -> r-phala
    chr(252): 'স্ব', # ü
    chr(199): 'ম্', # Ç
    chr(190): 'ন্', # ¾
    chr(191): 'ন্', # ¿
    chr(185): 'ত',  # ¹
    chr(8230): 'গু',
    chr(196): 'ত্ব',
    chr(201): '্য', # É -> ja-phala (্য)
    chr(246): 'শু', # ö
    
    # Standard Punctuation/Symbols
    ' ': ' ', '\t': '\t', '\n': '\n', '-': '-', '/': '/', '(': '(', ')': ')',
    ',': ',', '.': '.', ':': ':', '@': '@', '_': '_', '`': '`', '|': '।',
    chr(212): '“', chr(213): '”', chr(211): '‘',
    chr(8212): '—', chr(8216): '‘', chr(8217): '’', chr(8221): '”', chr(8222): '“'
}

def translate_lipi(text):
    res = []
    i = 0
    while i < len(text):
        c = text[i]
        res.append(lipi_map.get(c, c))
        i += 1
            
    translated = "".join(res)
    
    # Reordering diacritics
    consonant_pat = r'(?:[ক-হ]্)*[ক-হ]'
    
    # E-kar (ে), I-kar (ি), Oi-kar (ৈ) placement reordering
    translated = re.sub(r'ে(' + consonant_pat + r')', r'\1ে', translated)
    translated = re.sub(r'ি(' + consonant_pat + r')', r'\1ি', translated)
    translated = re.sub(r'ৈ(' + consonant_pat + r')', r'\1ৈ', translated)
    
    # Reorder Reph (র্)
    translated = re.sub(r'(' + consonant_pat + r')র্', r'র্\1', translated)
    
    # Contextual Cleanups
    translated = translated.replace("স্হ", "স্থ")
    translated = translated.replace("ত্রমানুসারে", "ক্রমানুসারে")
    
    return translated

def clean_text(text, font):
    if not text:
        return ""
    if font == 'AdarshaLipiExp':
        return translate_lipi(text)
    elif font == 'SutonnyMJ' or font == 'SutonnyAMJ':
        try:
            return convert_bijoy_to_unicode(text)
        except Exception:
            return text
    return text

def get_block_text(element):
    """Recursively processes a paragraph element, identifying runs and applying font-specific conversions."""
    text_parts = []
    for r in element.findall('.//w:r', namespaces):
        # Font name checking
        font = None
        rPr = r.find('w:rPr', namespaces)
        if rPr is not None:
            rFonts = rPr.find('w:rFonts', namespaces)
            if rFonts is not None:
                font = rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                
        t_parts = [t.text for t in r.findall('w:t', namespaces) if t.text]
        if t_parts:
            raw_run_text = "".join(t_parts)
            text_parts.append(clean_text(raw_run_text, font))
            
    return "".join(text_parts).strip()

def main():
    print("Opening JSSDM 2022 copy.docx...")
    with zipfile.ZipFile("JSSDM 202copy.docx" if not zipfile.is_zipfile("JSSDM 2022 copy.docx") else "JSSDM 2022 copy.docx") as z:
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        body = root.find('w:body', namespaces)
        
        print("Extracting elements in order...")
        blocks = []
        for child in body:
            tag = child.tag.split('}')[-1]
            if tag == 'p':
                text = get_block_text(child)
                if text:
                    blocks.append({'type': 'p', 'text': text})
            elif tag == 'tbl':
                rows_data = []
                for tr in child.findall('.//w:tr', namespaces):
                    row_cells = []
                    for tc in tr.findall('.//w:tc', namespaces):
                        cell_p_texts = []
                        for p in tc.findall('.//w:p', namespaces):
                            p_txt = get_block_text(p)
                            if p_txt:
                                cell_p_texts.append(p_txt)
                        row_cells.append(" ".join(cell_p_texts))
                    rows_data.append(row_cells)
                blocks.append({'type': 'tbl', 'rows': rows_data})
                
        print(f"Parsed {len(blocks)} document blocks.")
        
        # State trackers for categorizer
        current_part = "PART II"
        current_section = "SECTION 1"
        current_heading = ""
        
        rules = []
        abbreviations = []
        templates = []
        
        # Categorize content
        print("Processing and structuring data...")
        block_idx = 0
        while block_idx < len(blocks):
            block = blocks[block_idx]
            
            if block['type'] == 'p':
                text = block['text']
                
                # Check for structural headings
                if text.startswith("PART "):
                    current_part = text
                elif text.startswith("SECTION ") or text.startswith("cwi‡”Q` "):
                    current_section = text
                elif len(text) < 100 and not re.match(r'^\d{4}', text):
                    current_heading = text
                
                # Check for a rule (4 digit number followed by punctuation/space)
                rule_match = re.match(r'^(\d{4})[z।\.\s]\s*(.*)', text)
                if rule_match:
                    rule_id = rule_match.group(1)
                    rule_text = rule_match.group(2)
                    
                    # Accumulate paragraphs following this rule until next heading or table
                    next_idx = block_idx + 1
                    additional_text = []
                    while next_idx < len(blocks) and blocks[next_idx]['type'] == 'p' and not re.match(r'^\d{4}', blocks[next_idx]['text']) and len(blocks[next_idx]['text']) > 100:
                        additional_text.append(blocks[next_idx]['text'])
                        next_idx += 1
                        
                    full_text = rule_text
                    if additional_text:
                        full_text += "\n" + "\n".join(additional_text)
                        
                    rules.append({
                        "id": rule_id,
                        "part": current_part,
                        "section": current_section,
                        "category": current_heading,
                        "text": full_text
                    })
                    block_idx = next_idx - 1
                    
            elif block['type'] == 'tbl':
                rows = block['rows']
                if not rows:
                    block_idx += 1
                    continue
                    
                # Look for abbreviations table
                # Check if first cell of first row is a header
                first_row = rows[0]
                
                # Heuristic: if columns represent [English word, abbreviation] or [abbreviation, meaning]
                # Table 147-205 in the table list contains abbreviations
                is_abbr_table = False
                headers = [c.lower() for c in first_row]
                
                if any("abbreviation" in h or "meaning" in h or "acronym" in h or "symbol" in h for h in headers):
                    is_abbr_table = True
                elif len(first_row) >= 2 and len(first_row[0]) > 3 and len(first_row[1]) <= 10 and first_row[1].isupper():
                    # Word, abbreviation shape
                    is_abbr_table = True
                    
                if is_abbr_table or "SECTION 16" in current_section:
                    category = current_heading or "General Abbreviations"
                    for row in rows:
                        if not row or len(row) < 2:
                            continue
                        # Clean headers out
                        if any("abbreviation" in str(c).lower() or "meaning" in str(c).lower() for c in row):
                            continue
                        
                        abbr = ""
                        meaning = ""
                        
                        # Find which column is the abbreviation (shorter, usually uppercase)
                        if len(row) >= 2:
                            c0 = str(row[0]).strip()
                            c1 = str(row[1]).strip()
                            
                            # Sometimes column order is Word, Abbr, sometimes Abbr, Word.
                            # Heuristic: shorter text is the abbreviation.
                            if len(c0) > len(c1) and len(c1) > 0:
                                meaning = c0
                                abbr = c1
                            elif len(c1) > len(c0) and len(c0) > 0:
                                meaning = c1
                                abbr = c0
                            else:
                                abbr = c0
                                meaning = c1
                                
                        if abbr and meaning:
                            abbreviations.append({
                                "abbreviation": abbr,
                                "meaning": meaning,
                                "category": category
                            })
                            
                # Look for template formatting table
                elif any("template" in h or "format" in h or "pre-flight" in h for h in headers) or "SECTION 2" in current_section and len(rows) > 5:
                    templates.append({
                        "section": current_section,
                        "title": current_heading,
                        "structure": rows
                    })
                    
            block_idx += 1
            
        print(f"Extracted {len(rules)} rules.")
        print(f"Extracted {len(abbreviations)} abbreviations.")
        print(f"Extracted {len(templates)} templates.")
        
        # Save structured database to JSON file
        db = {
            "rules": rules,
            "abbreviations": abbreviations,
            "templates": templates
        }
        
        output_path = "jssdm_database.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully saved database to {output_path}")

if __name__ == "__main__":
    main()
