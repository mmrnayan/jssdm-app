#!/usr/bin/env python3
"""
JSSDM 2022 Database Extractor v2
Comprehensive extraction from JSSDM 2022 (JSP-001) docx.

Fixes from v1:
1. Section-aware parsing for all 19 sections (not just 4-digit rule IDs)
2. Abbreviation subsection handling (16A-16H) with junk filtering
3. Bangla abbreviation support (Part I annexes)
4. ID normalisation (all Arabic numerals)
5. Structured templates with field mapping
6. Complete coverage of Sections 10-19
"""

import zipfile
import xml.etree.ElementTree as ET
import json
import re
import sys
import unicodedata
from collections import Counter

try:
    from unicodeconverter import convert_bijoy_to_unicode
    HAS_BIJOY = True
except ImportError:
    HAS_BIJOY = False
    print("Warning: unicodeconverter not available. SutonnyMJ text will not be converted.")

sys.stdout.reconfigure(encoding='utf-8')

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

# ─── AdarshaLipi to Unicode map (from v1, verified) ───
LIPI_MAP = {
    'A': 'অ', 'B': 'আ', 'C': 'ই', 'D': 'ঈ', 'E': 'উ', 'F': 'ঊ', 'G': 'ঋ',
    'H': 'এ', 'I': 'ঐ', 'J': 'ও', 'K': 'ঔ',
    'L': 'ক', 'M': 'খ', 'N': 'গ', 'O': 'ঘ', 'P': 'ঙ', 'Q': 'চ', 'R': 'ছ',
    'S': 'জ', 'T': 'ঝ', 'U': 'ঞ', 'V': 'ট', 'W': 'ঠ', 'X': 'ড', 'Y': 'ঢ',
    'Z': 'ণ', 'a': 'ত', 'b': 'থ', 'c': 'দ', 'd': 'ধ', 'e': 'ন', 'f': 'প',
    'g': 'ফ', 'h': 'ব', 'i': 'ভ', 'j': 'ম', 'k': 'য', 'l': 'র', 'm': 'ল',
    'n': 'শ', 'o': 'ষ', 'p': 'স', 'q': 'হ', 'r': 'ক্ষ', 's': 'ড়', 't': 'ঢ়',
    'u': 'য়', 'v': 'ৎ',
    chr(161): 'া', chr(162): 'ি', chr(163): 'ী', chr(164): 'ু', chr(165): 'ূ',
    chr(166): 'ু', chr(167): 'ূ', chr(168): 'ূ', chr(171): 'ৃ',
    chr(173): 'ে', chr(174): 'ে', chr(177): 'ো', chr(178): 'ৌ',
    'w': 'ং', chr(124): '।', 'z': '।', '&': '্',
    '0': '০', '1': '১', '2': '২', '3': '৩', '4': '৪',
    '5': '৫', '6': '৬', '7': '৭', '8': '৮', '9': '৯',
    chr(231): 'প্ত', chr(249): 'ষ্ঠ', chr(248): 'ষ্ট', chr(230): 'ন্ন',
    chr(216): 'স্', chr(210): 'ল্', chr(217): 'স্', chr(218): 'থ',
    chr(339): 'ত্র', chr(353): 'ক্', chr(250): 'স্', chr(170): 'কৃ',
    chr(209): 'র্', chr(203): '্র', chr(252): 'স্ব', chr(199): 'ম্',
    chr(190): 'ন্', chr(191): 'ন্', chr(185): 'ত', chr(8230): 'গু',
    chr(196): 'ত্ব', chr(201): '্য', chr(246): 'শু',
    ' ': ' ', '\t': '\t', '\n': '\n', '-': '-', '/': '/', '(': '(', ')': ')',
    ',': ',', '.': '.', ':': ':', '@': '@', '_': '_', '`': '`',
    chr(212): '“', chr(213): '”', chr(211): '‘',
    chr(8212): '—', chr(8216): '‘', chr(8217): '’',
    chr(8221): '”', chr(8222): '„',
    # ─── Expanded conjuncts (verified against raw docx contexts) ───
    chr(193): '্ন',   # Á -> ্ন (as in পূর্ণ)
    chr(8482): 'ণ্ড',  # ™ -> ণ্ড (as in খণ্ড) — Unicode U+2122
    chr(219): 'থ',    # Û -> থ (as in ব্যবস্থা — the া comes from next char ¡)
    chr(220): 'দ্ধ',  # Ü -> দ্ধ (as in পদ্ধতি)
    chr(202): '্র',   # Ê -> র-ফলা (as in প্রকার)
    chr(402): 'কট',   # ƒ -> কট (as in ইলেকট্রনিক) — Unicode U+0192
    chr(181): 'চ্',   # µ -> চ্ (as in উচ্চ — hasanta AFTER চ)
    chr(245): 'ল্ল',  # õ -> ল্ল (as in উল্লেখ)
    chr(253): 'হু',   # ý -> হু
    chr(186): 'তু',   # º -> তু
    chr(214): 'ষ্',   # Ö -> ষ্ (as in বিষ্ফোরণ — প comes from next char f)
    chr(132): 'ক্স',  # „ -> ক্স
    chr(126): '~',    # ~ -> ~ (for E+tilde → Oi-kar replacement)
    # ─── Additional conjuncts from user verification report ───
    chr(235): 'ব্দ',   # ë -> ব্দ (as in শব্দ)
    chr(241): 'ম্ভ',   # ñ -> ম্ভ (as in সম্ভব)
    chr(208): '্র',    # Ð -> র-ফলা (as in প্রাপক)
    chr(169): 'ৃ',     # © -> ৃ (as in ব্যবহৃত)
    chr(226): 'দ্র',   # â -> দ্র (as in মুদ্রণ)
    chr(224): 'দৃ',    # à -> দৃ (as in দৃশ্য)
    chr(376): 'দ্দ',   # Ÿ -> দ্দ (as in উদ্দেশ্য)
    chr(187): 'ত্র',   # » -> ত্র (as in সশস্ত্র)
    chr(184): 'ধ্যা',  # ¸ -> ধ্যা (as in অধ্যায়)
    chr(229): 'ন্ধ',   # å -> ন্ধ (as in নিবন্ধ)
    chr(240): 'ম্ব',   # ð -> ম্ব (as in নম্বর)
    chr(192): '্ন',    # À -> ্ন (as in নিম্নলিখিত, সংলগ্নীর)
}


