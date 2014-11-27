# Second go round - orders sentences based on how far along they appear in the original
# texts, so that sentences that tend to appear near the beginning of an input text
# appear near the beginning of an output text, etc.

import codecs
import os
import xml.etree.ElementTree as ET

indir = '../corpora/monk/wright/bibadorned'
first_name = 'John'
surname = 'Arbuckle'

f = codecs.open('output2.txt', 'w', 'utf8')

first_name_tok = first_name.lower()
sentences = []
ntexts = 0
for file in os.listdir(indir):
    print file
    ntexts += 1
    tree = ET.parse(os.path.join(indir, file))
    root = tree.getroot()    
    body = root.find('{http://www.tei-c.org/ns/1.0}text/{http://www.tei-c.org/ns/1.0}body')
    doc_sentences = []
    ntoks = 0
    num_sentences = 0
    matching_surnames = set()
    for div in body.findall('{http://www.tei-c.org/ns/1.0}div'):
        current_sentence = []
        between_sentences = True
        contains_name = False
        num_quotes_in_sentence = 0
        prior_tok_is_first_name = False
        for p in div.findall('{http://www.tei-c.org/ns/1.0}p'):
            for el in p:
                if el.tag == '{http://www.tei-c.org/ns/1.0}w':
                    ntoks += 1
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
                            doc_sentences.append((''.join(current_sentence), ntoks))
                            num_sentences += 1
                        current_sentence = []
                        between_sentences = True
                        contains_name = False
                        num_quotes_in_sentence = 0
                if el.tag == '{http://www.tei-c.org/ns/1.0}c':
                    if not between_sentences:
                        current_sentence.append(el.text)
        doc_sentences.append(('<sectionbreak>', ntoks))
    if ntoks and num_sentences:
        ntoks_total = ntoks
        for sentence, ntoks in doc_sentences:
            sentences.append((sentence, float(ntoks) / ntoks_total))

text = ['Chapter 1\n\n']
chapter_num = 1
nsectionbreaks = 0
last_sentence = '.'
for sentence, ntoks in sorted(sentences, key=lambda x: x[1]):
    if sentence == '<sectionbreak>':
        nsectionbreaks += 1
    else:
        if nsectionbreaks >= ntexts:
            chapter_num += 1
            text.append('\n\n\nChapter ' + str(chapter_num) + '\n\n')
            nsectionbreaks = 0
            last_sentence = '.'
        elif last_sentence.endswith('"') or sentence.startswith('"'):
            text.append('\n\n')
        text.append(sentence + ' ')
        last_sentence = sentence
f.write(''.join(text))
