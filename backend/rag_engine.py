# rag_engine.py

import os
import re
import pickle
import faiss
import numpy as np

from sentence_transformers import SentenceTransformer

try:
    import google.generativeai as genai
except ImportError:
    genai = None


# ===============================
# File paths
# ===============================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

INDEX_PATH = os.path.join(BASE_DIR, "uniguide_faq.index")
METADATA_PATH = os.path.join(BASE_DIR, "uniguide_faq_metadata.pkl")


# ===============================
# Embedding model
# ===============================

MODEL_NAME = "intfloat/multilingual-e5-large"
embedding_model = SentenceTransformer(MODEL_NAME)


# ===============================
# Load FAISS index and metadata
# ===============================

if not os.path.exists(INDEX_PATH):
    raise FileNotFoundError(f"FAISS index not found: {INDEX_PATH}")

if not os.path.exists(METADATA_PATH):
    raise FileNotFoundError(f"Metadata file not found: {METADATA_PATH}")

index = faiss.read_index(INDEX_PATH)

with open(METADATA_PATH, "rb") as f:
    metadata = pickle.load(f)


# ===============================
# Gemini setup
# ===============================

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

llm = None

if GOOGLE_API_KEY and genai is not None:
    genai.configure(api_key=GOOGLE_API_KEY)
    llm = genai.GenerativeModel("gemini-2.5-flash")


# ===============================
# Text normalization
# ===============================

def normalize_text(text):
    if not isinstance(text, str):
        return ""

    text = text.strip().lower()

    arabic_diacritics = re.compile(r"[\u0617-\u061A\u064B-\u0652]")
    text = re.sub(arabic_diacritics, "", text)

    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ة", "ه", text)
    text = re.sub("ؤ", "و", text)
    text = re.sub("ئ", "ي", text)

    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def detect_language(text):
    if not isinstance(text, str):
        return "en"

    arabic_chars = re.findall(r"[\u0600-\u06FF]", text)

    if len(arabic_chars) > 0:
        return "ar"

    return "en"


def detect_lang(text):
    return detect_language(text)


def has_arabic(text):
    return bool(re.search(r"[\u0600-\u06FF]", str(text)))


# ===============================
# Query expansion
# ===============================