def translate_lipi(text):
    res = [LIPI_MAP.get(c, c) for c in text]
    translated = "".join(res)
    
    # Swap prefix-hasant conjuncts mapped from legacy layouts (e.g. ্চচ -> চ্চ, ্চছ -> চচ্ছ)
    translated = translated.replace("্চচ", "চ্চ")
    translated = translated.replace("্চছ", "চ্ছ")
    
    # Combine E-car + tilde to Oi-car before reordering
    translated = translated.replace("ে~", "ৈ")
    
    cp = r'্?(?:[ক-হ]্)*[ক-হ]'
    translated = re.sub(r'ে(' + cp + r')', r'\1ে', translated)
    translated = re.sub(r'ি(' + cp + r')', r'\1ি', translated)
    translated = re.sub(r'ৈ(' + cp + r')', r'\1ৈ', translated)
    translated = re.sub(r'(' + cp + r')র্', r'র্\1', translated)
    
    # Combine split vowels after reordering
    translated = translated.replace("ো", "ো")
    translated = translated.replace("েো", "ৌ")
    translated = translated.replace("েৌ", "ৌ")
    
    translated = translated.replace("স্হ", "স্থ")
    translated = translated.replace("ত্রমানুসারে", "ক্রমানুসারে")
    return translated


def looks_like_lipi(text):
    """Detect AdarshaLipi-encoded text misattributed to another font.
    These texts contain high-byte Latin characters (¢, ®, £, ¡, etc.)
    that are actually AdarshaLipi diacritics/conjuncts."""
    if not text or len(text) < 2:
        return False
    lipi_indicators = set(chr(c) for c in [161, 162, 163, 164, 165, 166, 167, 168,
                                            171, 173, 174, 177, 178, 209, 210, 216,
                                            217, 218, 230, 231, 248, 249, 250, 252,
                                            170, 185, 190, 191, 196, 199, 201, 203,
                                            193, 8482, 219, 220, 202, 402, 181,
                                            245, 253, 186, 214, 132, 235, 241,
                                            208, 169, 226, 224, 376, 187, 184, 229])
    indicator_count = sum(1 for c in text if c in lipi_indicators)
    # If more than 15% of characters are AdarshaLipi indicators, it's likely Lipi text
    return indicator_count >= 1 and indicator_count / len(text) > 0.15


def clean_text(text, font):
    if not text:
        return ""
    if font and 'AdarshaLipi' in font:
        return translate_lipi(text)
    elif font and ('SutonnyMJ' in font or 'SutonnyAMJ' in font):
        if HAS_BIJOY:
            try:
                return convert_bijoy_to_unicode(text)
            except Exception:
                return text
        return text
    # Auto-detect AdarshaLipi text misattributed to Calibri or other fonts
    if looks_like_lipi(text):
        return translate_lipi(text)
    return text


