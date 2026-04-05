import re

def _clean_and_summarize(text: str) -> str:
    text = re.sub(r'\[Source \d+: [^\]]+\]\n?', '', text)
    text = re.sub(r'[-—_|\*#]+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.replace(' ,', ',').replace(' .', '.').replace(' )', ')').replace('( ', '(')
    text = re.sub(r'^[^\w]+', '', text)
    
    sentences = re.split(r'(?<=[.!?])\s+', text)
    valid_sentences = [s.strip() for s in sentences if len(s.strip()) > 15]
    
    if not valid_sentences:
        return text[:200] + "..."
        
    out = "After analyzing the authorized documents, here is the summarized intelligence:\n\n"
    for s in valid_sentences[:3]:
        s = re.sub(r'^\d+\s*[\.\)]?\s*', '', s)
        s = s.strip()
        if not s: continue
        s = s[0].upper() + s[1:]
        if not s.endswith('.'): s += '.'
        out += f"• {s}\n"
        
    return out

raw = "recruitment , training ) saw a 10 % increase . While employee growth is essential , optimizing benefits packages and hiring processes could reduce per-employee cost . 4 . Other Operational Expenses - A mix of general operational and administrative expenses totaling $ 15M , with a notable increase in travel and miscellaneous office costs , which grew by 8 % year-over-year . Cash Flow Analysis : — —— — — - — —— —— - — —— — —— —— - FinSolve Technologies s ca..."
print(_clean_and_summarize(raw))
