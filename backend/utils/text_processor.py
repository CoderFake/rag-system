import re
import unicodedata
from typing import List, Dict, Any, Optional
import logging
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords

logger = logging.getLogger(__name__)


try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

def clean_text(text: str) -> str:
    if not text:
        return ""
        
    text = unicodedata.normalize('NFKC', text)
    text = re.sub(r'[^\w\s.,?!;:()\[\]"\'%$#@&*+-]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def normalize_unicode(text: str) -> str:
    return unicodedata.normalize('NFKC', text) if text else ""

def detect_language(text: str) -> str:

    if not text:
        return "vi" 
        

    vn_chars = set('àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ')
    
    sample = text.lower()[:1000]
    

    vn_count = sum(1 for c in sample if c in vn_chars)
    vn_ratio = vn_count / len(sample) if sample else 0
    

    return "vi" if vn_ratio > 0.01 else "en"

def tokenize_text(text: str, language: str = "vi") -> List[str]:
    if not text:
        return []
    
    text = clean_text(text)
    
    return word_tokenize(text)

def remove_stopwords(tokens: List[str], language: str = "vi") -> List[str]:
    if not tokens:
        return []
    
    lang = "vietnamese" if language == "vi" else "english"
    try:
        stop_words = set(stopwords.words(lang))
    except:
        stop_words = set()
    

    if language == "vi":
        additional_stopwords = {"của", "và", "các", "có", "được", "những", "rằng", "cho", "này", "đó", "lại"}
        stop_words.update(additional_stopwords)
    

    return [token for token in tokens if token.lower() not in stop_words]

def extract_keywords(text: str, language: str = "vi", top_n: int = 10) -> List[str]:

    if not text:
        return []
    
    tokens = tokenize_text(text, language)
    
    tokens = remove_stopwords(tokens, language)
    
    freq = {}
    for token in tokens:
        if len(token) > 1:
            token = token.lower()
            freq[token] = freq.get(token, 0) + 1
    

    keywords = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:top_n]
    

    return [keyword for keyword, _ in keywords]

def split_into_sentences(text: str, language: str = "vi") -> List[str]:
    if not text:
        return []
    
    text = normalize_unicode(text)

    return sent_tokenize(text)