def expand_query(question):
    q = normalize_text(question)

    synonym_map = {
        "قبول": ["تسجيل", "admission", "registration", "requirements"],
        "تسجيل": ["قبول", "admission", "registration"],
        "admission": ["قبول", "تسجيل", "شروط القبول", "registration"],
        "registration": ["قبول", "تسجيل", "admission"],
        "requirements": ["شروط", "متطلبات", "شروط القبول"],

        "تخصص": ["تخصصات", "برنامج", "برامج", "major", "program"],
        "تخصصات": ["تخصص", "برامج", "majors", "programs"],
        "major": ["تخصص", "تخصصات", "program"],
        "majors": ["تخصص", "تخصصات", "programs"],
        "program": ["تخصص", "برنامج", "major"],
        "programs": ["تخصصات", "برامج", "majors"],

        "computer": ["حاسب", "الحاسب", "علوم الحاسب", "computer science"],
        "computer science": ["علوم الحاسب", "كلية علوم وهندسة الحاسب"],
        "cs": ["علوم الحاسب", "حاسب"],
        "ai": ["ذكاء اصطناعي", "الذكاء الاصطناعي", "artificial intelligence"],
        "artificial": ["ذكاء اصطناعي", "الذكاء الاصطناعي"],
        "artificial intelligence": ["ذكاء اصطناعي", "الذكاء الاصطناعي"],
        "cybersecurity": ["الأمن السيبراني", "امن سيبراني"],
        "data science": ["علوم البيانات"],
        "software engineering": ["هندسة البرمجيات"],

        "رسوم": ["تكلفة", "مبلغ", "fee", "fees", "tuition"],
        "تكلفه": ["رسوم", "fee", "fees", "tuition"],
        "تكلفة": ["رسوم", "fee", "fees", "tuition"],
        "fee": ["رسوم", "تكلفة", "tuition"],
        "fees": ["رسوم", "تكلفة", "tuition"],
        "tuition": ["رسوم", "تكلفة"],

        "دبلوم": ["دبلومات", "diploma"],
        "دبلومات": ["دبلوم", "diplomas"],
        "diploma": ["دبلوم", "دبلومات"],
        "diplomas": ["دبلوم", "دبلومات"],

        "مسار": ["مسارات", "track", "pathway"],
        "مسارات": ["مسار", "tracks", "pathways"],
        "track": ["مسار", "مسارات"],
        "tracks": ["مسارات"],
        "pathway": ["مسار", "مسارات"],
        "pathways": ["مسارات"],

        "سنه": ["عام", "year"],
        "سنة": ["عام", "year"],
        "التاهيليه": ["السنة التأهيلية", "preparatory year"],
        "التأهيلية": ["السنة التأهيلية", "preparatory year"],
        "preparatory": ["السنة التأهيلية", "التاهيلية"],
        "preparatory year": ["السنة التأهيلية", "التاهيلية"],

        "كلية": ["كليات", "college", "faculty"],
        "كليات": ["كلية", "colleges", "faculties"],
        "college": ["كلية", "كليات"],
        "colleges": ["كلية", "كليات"],

        "عدد": ["كم", "number", "count"],
        "كم": ["عدد", "number", "count"],
        "number": ["عدد", "كم"],
        "count": ["عدد", "كم"],

        "طوارئ": ["emergency", "حالة طارئة"],
        "emergency": ["طوارئ", "حالة طارئة"],
        "دعم": ["support", "technical support"],
        "support": ["دعم", "مساعدة"],
        "contact": ["تواصل", "اتصال", "email", "phone"],

        "مرتبه": ["مرتبة", "honor", "honors"],
        "مرتبة": ["مرتبه", "honor", "honors"],
        "شرف": ["مرتبة الشرف", "honors"],
        "honor": ["مرتبة الشرف", "شرف"],
        "honors": ["مرتبة الشرف", "شرف"],
    }

    phrase_map = {
        "computer science": ["علوم الحاسب", "كلية علوم وهندسة الحاسب"],
        "artificial intelligence": ["الذكاء الاصطناعي", "تخصص الذكاء الاصطناعي"],
        "preparatory year": ["السنة التأهيلية"],
        "university of jeddah": ["جامعة جدة"],
        "technical support": ["الدعم الفني"],
    }

    extra_words = []

    for phrase, synonyms in phrase_map.items():
        if phrase in q:
            extra_words.extend(synonyms)

    for word, synonyms in synonym_map.items():
        if word in q:
            extra_words.extend(synonyms)

    if extra_words:
        q = q + " " + " ".join(extra_words)

    return q


# ===============================
# English answer fallback translator
# ===============================

def local_translate_to_english(answer):
    """
    Rule-based fallback when Gemini is not available.
    Covers common UniGuide answers.
    """

    a = normalize_text(answer)

    if "18000" in a or "١٨٠٠٠" in a:
        return "The preparatory year fee at the University of Jeddah is 18,000 SAR for the academic year."

    if "دبلوم" in a or "دبلومات" in a:
        return "Yes, the University of Jeddah offers applied diploma programs in multiple fields."

    if "ذكاء اصطناعي" in a or "الذكاء الاصطناعي" in a:
        return "Yes, the University of Jeddah offers an Artificial Intelligence major within the College of Computer Science and Engineering."

    if "هندسة الحاسب" in a or "علوم الحاسب" in a or "الأمن السيبراني" in a or "علوم البيانات" in a:
        return "The College of Computer Science and Engineering includes Computer Engineering and Networks, Artificial Intelligence, Computer Science, Cybersecurity, Data Science, and Software Engineering."

    if "شروط القبول" in a or "الثانوية" in a or "القدرات" in a or "التحصيلي" in a:
        return "The general admission requirements at the University of Jeddah include having a high school certificate or equivalent and meeting the required aptitude and achievement test scores according to the selected track."

    if "السنة التأهيلية" in a and "عام دراسي واحد" in a:
        return "The preparatory year at the University of Jeddah lasts one academic year."

    if "النسبة الموزونة" in a:
        return "The required weighted percentage varies depending on the track and major, and it usually depends on high school, aptitude test, and achievement test scores."

    return answer


def translate_to_english(answer):
    """
    Translate Arabic answer to English.
    Uses Gemini if available, otherwise uses local fallback.
    """

    if not has_arabic(answer):
        return answer

    if llm is None:
        return local_translate_to_english(answer)

    prompt = f"""
Translate the following Arabic answer into clear professional English.
Do not add new information.
Only translate the meaning.

Arabic Answer:
{answer}

English Answer:
"""

    try:
        response = llm.generate_content(prompt)
        return response.text.strip()

    except Exception as e:
        print("Translation error:", e)
        return local_translate_to_english(answer)


