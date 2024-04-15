import re

def pre_process(text):
    text = re.sub(r"\n\n", "\n", text)
    # remove \u3000 and \u00a0
    # text = text.replace("\u3000", "").replace("\u00a0", "")
    paragraphs = re.split(r'。|\n', text.strip())
    # remove all empty strings
    paragraphs = [p for p in paragraphs if p.strip()]
    return paragraphs

def pre_process_without_n(text):
    text = re.sub(r"\n\n", "\n", text)
    # text = text.replace("\u3000", "").replace("\u00a0", "")
    paragraphs = re.split(r'。', text.strip())
    # remove all empty strings
    paragraphs = [p for p in paragraphs if p.strip()]
    return paragraphs