import streamlit as st
import joblib
import string
import pymorphy3
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from langdetect import detect
import os

# Скачиваем NLTK-данные при первом запуске
try:
    nltk.data.find('corpora/stopwords')
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('stopwords', quiet=True)
    nltk.download('wordnet', quiet=True)

@st.cache_resource
def load_nlp_resources():
    morph = pymorphy3.MorphAnalyzer()
    lemmatizer = WordNetLemmatizer()
    ru_stops = set(stopwords.words('russian'))
    en_stops = set(stopwords.words('english'))
    return morph, lemmatizer, ru_stops, en_stops

def preprocess_text(text, morph, lemmatizer, ru_stops, en_stops):
    if not isinstance(text, str) or not text.strip():
        return ""
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    try:
        lang = detect(text)
    except:
        lang = 'en'
        
    words = text.split()
    if lang == 'ru':
        words = [w for w in words if w not in ru_stops]
        words = [morph.parse(w)[0].normal_form for w in words]
    else:
        words = [w for w in words if w not in en_stops]
        words = [lemmatizer.lemmatize(w) for w in words]
    return ' '.join(words)

@st.cache_resource
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model_logreg.pkl")
    vec_path = os.path.join(os.path.dirname(__file__), "vectorizer_tfidf.pkl")
    
    if not os.path.exists(model_path) or not os.path.exists(vec_path):
        st.error("Не найдены файлы model_logreg.pkl или vectorizer_tfidf.pkl")
        st.stop()
        
    return joblib.load(model_path), joblib.load(vec_path)

def predict(text_raw):
    morph, lemmatizer, ru_stops, en_stops = load_nlp_resources()
    model, vectorizer = load_model()
    
    cleaned = preprocess_text(text_raw, morph, lemmatizer, ru_stops, en_stops)
    if not cleaned.strip():
        return None, 0.0, "Текст слишком короткий или пуст"
        
    vec = vectorizer.transform([cleaned])
    pred = model.predict(vec)[0]
    prob = model.predict_proba(vec)[0].max()
    return pred, prob, cleaned

# ---------------- UI STREAMLIT ----------------
st.set_page_config(page_title="Детектор фейков", page_icon="🔍", layout="centered")

st.title("🔍 Детектор фейковых новостей")
st.caption("Модель: Logistic Regression + TF-IDF | Точность: ~97.8% | Языки: RU / EN")

text_input = st.text_area(
    "Вставьте заголовок или полный текст новости:",
    height=180,
    placeholder="Например: Учёные доказали, что шоколад лечит все болезни..."
)

if st.button("🔎 Проверить достоверность", type="primary", use_container_width=True):
    if not text_input.strip():
        st.warning("⚠️ Пожалуйста, введите текст для анализа.")
    else:
        with st.spinner("🔄 Анализирую текст..."):
            pred, prob, cleaned = predict(text_input)
            
        if pred is None:
            st.error(f"❌ {cleaned}")
        else:
            verdict = "✅ НАСТОЯЩАЯ НОВОСТЬ" if pred == 0 else "ФЕЙКОВАЯ НОВОСТЬ"
            color = "green" if pred == 0 else "red"
            
            st.markdown(f"### Вердикт: <span style='color:{color}; font-weight:bold'>{verdict}</span>", unsafe_allow_html=True)
            
            cols = st.columns(2)
            cols[0].metric("Уверенность модели", f"{prob:.1%}")
            cols[1].metric("Обработано слов", len(cleaned.split()))
            
            with st.expander("📝 Показать предобработанный текст"):
                st.code(cleaned, language="text")

st.sidebar.markdown("---")
st.sidebar.info("💡 **Совет:**\nМодель лучше всего работает с текстами от 10 слов. Спам или случайный набор символов могут снижать точность.")
st.sidebar.caption("Разработано на базе Logistic Regression + TF-IDF")