def get_run_font(r):
    """Extract font name from a run element."""
    rPr = r.find('w:rPr', NS)
    if rPr is not None:
        rFonts = rPr.find('w:rFonts', NS)
        if rFonts is not None:
            return (rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii')
                    or rFonts.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi'))
    return None


def get_block_text(element):
    """Extract text from a paragraph, applying font-specific conversions."""
    parts = []
    for r in element.findall('.//w:r', NS):
        font = get_run_font(r)
        for t in r.findall('w:t', NS):
            if t.text:
                parts.append(clean_text(t.text, font))
    return "".join(parts).strip()


def get_table_rows(tbl):
    """Extract rows from a table element, each row is a list of cell strings."""
    rows = []
    for tr in tbl.findall('.//w:tr', NS):
        cells = []
        for tc in tr.findall('.//w:tc', NS):
            cell_parts = []
            for p in tc.findall('.//w:p', NS):
                txt = get_block_text(p)
                if txt:
                    cell_parts.append(txt)
            cells.append(" ".join(cell_parts))
        rows.append(cells)
    return rows


def normalise_id(rule_id):
    """Convert Bangla numeral IDs to Arabic numerals."""
    bangla_digits = '০১২৩৪৫৬৭৮৯'
    result = []
    for ch in str(rule_id):
        idx = bangla_digits.find(ch)
        if idx >= 0:
            result.append(str(idx))
        else:
            result.append(ch)
    return "".join(result)


def is_junk_abbreviation(abbr, meaning):
    """Filter out junk entries from abbreviation tables."""
    abbr_s = abbr.strip()
    meaning_s = meaning.strip()

    if not abbr_s or not meaning_s:
        return True

    # Table header fragments
    header_words = ['abbreviation', 'meaning', 'acronym', 'serial', 'word', 'full form',
                    'appointment', 'rank', 'description', 'symbol']
    if abbr_s.lower() in header_words or meaning_s.lower() in header_words:
        return True

    # Column labels like (a), (b), (c), (d)
    if re.match(r'^\([a-z]\)$', abbr_s) or re.match(r'^\([a-z]\)$', meaning_s):
        return True

    # Pure serial numbers: 1., 2., 3. etc
    if re.match(r'^\d+\.?$', abbr_s) or re.match(r'^\d+\.?$', meaning_s):
        return True

    # Page markers like 16A-1, 16B-2
    if re.match(r'^\d+[A-H]-\d+$', abbr_s):
        return True

    # Very short meaningless entries
    if len(abbr_s) <= 1 and not abbr_s.isalpha():
        return True

    # Measurement units that leaked in
    measurement_junk = ['mm', 'cm', 'km', 'kg', 'lb', 'oz', 'ft', 'in', 'yd', 'mi',
                        'sq', 'cu', 'gal', 'pt', 'qt']
    # Only filter if both abbr and meaning look like measurement descriptors
    if abbr_s.lower() in measurement_junk and len(meaning_s) < 15:
        return True

    # Empty or whitespace only
    if not abbr_s.strip() or not meaning_s.strip():
        return True

    return False


def parse_paragraph_abbreviations(text):
    """Parse abbreviation entries from paragraph text like 'Full Name   ABBR'.
    Returns (meaning, abbreviation) or None."""
    # Pattern: words followed by whitespace then short uppercase abbreviation
    # e.g. "Armoured Corps.    AC" or "BNS ISSA KHAN IK"
    m = re.match(r'^(.+?)\s{2,}(\S+(?:\s\S+)?)$', text.strip())
    if m:
        meaning = m.group(1).strip().rstrip('.')
        abbr = m.group(2).strip()
        # Abbreviation should be relatively short compared to meaning
        if len(abbr) < len(meaning) and len(abbr) <= 30:
            return (meaning, abbr)
    return None


# ─── Section boundary map (element indices) ───
# Built from the docx structure analysis
SECTION_BOUNDARIES = {
    # Part I (Bangla)
    "PART_I": (0, 575),
    # Part II (English)
    "SECTION_1": (603, 842),
    "SECTION_2": (843, 2331),
    "SECTION_3": (2332, 2954),
    "SECTION_4": (2955, 3154),
    "SECTION_5": (3155, 3522),
    "SECTION_6": (3523, 3708),
    "SECTION_7": (3709, 3800),
    "SECTION_8": (3801, 3866),
    "SECTION_9": (3867, 4561),
    "SECTION_10": (4562, 4627),
    "SECTION_11": (4628, 6693),
    "SECTION_12": (6694, 7762),
    "SECTION_13": (7763, 7851),
    "SECTION_14": (7852, 7928),
    "SECTION_15": (7929, 8470),
    "SECTION_16": (8471, 9464),
    "SECTION_17": (9465, 10693),
    "SECTION_18": (10694, 10773),
    "SECTION_19": (10774, 10879),
}

# Abbreviation annex boundaries within Section 16
ABBR_ANNEXES = {
    "16A": (8539, 8927),   # General Abbreviations
    "16B": (8928, 8962),   # Multiple Meanings
    "16C": (8963, 9135),   # Ranks and Appointments
    "16D": (9136, 9155),   # National Distinguishing Letters
    "16E": (9156, 9180),   # Training Institutions
    "16F": (9181, 9270),   # Regiments and Corps (paragraph-based)
    "16G": (9271, 9353),   # Navy units (paragraph-based)
    "16H": (9354, 9464),   # Air Force units
}

# Bangla abbreviation tables in Part I
BANGLA_ABBR_TABLES = [522, 531, 533, 535, 537, 541, 544, 546]


def is_valid_annex_start(text):
    t_upper = text.upper().strip()

    if len(text) >= 120:
        return False

    # Plural ANNEXES is generally a section heading/intro, not a template start
    if 'ANNEXES' in t_upper and 'ANNEX' not in t_upper.replace('ANNEXES', ''):
        return False

    words = t_upper.split()
    if not words:
        return False
    first_word = words[0]

    # Template keyword headings (don't require ANNEX/TO)
    template_first = ['EXAMPLE', 'SPECIMEN', 'FRAMEWORK', 'MEMORANDUM', 'MODEL', 'SAMPLE']
    if first_word in template_first:
        # Reject sentence-like text (ends with period and is long)
        if text.strip().endswith('.') and len(text) > 50:
            return False
        return True

    # ANNEX/APPENDIX headings require TO or SECTION
    if any(w in t_upper for w in ['ANNEX', 'APPENDIX', 'APPX', 'ANX']):
        if 'TO' in t_upper or 'SECTION' in t_upper:
            annex_first = ['ANNEX', 'APPENDIX', 'APPX', 'ANX', 'SECRET']
            if first_word in annex_first:
                return True
            # Page prefix like 3D-2 or 16E-3
            if re.match(r'^\d+[A-Z]\d*-\d+$', first_word):
                return True

    # LAYOUT/FORMAT/STANDARD headings (standalone, no ANNEX required)
    layout_first = ['LAYOUT', 'FORMAT', 'STANDARD', 'OUTLINE']
    if first_word in layout_first:
        if text.strip().endswith('.') and len(text) > 50:
            return False
        return True

    return False


def main():
    print("Opening JSSDM 2022 copy.docx...")
    with zipfile.ZipFile("JSSDM 2022 copy.docx") as z:
        xml_content = z.read('word/document.xml')
        root = ET.fromstring(xml_content)
        body = root.find('w:body', NS)
        children = list(body)

        print(f"Total document elements: {len(children)}")

        # ─── Phase 1: Parse all elements ───
        blocks = []
        for i, child in enumerate(children):
            tag = child.tag.split('}')[-1]
            if tag == 'p':
                text = get_block_text(child)
                blocks.append({'idx': i, 'type': 'p', 'text': text or ''})
            elif tag == 'tbl':
                rows = get_table_rows(child)
                blocks.append({'idx': i, 'type': 'tbl', 'rows': rows})
            else:
                blocks.append({'idx': i, 'type': 'other', 'text': ''})

        # Build index-to-block lookup
        idx_to_block = {b['idx']: b for b in blocks}

        # ─── Phase 2: Extract Rules ───
        print("\n--- Extracting Rules ---")
        rules = []
        current_section = ""
        current_heading = ""
        current_annex = ""

        for b in blocks:
            if b['type'] != 'p' or not b['text']:
                continue

            text = b['text']
            idx = b['idx']

            # Detect section boundaries
            if text.startswith('SECTION') and len(text) < 80:
                sec_match = re.match(r'SECTION[\s-]*(\d+)', text)
                if sec_match:
                    current_section = f"SECTION {sec_match.group(1)}"
                    current_heading = ""
                    current_annex = ""
                    continue

            # Detect annex markers
            if 'ANNEX' in text and 'SECTION' in text and len(text) < 100:
                current_annex = text.strip()
                continue

            # Detect section from combined text like "9C-1 CHAPTER-IV: OPERATIONAL WRITING SECTION 10 ..."
            sec_inline = re.search(r'SECTION[\s-]*(\d+)', text)
            if sec_inline and len(text) < 120 and ('CHAPTER' in text or text.startswith('SECTION')):
                current_section = f"SECTION {sec_inline.group(1)}"
                current_heading = ""
                current_annex = ""

            # Detect Part I bangla sections
            if idx < 576:
                current_section = "SECTION 1 (BANGLA)"

            # Detect headings (short non-rule paragraphs)
            if len(text) < 120 and not re.match(r'^[\d০-৯]{4}', text) and text.isupper() if len(text) > 3 else False:
                current_heading = text

            # Match rule IDs: 4-digit Arabic or Bangla numerals
            rule_match = re.match(r'^([\d০-৯]{4})[z।.\s]\s*(.*)', text, re.DOTALL)
            if rule_match:
                raw_id = rule_match.group(1)
                rule_id = normalise_id(raw_id)
                rule_text = rule_match.group(2).strip()

                # Fix anomalous IDs
                if rule_id == '2626' and current_section == 'SECTION 2':
                    # Likely should be in 0246 range based on context
                    pass  # Keep as-is but flag it

                # Accumulate continuation paragraphs
                next_blocks = [nb for nb in blocks if nb['idx'] > idx and nb['idx'] < idx + 50]
                for nb in next_blocks:
                    if nb['type'] != 'p':
                        break
                    if not nb['text']:
                        continue
                    if re.match(r'^[\d০-৯]{4}', nb['text']):
                        break
                    if len(nb['text']) > 60:  # Continuation paragraph
                        rule_text += "\n" + nb['text']
                    else:
                        break

                # Determine section from boundary map if not set
                section = current_section
                if not section:
                    for sec_name, (start, end) in SECTION_BOUNDARIES.items():
                        if start <= idx <= end:
                            sec_num = re.search(r'\d+', sec_name)
                            if sec_num:
                                section = f"SECTION {sec_num.group()}"
                            break

                # Enforce section prefix validation to prevent misparses and collisions (e.g. 2626 in Sec 2, 1900 in Sec 12)
                sec_match = re.search(r'\d+', section or "")
                if sec_match:
                    sec_num = int(sec_match.group())
                    expected_prefix = f"{sec_num:02d}"
                    if not rule_id.startswith(expected_prefix):
                        # This rule ID does not belong to the current section; skip it as a misparse
                        continue

                rules.append({
                    "id": rule_id,
                    "section": section or "UNKNOWN",
                    "category": current_heading,
                    "annex": current_annex,
                    "text": rule_text
                })

        # ─── Phase 3: Extract Content from Sections 10-15 (non-rule content) ───
        # These sections have prose/table content that isn't numbered with 4-digit IDs
        print("--- Extracting Section 10-15 content ---")

        for sec_num in [10, 11, 12, 13, 14, 15]:
            sec_key = f"SECTION_{sec_num}"
            if sec_key not in SECTION_BOUNDARIES:
                continue
            start, end = SECTION_BOUNDARIES[sec_key]

            # Check if we already have rules for this section
            existing_ids = [r['id'] for r in rules if r['section'] == f'SECTION {sec_num}']

            # Extract all meaningful paragraphs from this section
            section_paras = []
            for b in blocks:
                if b['idx'] < start or b['idx'] > end:
                    continue
                if b['type'] == 'p' and b['text'] and len(b['text']) > 20:
                    # Skip structural markers
                    if b['text'].startswith('SECTION') or b['text'].startswith('ANNEX') or b['text'].startswith('CHAPTER'):
                        continue
                    if re.match(r'^\d+[A-Z]-\d+$', b['text'].strip()):  # Page markers like 11A-1
                        continue
                    section_paras.append(b)

            # For sections with few/no rules, create synthetic entries from paragraphs
            if len(existing_ids) < 3:
                para_group = []
                current_sub_heading = ""
                for b in section_paras:
                    text = b['text']
                    # Check if this is already captured as a rule
                    if re.match(r'^[\d]{4}', text):
                        continue

                    # Detect sub-headings
                    if len(text) < 100 and (text.endswith('.') or text.isupper()):
                        if para_group:
                            # Save accumulated paragraph group
                            combined = "\n".join([p['text'] for p in para_group])
                            if len(combined) > 30:
                                # Generate section-prefixed sequential IDs
                                count = len([r for r in rules if r['section'] == f'SECTION {sec_num}' and r.get('synthetic')])
                                rule_id = f"S{sec_num}-{count+1:03d}"
                                rules.append({
                                    "id": rule_id,
                                    "section": f"SECTION {sec_num}",
                                    "category": current_sub_heading,
                                    "annex": "",
                                    "text": combined,
                                    "synthetic": True
                                })
                            para_group = []
                        current_sub_heading = text
                    else:
                        para_group.append(b)

                # Flush remaining
                if para_group:
                    combined = "\n".join([p['text'] for p in para_group])
                    if len(combined) > 30:
                        count = len([r for r in rules if r['section'] == f'SECTION {sec_num}' and r.get('synthetic')])
                        rules.append({
                            "id": f"S{sec_num}-{count+1:03d}",
                            "section": f"SECTION {sec_num}",
                            "category": current_sub_heading,
                            "annex": "",
                            "text": combined,
                            "synthetic": True
                        })

        print(f"Total rules extracted: {len(rules)}")

        # ─── Phase 4: Extract Abbreviations ───
        print("\n--- Extracting Abbreviations ---")
        abbreviations = []
        seen_abbrs = set()  # For dedup

        def add_abbr(abbr, meaning, category, subcategory=""):
            """Add abbreviation with dedup and junk filtering."""
            abbr = abbr.strip()
            meaning = meaning.strip()
            if is_junk_abbreviation(abbr, meaning):
                return
            key = (abbr.upper(), meaning.upper())
            if key in seen_abbrs:
                return
            seen_abbrs.add(key)
            abbreviations.append({
                "abbreviation": abbr,
                "meaning": meaning,
                "category": category,
                "subcategory": subcategory
            })

        # ── 16A: General Abbreviations (tables) ──
        print("  Processing 16A (General Abbreviations)...")
        start_16a, end_16a = ABBR_ANNEXES["16A"]
        for b in blocks:
            if b['idx'] < start_16a or b['idx'] > end_16a:
                continue
            if b['type'] == 'tbl':
                for row in b['rows']:
                    if len(row) < 2:
                        continue
                    # Tables have format: [Meaning, Abbreviation] or [Meaning, ..., Abbreviation]
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) < 2:
                        continue

                    # Try to find meaning-abbreviation pairs
                    # Some rows have merged cells or multiple entries per row
                    # Pattern: longer text is meaning, shorter uppercase text is abbreviation
                    for j in range(0, len(cells) - 1, 2):
                        if j + 1 < len(cells):
                            c0 = cells[j]
                            c1 = cells[j + 1]
                            if len(c0) > len(c1):
                                add_abbr(c1, c0, "General Abbreviations", "16A")
                            elif len(c1) > len(c0):
                                add_abbr(c0, c1, "General Abbreviations", "16A")
                            else:
                                add_abbr(c1, c0, "General Abbreviations", "16A")

            elif b['type'] == 'p' and b['text']:
                # Some abbreviations are in paragraph form: "Full Name ABBR"
                parsed = parse_paragraph_abbreviations(b['text'])
                if parsed:
                    add_abbr(parsed[1], parsed[0], "General Abbreviations", "16A")

        # ── 16B: Multiple Meanings ──
        print("  Processing 16B (Multiple Meanings)...")
        start_16b, end_16b = ABBR_ANNEXES["16B"]
        for b in blocks:
            if b['idx'] < start_16b or b['idx'] > end_16b:
                continue
            if b['type'] == 'tbl':
                for row in b['rows']:
                    if len(row) < 2:
                        continue
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        abbr = cells[0]
                        meanings = ", ".join(cells[1:])
                        add_abbr(abbr, meanings, "Multiple Meanings", "16B")

        # ── 16C: Ranks and Appointments ──
        print("  Processing 16C (Ranks and Appointments)...")
        start_16c, end_16c = ABBR_ANNEXES["16C"]
        for b in blocks:
            if b['idx'] < start_16c or b['idx'] > end_16c:
                continue
            if b['type'] == 'tbl':
                for row in b['rows']:
                    if len(row) < 2:
                        continue
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        # Usually: [Rank/Title, Abbreviation] or [Rank/Title, ..., Abbreviation]
                        meaning = cells[0]
                        abbr = cells[-1]
                        if len(meaning) > len(abbr):
                            add_abbr(abbr, meaning, "Ranks and Appointments", "16C")
                        else:
                            add_abbr(meaning, abbr, "Ranks and Appointments", "16C")

        # ── 16D: National Distinguishing Letters ──
        print("  Processing 16D (National Distinguishing Letters)...")
        start_16d, end_16d = ABBR_ANNEXES["16D"]
        for b in blocks:
            if b['idx'] < start_16d or b['idx'] > end_16d:
                continue
            if b['type'] == 'tbl':
                for row in b['rows']:
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        # Country, Letter pairs
                        for j in range(0, len(cells) - 1, 2):
                            if j + 1 < len(cells):
                                add_abbr(cells[j + 1], cells[j], "National Distinguishing Letters", "16D")

        # ── 16E: Training Institutions ──
        print("  Processing 16E (Training Institutions)...")
        start_16e, end_16e = ABBR_ANNEXES["16E"]
        for b in blocks:
            if b['idx'] < start_16e or b['idx'] > end_16e:
                continue
            if b['type'] == 'tbl':
                for row in b['rows']:
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        name = cells[0]
                        abbr = cells[-1]
                        if name.lower() in ('name of training institute', 'abbreviation', 'serial'):
                            continue
                        if len(name) > len(abbr):
                            add_abbr(abbr, name, "Training Institutions", "16E")
                        else:
                            add_abbr(name, abbr, "Training Institutions", "16E")

        # ── 16F: Regiments and Corps (paragraph-based) ──
        print("  Processing 16F (Regiments and Corps)...")
        start_16f, end_16f = ABBR_ANNEXES["16F"]
        current_corps = ""
        for b in blocks:
            if b['idx'] < start_16f or b['idx'] > end_16f:
                continue
            if b['type'] == 'p' and b['text']:
                text = b['text'].strip()
                if not text or text.startswith('ANNEX') or text.startswith('SECTION') or re.match(r'^\d+[A-Z]-\d+$', text):
                    continue
                if text == 'REGIMENTS AND CORPS IN THE ARMY' or text == 'Unit/Regiment/Sub-unit     Abbreviation':
                    continue

                # Detect corps headings (end with period, e.g. "Armoured Corps.    AC")
                parsed = parse_paragraph_abbreviations(text)
                if parsed:
                    add_abbr(parsed[1], parsed[0], "Regiments and Corps", "16F")
                elif text.endswith('.') and len(text) < 50:
                    current_corps = text.rstrip('.')
            elif b['type'] == 'tbl':
                for row in b['rows']:
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        add_abbr(cells[-1], cells[0], "Regiments and Corps", "16F")

        # ── 16G: Navy Units (paragraph-based) ──
        print("  Processing 16G (Navy Units)...")
        start_16g, end_16g = ABBR_ANNEXES["16G"]
        current_nav_cat = ""
        for b in blocks:
            if b['idx'] < start_16g or b['idx'] > end_16g:
                continue
            if b['type'] == 'p' and b['text']:
                text = b['text'].strip()
                if not text or text.startswith('ANNEX') or text.startswith('SECTION') or re.match(r'^\d+[A-Z]-\d+$', text):
                    continue
                if text == 'BASES, UNITS AND BRANCHES OF BANGLADESH NAVY':
                    continue

                # Detect category headings (end with period)
                if text.endswith('.') and len(text) < 40:
                    current_nav_cat = text.rstrip('.')
                    continue

                parsed = parse_paragraph_abbreviations(text)
                if parsed:
                    add_abbr(parsed[1], parsed[0], f"Bangladesh Navy - {current_nav_cat}" if current_nav_cat else "Bangladesh Navy", "16G")
            elif b['type'] == 'tbl':
                for row in b['rows']:
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        add_abbr(cells[-1], cells[0], "Bangladesh Navy", "16G")

        # ── 16H: Air Force Units ──
        print("  Processing 16H (Air Force Units)...")
        start_16h, end_16h = ABBR_ANNEXES["16H"]
        current_af_cat = ""
        for b in blocks:
            if b['idx'] < start_16h or b['idx'] > end_16h:
                continue
            if b['type'] == 'p' and b['text']:
                text = b['text'].strip()
                if not text or text.startswith('ANNEX') or text.startswith('SECTION') or re.match(r'^\d+[A-Z]-\d+$', text):
                    continue

                if text.endswith('.') and len(text) < 50:
                    current_af_cat = text.rstrip('.')
                    continue

                parsed = parse_paragraph_abbreviations(text)
                if parsed:
                    add_abbr(parsed[1], parsed[0],
                             f"Bangladesh Air Force - {current_af_cat}" if current_af_cat else "Bangladesh Air Force", "16H")
            elif b['type'] == 'tbl':
                for row in b['rows']:
                    cells = [c.strip() for c in row if c.strip()]
                    if len(cells) >= 2:
                        add_abbr(cells[-1], cells[0], "Bangladesh Air Force", "16H")

        # ── Bangla Abbreviations (Part I) ──
        print("  Processing Bangla abbreviations (Part I)...")
        for tbl_idx in BANGLA_ABBR_TABLES:
            b = idx_to_block.get(tbl_idx)
            if not b or b['type'] != 'tbl':
                continue
            for row in b['rows']:
                if len(row) < 3:
                    continue
                # Format: [Serial, English, Bangla]
                serial = row[0].strip()
                english = row[1].strip() if len(row) > 1 else ""
                bangla = row[2].strip() if len(row) > 2 else ""

                # Skip header rows
                if serial.lower() in ('ser', 'serial', '') or english.lower() in ('english', ''):
                    continue
                if not english or not bangla:
                    continue

                add_abbr(english, bangla, "Bangla Abbreviations", "Part_I")

        print(f"Total abbreviations: {len(abbreviations)}")

        # ─── Phase 5: Extract Templates ───
        print("\n--- Extracting Templates ---")
        templates = []

        # Extract templates from annexes containing examples/formats
        for sec_name, (start, end) in SECTION_BOUNDARIES.items():
            sec_match = re.search(r'\d+', sec_name)
            if not sec_match:
                continue
            sec_num = int(sec_match.group())

            sec_blocks = [b for b in blocks if start <= b['idx'] <= end]
            sec_templates = []

            i = 0
            n = len(sec_blocks)
            while i < n:
                b = sec_blocks[i]
                if b['type'] == 'p' and b['text']:
                    text = b['text'].strip()
                    
                    if is_valid_annex_start(text):
                        text_upper = text.upper()
                        # Filter out inline references
                        is_false = False
                        for ref in ['SEE PARAGRAPH', 'SEE ANNEX', 'IS AT ANNEX', 'ARE AT ANNEX', 'ARE GIVEN AT', 'SHOWN IN', 'LISTED AT', 'GIVEN AT', 'REFER TO', 'REFERRED TO', 'INSERTED IN', 'OMITTED FOR', 'SEE ALSO', 'FOR INDENTING']:
                            if ref in text_upper:
                                is_false = True
                                break
                        if text_upper.startswith('FOR ') or text_upper.startswith('IF AN ') or text_upper.startswith('THIS ANNEX'):
                            is_false = True
                        if 'CONTENTS' in text_upper or 'LIST OF' in text_upper:
                            is_false = True
                            
                        if not is_false:
                            # Found a template header start!
                            header_lines = [text]
                            j = i + 1
                            
                            descriptive_title = ""
                            last_header_idx = i
                            
                            # Standalone special headings need no lookahead
                            if text_upper in ['EXAMPLE OF A COMMANDED LETTER', 'EXAMPLE OF A DIRECTED LETTER', 'EXAMPLE OF A ROUTINE LETTER']:
                                descriptive_title = text
                                
                            if not descriptive_title:
                                while j < i + 6 and j < n:
                                    next_b = sec_blocks[j]
                                    if next_b['type'] == 'p':
                                        next_text = next_b['text'].strip()
                                        if not next_text:
                                            j += 1
                                            continue
                                        
                                        # If it looks like a numbered paragraph, stop lookahead
                                        if re.match(r'^\d{4}\.', next_text) or re.match(r'^\d+\.', next_text):
                                            break
                                            
                                        next_upper = next_text.upper()
                                        
                                        # Check if it is a prefix continuation line
                                        is_prefix_continuation = False
                                        if any(w in next_upper for w in ['ANNEX', 'APPENDIX', 'SECTION', 'TO', 'SECRET']) and len(next_text) < 80:
                                            is_prefix_continuation = True
                                        elif re.match(r'^\d+[A-Z]-\d+$', next_text):
                                            is_prefix_continuation = True
                                        elif re.match(r'^\d+[A-Z]\d+-\d+$', next_text):
                                            is_prefix_continuation = True
                                            
                                        if is_prefix_continuation:
                                            header_lines.append(next_text)
                                            last_header_idx = j
                                            j += 1
                                        else:
                                            # It's not a prefix line, so it must be the descriptive title!
                                            # Ensure it is short enough and doesn't start another annex
                                            if len(next_text) < 120 and not is_valid_annex_start(next_text):
                                                descriptive_title = next_text
                                                header_lines.append(next_text)
                                                last_header_idx = j
                                            break
                                    else:
                                        break
                                        
                            # Combine header lines
                            unique_lines = []
                            for line in header_lines:
                                if line not in unique_lines:
                                    unique_lines.append(line)
                                    
                            prefix_parts = [l for l in unique_lines if l != descriptive_title]
                            prefix = " ".join(prefix_parts)
                            prefix = re.sub(r'\s+', ' ', prefix).strip()
                            
                            if descriptive_title:
                                descriptive_title = re.sub(r'\s+', ' ', descriptive_title).strip()
                                if prefix:
                                    full_title = f"{prefix} - {descriptive_title}"
                                else:
                                    full_title = descriptive_title
                            else:
                                full_title = prefix
                                
                            sec_templates.append({
                                "section": sec_num,
                                "title": full_title,
                                "start_idx": sec_blocks[i]['idx'],
                                "end_idx": sec_blocks[last_header_idx]['idx']
                            })
                            
                            i = last_header_idx + 1
                            continue
                i += 1

            # Extract content for each template in the section
            for idx_t, t in enumerate(sec_templates):
                content_start = t["end_idx"] + 1
                if idx_t + 1 < len(sec_templates):
                    content_end = sec_templates[idx_t + 1]["start_idx"] - 1
                else:
                    content_end = end

                annex_content = []
                for idx_b in range(content_start, content_end + 1):
                    b = idx_to_block.get(idx_b)
                    if not b:
                        continue
                    if b['type'] == 'p' and b['text']:
                        text = b['text'].strip()
                        if text.upper().startswith('SECTION') and len(text) < 50:
                            continue
                        if re.match(r'^\d+[A-Z]-\d+$', text):
                            continue
                        annex_content.append({"type": "paragraph", "text": text})
                    elif b['type'] == 'tbl':
                        annex_content.append({"type": "table", "rows": b['rows'][:30]})

                # Classify template type from title
                title_upper = t["title"].upper()
                if 'APPENDIX' in title_upper:
                    tpl_type = 'appendix'
                elif 'ANNEX' in title_upper and not any(kw in title_upper for kw in ['EXAMPLE', 'SPECIMEN', 'LAYOUT', 'FORMAT', 'FRAMEWORK']):
                    tpl_type = 'annex'
                elif 'SPECIMEN' in title_upper:
                    tpl_type = 'specimen'
                elif 'LAYOUT' in title_upper or 'OUTLINE' in title_upper:
                    tpl_type = 'layout'
                elif 'FORMAT' in title_upper or 'FRAMEWORK' in title_upper:
                    tpl_type = 'format'
                elif 'MEMORANDUM' in title_upper:
                    tpl_type = 'memorandum'
                elif 'LETTER' in title_upper and 'EXAMPLE' not in title_upper:
                    tpl_type = 'letter'
                elif 'CORRESPONDENCE' in title_upper:
                    tpl_type = 'correspondence'
                elif 'SAMPLE' in title_upper:
                    tpl_type = 'sample'
                elif 'MODEL' in title_upper:
                    tpl_type = 'model'
                else:
                    tpl_type = 'example'

                # Extract annex reference (e.g. "ANNEX B TO SECTION 11")
                annex_ref = ""
                annex_match = re.search(r'(ANNEX\s+[A-Z]\d*)\s+(?:TO\s+)?(?:SECTION\s+\d+)?', title_upper)
                if annex_match:
                    annex_ref = annex_match.group(1)
                appendix_match = re.search(r'(APPENDIX\s+\d+)\s+(?:TO\s+)?', title_upper)
                if appendix_match:
                    annex_ref = appendix_match.group(1)

                # Filter obvious non-template noise
                noise_indicators = [
                    "THE VERB", "IS USED ONLY", "WRONG EXAMPLE", "CORRECT EXAMPLE",
                    "LETTERED CONSECUTIVELY", "REFERRED TO IN THE TEXT",
                    "COPY NUMBERED", "NUMBERING OF"
                ]
                if any(ni in title_upper for ni in noise_indicators):
                    continue

                templates.append({
                    "section": sec_num,
                    "title": t["title"],
                    "type": tpl_type,
                    "annex": annex_ref,
                    "content": annex_content[:50]
                })

        print(f"Total templates: {len(templates)}")

        # ─── Phase 6: Extract Symbols (Sections 17-19) ───
        print("\n--- Extracting Symbols ---")
        symbols = []

        for sec_num in [17, 18, 19]:
            sec_key = f"SECTION_{sec_num}"
            if sec_key not in SECTION_BOUNDARIES:
                continue
            start, end = SECTION_BOUNDARIES[sec_key]

            sec_name = {17: "Army Symbols", 18: "Naval Symbols", 19: "Air Force Symbols"}[sec_num]
            current_annex_title = ""

            for b in blocks:
                if b['idx'] < start or b['idx'] > end:
                    continue

                if b['type'] == 'p' and b['text']:
                    text = b['text']
                    if 'ANNEX' in text and len(text) < 100:
                        current_annex_title = text
                    rule_match = re.match(r'^(\d{4})[.\s]\s*(.*)', text)
                    if rule_match:
                        rules.append({
                            "id": rule_match.group(1),
                            "section": f"SECTION {sec_num}",
                            "category": sec_name,
                            "annex": current_annex_title,
                            "text": rule_match.group(2)
                        })

                elif b['type'] == 'tbl':
                    for row in b['rows']:
                        cells = [c.strip() for c in row if c.strip()]
                        if len(cells) >= 2:
                            symbols.append({
                                "section": sec_num,
                                "service": sec_name,
                                "annex": current_annex_title,
                                "description": cells[1] if len(cells) > 1 else cells[0],
                                "details": cells
                            })

        print(f"Total symbols: {len(symbols)}")

        for r in rules:
            r.pop('synthetic', None)

        def sort_key(r):
            sec = re.search(r'\d+', r['section'])
            sec_num = int(sec.group()) if sec else 0
            rid = r['id']
            if rid.startswith('S') and '-' in rid:
                id_num = 90000 + int(rid.split('-')[1])
            else:
                try:
                    id_num = int(rid)
                except ValueError:
                    id_num = 0
            return (sec_num, id_num)

        rules.sort(key=sort_key)

        seen_rules = set()
        unique_rules = []
        for r in rules:
            key = (r['id'], r['section'])
            if key not in seen_rules:
                seen_rules.add(key)
                unique_rules.append(r)
        rules = unique_rules

        vocab = [
            {"english": "TOP SECRET", "bangla": "অতি গোপনীয়", "category": "Security Classification"},
            {"english": "SECRET", "bangla": "বিশেষ গোপনীয়", "category": "Security Classification"},
            {"english": "CONFIDENTIAL", "bangla": "গোপনীয়", "category": "Security Classification"},
            {"english": "RESTRICTED", "bangla": "সীমিত", "category": "Security Classification"},
            {"english": "UNCLASSIFIED", "bangla": "অশ্রেণীবদ্ধ", "category": "Security Classification"},
            {"english": "IN CONFIDENCE", "bangla": "ব্যক্তিগত গোপনীয়", "category": "Privacy Marking"},
            {"english": "IMMEDIATE", "bangla": "জরুরি", "category": "Precedence"},
            {"english": "PRIORITY", "bangla": "অগ্রগণ্য", "category": "Precedence"},
            {"english": "Top Priority", "bangla": "সর্বোচ্চ অগ্রাধিকার", "category": "Civil Precedence"},
            {"english": "Immediate", "bangla": "অবিলম্বে", "category": "Civil Precedence"},
            {"english": "Urgent", "bangla": "জরুরি", "category": "Civil Precedence"}
        ]

        from collections import defaultdict
        abbr_map = defaultdict(list)
        for a in abbreviations:
            abbr_map[a['abbreviation'].upper()].append(a)
        for upper_abbr, entries in abbr_map.items():
            unique_meanings = list(dict.fromkeys(e['meaning'] for e in entries))
            if len(unique_meanings) > 1:
                has_16b = any(e['subcategory'] == '16B' for e in entries)
                if not has_16b:
                    meanings_str = ", ".join(unique_meanings)
                    orig_abbr = entries[0]['abbreviation']
                    abbreviations.append({
                        "abbreviation": orig_abbr,
                        "meaning": meanings_str,
                        "category": "Multiple Meanings",
                        "subcategory": "16B"
                    })

        db = {
            "metadata": {
                "source": "JSSDM 2022 (JSP-001)",
                "extracted": "2026-05-30",
                "version": "2.0",
                "sections": 19
            },
            "rules": rules,
            "abbreviations": abbreviations,
            "templates": templates,
            "symbols": symbols,
            "vocab": vocab
        }

        output_path = "jssdm_database.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)

        print("\nEXTRACTION SUMMARY")
        print("Rules:         ", len(rules))
        print("Abbreviations: ", len(abbreviations))
        print("Templates:     ", len(templates))
        print("Symbols:       ", len(symbols))

        sec_counts = Counter(r['section'] for r in rules)
        print("\nRules by section:")
        for sec in sorted(sec_counts.keys(), key=lambda s: int(re.search(r'\d+', s).group()) if re.search(r'\d+', s) else 0):
            print("  {}: {}".format(sec, sec_counts[sec]))


        tpl_types = Counter(t['type'] for t in templates)
        print("\nTemplates by type:")
        for tp in sorted(tpl_types.keys()):
            print("  {}: {}".format(tp, tpl_types[tp]))

        print("\nSaved to", output_path)


if __name__ == "__main__":
    main()