def ensure_answer_language(question, answer):
    lang = detect_language(question)

    if lang == "en":
        return translate_to_english(answer)

    return answer


# ===============================
# Smalltalk
# ===============================

def detect_smalltalk(question):
    q = normalize_text(question)

    if any(x in q for x in ["السلام عليكم", "مرحبا", "هلا", "اهلا", "هاي", "السلام"]):
        return "greeting_ar"

    if any(x in q for x in ["hi", "hello", "hey"]):
        return "greeting_en"

    if any(x in q for x in ["شكرا", "مشكور", "يعطيك العافيه", "يعطيك العافية", "ثانكس"]):
        return "thanks_ar"

    if any(x in q for x in ["thanks", "thank you", "thx"]):
        return "thanks_en"

    if any(x in q for x in ["من انت", "مين انت", "وش انت", "ايش انت", "عرف نفسك"]):
        return "who_ar"

    if any(x in q for x in ["who are you", "what are you"]):
        return "who_en"

    if any(x in q for x in ["ساعدني", "مساعده", "مساعدة", "كيف استخدمك", "ايش تقدر تسوي"]):
        return "help_ar"

    if any(x in q for x in ["help", "how to use", "what can you do"]):
        return "help_en"

    return None


# ===============================
# Out of scope
# ===============================

def is_out_of_scope(question):
    q = normalize_text(question)

    out_of_scope_keywords = [
        "iphone", "samsung", "playstation", "ps5", "netflix",
        "car", "weather", "movie", "game", "football", "restaurant",
        "ايفون", "سامسونج", "بلايستيشن", "سوني", "سياره", "سيارة",
        "طقس", "فيلم", "لعبه", "لعبة", "مطعم"
    ]

    university_keywords = [
        "جامعه", "جامعة", "جده", "جدة", "قبول", "تخصص", "تخصصات",
        "دبلوم", "دبلومات", "رسوم", "سنه", "سنة", "السنه", "السنة",
        "التاهيليه", "التأهيلية", "كلية", "كليات", "طالب", "طالبه",
        "طوارئ", "اخلاء", "حريق", "uj", "university", "jeddah",
        "admission", "major", "majors", "program", "programs",
        "diploma", "fee", "fees", "college", "computer",
        "computer science", "ai", "artificial intelligence", "emergency"
    ]

    has_out_scope = any(word in q for word in out_of_scope_keywords)
    has_university_scope = any(word in q for word in university_keywords)

    return has_out_scope and not has_university_scope


# ===============================
# Fallback
# ===============================

def fallback_response(question, reason="not_found"):
    lang = detect_language(question)

    if reason == "low_confidence":
        if lang == "ar":
            return "لم أجد إجابة مؤكدة في بيانات الجامعة. ممكن تعيد صياغة السؤال أو تحدد هل تقصد القبول، التخصصات، الرسوم، الطوارئ، أو الخدمات الجامعية؟"

        return "I could not find a confident answer in the university data. Please rephrase your question or specify whether you mean admission, majors, fees, emergency, or university services."

    if reason == "empty":
        if lang == "ar":
            return "اكتب سؤالك عن جامعة جدة، مثل القبول، التخصصات، الرسوم، الدبلومات، أو خدمات الجامعة."

        return "Please ask a question about University of Jeddah, such as admission, majors, fees, diplomas, or university services."

    if lang == "ar":
        return "لا توجد معلومات كافية في بيانات الجامعة."

    return "There is not enough information in the university data."


# ===============================
# Retrieval
# ===============================

