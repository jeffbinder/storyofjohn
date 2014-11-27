# First go round - creates a chapter for each text and a paragraph for each section
# of the source texts.

import codecs
import os
import xml.etree.ElementTree as ET

indir = '../corpora/monk/wright/bibadorned'
first_name = 'John'
surname = 'Arbuckle'

f = codecs.open('output.txt', 'w', 'utf8')

first_name_tok = first_name.lower()
chapter = 0
for file in os.listdir(indir):
    print file
    tree = ET.parse(os.path.join(indir, file))
    root = tree.getroot()    
    body = root.find('{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}body')
    paragraphs = []
    matching_surnames = set()
    for div in body.findall('{http://www.tei-c.org/ns/1.0}div'):
        sentences = []
        current_sentence = []
        between_sentences = True
        contains_name = False
        num_quotes_in_sentence = 0
        prior_tok_is_first_name = False
        for p in div.findall('{http://www.tei-c.org/ns/1.0}p'):
            for el in p:
                if el.tag == '{http://www.tei-c.org/ns/1.0}w':
                    pos = el.attrib['pos']
                    lem = el.attrib['lem'].lower()
                    if between_sentences:
                        between_sentences = False
                    if prior_tok_is_first_name and (pos in ('np1', 'np-n1') or (pos == 'n1' and el.text[0].isupper())):
                        current_sentence.append(surname)
                        matching_surnames.add(lem)
                    elif prior_tok_is_first_name and (pos == 'npg1' or (pos == 'ng1' and el.text[0].isupper())):
                        current_sentence.append(surname)
                        matching_surnames.add(lem)
                        current_sentence.append("'s")
                    elif pos == 'np1' and lem in matching_surnames:
                        current_sentence.append(surname)
                    elif pos == 'npg1' and lem in matching_surnames:
                        current_sentence.append(surname)
                        current_sentence.append("'s")
                    else:
                        current_sentence.append(el.text)
                    if pos in ('np1', 'npg1') and lem == first_name_tok:
                        contains_name = True
                        prior_tok_is_first_name = True
                    else:
                        prior_tok_is_first_name = False
                    if pos == '&quot;' or lem == '&quot;' or pos == '"' or lem == '"':
                        num_quotes_in_sentence += 1
                    if el.attrib['eos'] == '1':
                        if contains_name and num_quotes_in_sentence % 2 == 0:
                            sentences.append(''.join(current_sentence))
                        current_sentence = []
                        between_sentences = True
                        contains_name = False
                        contains_offensive_word = False
                        num_quotes_in_sentence = 0
                if el.tag == '{http://www.tei-c.org/ns/1.0}c':
                    if not between_sentences:
                        current_sentence.append(el.text)
        if sentences:
            paragraphs.append(' '.join(sentences))
    if paragraphs:
        chapter += 1
        if chapter > 1:
            text = '\n\n\n'
        else:
            text = ''
        text += 'Chapter ' + str(chapter) + '\n\n'
        text += '\n\n'.join(paragraphs)
        f.write(text)
        f.flush()
