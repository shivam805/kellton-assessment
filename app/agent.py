
import language_tool_python
import textstat
import re
from typing import List, Tuple, Dict
import spacy

tool = language_tool_python.LanguageToolPublicAPI('en-US')
nlp = spacy.load('en_core_web_sm')

BANNED_PHRASES = {'very', 'basically', 'literally', 'obviously'}

def analyze_text(text: str) -> Dict:
    doc = nlp(text)
    sentences = list(doc.sents)
    passive_cnt = sum(1 for s in sentences if has_passive(s))
    avg_len = sum(len(s.text.split()) for s in sentences) / max(1, len(sentences))
    flesch = textstat.flesch_reading_ease(text)
    fk = textstat.flesch_kincaid_grade(text)

    matches = tool.check(text)
    violations = []
    for m in matches:
        violations.append({
            'id': m.ruleId,
            'type': m.category,
            'message': m.message,
            'span': text[m.offset:m.offset+m.errorLength],
            'suggestion': (m.replacements or [""])[0]
        })

    for phrase in BANNED_PHRASES:
        for hit in re.finditer(rf"\b({re.escape(phrase)})\b", text, flags=re.I):
            violations.append({
                'id': "STYLE_BANNED",
                'type': "style",
                'message': f"Discouraged word: '{phrase}'",
                'span': phrase,
                'suggestion': "Remove or replace with a stronger term."
            })

    overall = score_overall(len(violations), passive_cnt, avg_len, flesch, fk)
    return {
        "summary": {"overall_compliance": overall, "grade": letter_grade(overall)},
        "metrics": {
            "readability": {'flesch': flesch, "fk_grade": fk},
            "style": {'passive_ratio': passive_cnt/max(1,len(sentences)), 'avg_sentence_len': avg_len},
        },
        "violations": violations
    }

def has_passive(span) -> bool:
    lemmas = [t.lemma_.lower() for t in span]
    return any(t.tag_ == "VBN" for t in span) and any(l in {"be"} for l in lemmas)

def score_overall(num, passive, avg_len, flesch, fk):
    p = max(0, 1 - (num/100)) * 0.5
    s = max(0, 1 - min(passive/10, 1)) * 0.2
    r = min(max((flesch/100), 0), 1) * 0.3
    return round(p + s + r, 2)

def letter_grade(score):
    return "A" if score >= 0.9 else "B" if score >= 0.8 else "C" if score >= 0.7 else "D" if score >= 0.6 else "F"

def modify_text(text: str, rules: List[str]) -> Tuple[str, List[Dict]]:
    matches = tool.check(text)
    changes = []
    out = text
    offset = 0
    for m in matches:
        if m.replacements:
            start, end = m.offset, m.offset + m.errorLength
            suggestion = m.replacements[0]
            changes.append({'from': out[start+offset:end+offset], "to": suggestion, "pos": [start+offset, end+offset]})
            out = out[:start+offset] + suggestion + out[end+offset:]
            offset += len(suggestion) - (end - start)

    for phrase in BANNED_PHRASES:
        out = re.sub(rf"\b({re.escape(phrase)})\b", "", out, flags=re.I)

    return out, changes