def retrieve(question, top_k=7, min_score=0.35):
    cleaned_question = expand_query(question)

    query_embedding = embedding_model.encode(
        ["query: " + cleaned_question],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(
        query_embedding.astype("float32"),
        top_k
    )

    docs = []

    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue

        if float(score) < min_score:
            continue

        item = metadata[idx]

        docs.append({
            "type": item.get("type", ""),
            "question": item.get("question", ""),
            "answer": item.get("answer", ""),
            "category": item.get("category", ""),
            "source": item.get("source", ""),
            "score": float(score),
        })

    return docs


# ===============================
# Gemini answer generation
# ===============================

def generate_answer(question, docs):
    if not question or not question.strip():
        return fallback_response(question, reason="empty")

    if len(docs) == 0:
        return fallback_response(question, reason="low_confidence")

    if llm is None:
        return ensure_answer_language(question, docs[0]["answer"])

    context = ""

    for i, doc in enumerate(docs, 1):
        context += f"""
Source {i}
Question: {doc['question']}
Answer: {doc['answer']}
Category: {doc['category']}
Source: {doc['source']}
Similarity score: {doc['score']}
"""

    prompt = f"""
You are UniGuide AI, a smart assistant for University of Jeddah.

Answer in the same language as the user's question.

Use ONLY the provided context.
Do NOT invent information.

If the user asks in English, answer in English.
If the user asks in Arabic, answer in Arabic.

Be direct, clear, and helpful.

Context:
{context}

User question:
{question}

Answer:
"""

    try:
        response = llm.generate_content(prompt)
        answer = response.text.strip()
        return ensure_answer_language(question, answer)

    except Exception as e:
        print("Gemini generation error:", e)
        return ensure_answer_language(question, docs[0]["answer"])


# ===============================
# Main RAG router
# ===============================

def rag_answer(question, top_k=7, min_score=0.35, direct_score=0.80):
    if not question or not str(question).strip():
        return fallback_response(question, reason="empty"), []

    cleaned_question = normalize_text(question)
    lang = detect_language(question)

    smalltalk = detect_smalltalk(cleaned_question)

    if smalltalk == "greeting_ar":
        return "أهلًا بك، أنا UniGuide AI مساعد ذكي لجامعة جدة. أقدر أساعدك في القبول، التخصصات، الرسوم، المسارات، الدبلومات، الخدمات الجامعية، والطوارئ.", []

    if smalltalk == "greeting_en":
        return "Hello! I am UniGuide AI, the University of Jeddah assistant. I can help with admission, majors, fees, tracks, diplomas, university services, and emergency information.", []

    if smalltalk == "thanks_ar":
        return "العفو، في خدمتك.", []

    if smalltalk == "thanks_en":
        return "You are welcome.", []

    if smalltalk == "who_ar":
        return "أنا UniGuide AI، مساعد ذكي مخصص للإجابة عن أسئلة جامعة جدة بناءً على البيانات المتوفرة لدي.", []

    if smalltalk == "who_en":
        return "I am UniGuide AI, an assistant designed to answer University of Jeddah questions based on the available data.", []

    if smalltalk == "help_ar":
        return "اسألني عن القبول، شروط التسجيل، النسب الموزونة، التخصصات، الرسوم، المسارات، الدبلومات، الخدمات الجامعية، أو معلومات الطوارئ في جامعة جدة.", []

    if smalltalk == "help_en":
        return "You can ask me about admission, registration requirements, weighted percentages, majors, fees, tracks, diplomas, university services, or emergency information at the University of Jeddah.", []

    if is_out_of_scope(cleaned_question):
        if lang == "ar":
            return "هذا السؤال خارج نطاق مساعد جامعة جدة. أقدر أساعدك في معلومات الجامعة مثل القبول، التخصصات، الرسوم، الدبلومات، الخدمات الجامعية، والطوارئ.", []

        return "This question is outside the scope of the University of Jeddah assistant. I can help with university information such as admission, majors, fees, diplomas, services, and emergency information.", []

    docs = retrieve(
        question,
        top_k=top_k,
        min_score=min_score
    )

    if len(docs) == 0:
        return fallback_response(question, reason="low_confidence"), []

    best_score = docs[0]["score"]
    best_answer = docs[0]["answer"]

    if best_score < min_score:
        return fallback_response(question, reason="low_confidence"), docs

    # High confidence: return direct answer, translated if needed
    if best_score >= direct_score:
        final_answer = ensure_answer_language(question, best_answer)
        return final_answer, docs

    # Medium confidence: use Gemini if available
    if llm is None:
        final_answer = ensure_answer_language(question, best_answer)
        return final_answer, docs

    try:
        answer = generate_answer(question, docs)
        answer = ensure_answer_language(question, answer)
        return answer, docs

    except Exception as e:
        print("Gemini fallback error:", e)
        final_answer = ensure_answer_language(question, best_answer)
        return final_answer, docs


# ===============================
# FastAPI helper
# ===============================

def ask_uniguide(question):
    answer, docs = rag_answer(question)

    return {
        "answer": answer,
        "docs": docs,
    }