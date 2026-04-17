import os
import re
from datetime import datetime
import warnings
from langdetect import detect, LangDetectException
from underthesea import word_tokenize
from transformers import pipeline

# Tắt cảnh báo rườm rà của HuggingFace trên terminal
warnings.filterwarnings("ignore", category=UserWarning)

def load_stopwords(path: str = "stopwords_vi.txt") -> set[str]:
    """TODO 1: Đọc stopwords từ file ngoài, trả về set."""
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return set(line.strip().lower() for line in f if line.strip())
    # Fallback dự phòng chống crash nếu mất file
    return {"và", "là", "của", "có", "trong", "những", "các", "cho", "để", "thì", "mà", "với"}

STOPWORDS = load_stopwords()
EMOJI_MAP = {"positive": "😊", "negative": "😟", "neutral": "😐"}

try:
    print("⏳ Đang tải mô hình PhoBERT AI dành riêng cho tiếng Việt...")
    sentiment_model = pipeline(
        "sentiment-analysis", 
        model="wonrax/phobert-base-vietnamese-sentiment"
    )
    print("✅ Tải mô hình thành công!")
except Exception as e:
    sentiment_model = None
    print(f"❌ Lỗi load model: {e}")
# ====================================================

def detect_language(text: str) -> str:
    """TODO 9: Detect ngôn ngữ."""
    try:
        return detect(text)
    except LangDetectException:
        return "unknown"

def analyze_feedback(text: str) -> dict:
    """Phân tích cảm xúc + trích xuất từ khóa (Giải quyết trọn vẹn TODO 8 & 13)."""
    clean_text = text.strip()
    
    # TODO 13: Xử lý edge case
    if not clean_text or len(clean_text) <= 2 or not re.search(r'\w', clean_text):
        return {
            "text": text,
            "sentiment": "neutral",
            "confidence": 1.0, 
            "keywords": [],
            "language": detect_language(clean_text) if clean_text else "unknown",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    lang = detect_language(clean_text)
    
    # 1. ĐO CẢM XÚC BẰNG PHO-BERT (TODO 8)
    if sentiment_model:
        try:
            hf_result = sentiment_model(clean_text)[0]
            raw_label = hf_result["label"].upper()
            
            # Chuyển đổi nhãn của PhoBERT (POS, NEG, NEU) về dạng chuẩn của app
            label_map = {"POS": "positive", "NEG": "negative", "NEU": "neutral"}
            sent = label_map.get(raw_label, "neutral")
            
            confidence = hf_result["score"]
        except Exception:
            sent = "neutral"
            confidence = 0.5
    else:
        sent = "neutral"
        confidence = 0.5
        
    # 2. TRÍCH XUẤT TỪ KHÓA BẰNG NLP (Tách khối try...except độc lập)
    keywords = []
    if lang == "vi":
        try:
            tokens = word_tokenize(clean_text)
            keywords = [t.lower() for t in tokens if t.lower() not in STOPWORDS and len(t) > 1 and re.match(r'\w+', t)]
        except Exception:
            pass
    elif lang == "en":
        # Fallback keyword extraction đơn giản cho tiếng Anh
        keywords = [w.lower() for w in re.findall(r'\w+', clean_text) if len(w) > 3]
        
    if sent not in ["positive", "negative", "neutral"]:
        sent = "neutral"
        
    return {
        "text": text,
        "sentiment": sent,
        "confidence": confidence,
        "keywords": keywords,
        "language": lang,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

def render_analysis(result: dict) -> str:
    """Hiển thị markdown kết quả với % độ tin cậy."""
    emoji = EMOJI_MAP.get(result["sentiment"], "😐")
    kw = ", ".join(result["keywords"]) if result["keywords"] else "Không có"
    conf_percent = result['confidence'] * 100
    
    return f"""**Kết quả phân tích:**
- **Ngôn ngữ:** `{result['language']}`
- **Cảm xúc:** {result['sentiment'].capitalize()} {emoji} *(Độ tin cậy: {conf_percent:.1f}%)*
- **Từ khóa:** {kw}"""