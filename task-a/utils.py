import re

def pre_process(text):
    text = re.sub(r"\n\n", "\n", text)
    paragraphs = re.split(r'。|\n', text.strip())
    # remove all empty strings
    paragraphs = [p for p in paragraphs if p.strip()]
    return paragraphs

def pre_process_without_n(text):
    text = re.sub(r"\n\n", "\n", text)
    paragraphs = re.split(r'。', text.strip())
    # remove all empty strings
    paragraphs = [p for p in paragraphs if p.strip()]
    return paragraphs