# -*- coding: utf-8 -*-
"""prereq_yt.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1BbgEnUzf1jgf8aU-hRHDdr6LIaT12kXP
"""

import urllib.request
import re
import ssl
import spacy
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer

CUSTOM_STOPWORDS = set([
    "methods", "introduction", "related", "work", "conclusion", "references",
    "abstract", "author", "study", "figure", "table", "journal", "doi", "section"
])

def clean_keyword(keyword):
    keyword = re.sub(r'\s+', ' ', keyword)
    keyword = re.sub(r'[^\w\s]', '', keyword)
    return keyword.strip()

def searchVideoForKeyword(searchKeyword):
    allvideos = []
    searchKeyword = clean_keyword(searchKeyword)
    if len(searchKeyword.split(" ")) > 1:
        searchKeyword = searchKeyword.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={searchKeyword}"
    gcontext = ssl.SSLContext()
    try:
        html = urllib.request.urlopen(url, context=gcontext)
        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
        if video_ids:
            allvideos.append(f"https://www.youtube.com/embed/{video_ids[0]}")
    except Exception as e:
        print(f"Error fetching video for keyword '{searchKeyword}': {e}")
    return allvideos
def extract_section(text, section_name, next_sections=None):
    section_start = re.search(rf'\b{section_name}\b', text, re.IGNORECASE)
    if not section_start:
        return ""
    if next_sections:
        next_section = re.search(rf'\b({"|".join(next_sections)})\b', text[section_start.end():], re.IGNORECASE)
        if next_section:
            return text[section_start.end():section_start.end() + next_section.start()]
    return text[section_start.end():]
def extract_keywords_from_pdf(pdf_path, num_keywords=5):
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
    methods_text = extract_section(text, 'Methods', ['Results', 'Discussion', 'Conclusion'])
    intro_text = extract_section(text, 'Introduction', ['Methods', 'Discussion', 'Conclusion'])
    conclusion_text = extract_section(text, 'Conclusion', ['References'])
    combined_text = methods_text + intro_text + conclusion_text
    if not combined_text:
        return []
    # Process text with spacy
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(combined_text)

    # Extract noun chunks
    raw_chunks = [chunk.text.lower() for chunk in doc.noun_chunks if len(chunk.text.split()) > 1]
    cleaned_chunks = [clean_keyword(chunk) for chunk in raw_chunks if chunk not in CUSTOM_STOPWORDS and len(chunk) > 2]
    vectorizer = TfidfVectorizer(max_features=num_keywords, stop_words='english')
    X = vectorizer.fit_transform(cleaned_chunks)
    feature_names = vectorizer.get_feature_names_out()
    return list(feature_names)

def search_videos_from_pdf(pdf_path):
    keywords = extract_keywords_from_pdf(pdf_path, num_keywords=10)
    print(f"Extracted Keywords: {keywords}")
    # Search for videos based on the extracted keywords
    videos = {}
    for keyword in keywords:
        video_links = searchVideoForKeyword(keyword)
        videos[keyword] = video_links
    return videos

pdf_path = "/content/1706.03762v7.pdf"
video_results = search_videos_from_pdf(pdf_path)
for keyword, video_links in video_results.items():
    print(f"Keyword: {keyword}")
    for video in video_links:
        print(f"Video Link: {video}")