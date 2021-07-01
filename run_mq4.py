"""Run  MQ-4 for the Synergy task"""

import os
import json
import csv

from nltk.tokenize import word_tokenize

from multisummarise import qsummarise as single_summarise
from multisummarise import bioasq_summarise as multi_summarise
from nnc import LSTMSimilarities

import search

nnc = LSTMSimilarities(hidden_layer=50, build_model=False, positions=True)
nnc.fit(None, None, None, restore_model=True, verbose=0, savepath="task8b_nnc_model_1024")

# Retrieve the documents
with open('neural_tuned_rd4/neural_untuned_rd4_nolimit.tsv') as f:
    csv_reader = csv.DictReader(f, delimiter='\t', fieldnames=('i', 'qid', 'cordid', 'score', 'text'))
    retrieved_data  = {}
    for row in csv_reader:
        if row['qid'] not in retrieved_data:
            retrieved_data[row['qid']] = []
        retrieved_data[row['qid']].append({'cordid': row['cordid'],
                                           'score': row['score'],
                                           'text': row['text']})

nanswers={"summary": 6,
          "factoid": 2,
          "yesno": 2,
          "list": 3}

#with open("BioASQ-taskSynergy-dryRun-testset.json") as f:
with open("BioASQ-taskSynergy-testset4.json") as f:
    questions = json.load(f)['questions']

with open("BioASQ-taskSynergy-feedback_round4.json") as f:
    feedback = json.load(f)['questions']
#feedback = []

print("Processing %i questions" % len(questions))
json_results = []
for q in questions:
    feedback_found = False
    question_feedback = None
    gold_document_negatives = []
    gold_snippet_negatives = []
    #print(q['body'])
    #print('Answer required:', q['answerReady'])
    for f in feedback:
        if q['id'] == f['id']:
            print("Feedback found")
            feedback_found = True
            question_feedback = f
            gold_document_negatives = [d['id'] for d in question_feedback['documents'] if not d['golden']]
            gold_snippet_negatives = [s['text'] for s in question_feedback['snippets'] if not s['golden']]
            #print("Gold snippet negatives:", gold_snippet_negatives)

    json_r = {'body': q['body'],
              'id': q['id'],
              'type': q['type'],
              'answerReady': q['answerReady']}
    question = q['body']
    print(question)

    if q['id'] in retrieved_data:
        result = retrieved_data[q['id']]
        
        print("Processing %i results" % (len(result)))

        json_r['documents'] = [d['cordid'] for d in result]
        snippets = []
        for d in result:
            if d['cordid'] in gold_document_negatives:
                # print("Ignoring document negative", d['cord_uid'])
                continue

            single_summary = single_summarise(question, d['text'])
            for s in single_summary:
                result_summary = {
                    'document': d['cordid'],
                    'beginSection': 'abstract',
                    'endSection': 'abstract',
                    'offsetInBeginSection': s[0][0],
                    'offsetInEndSection': s[0][1],
                    'text': d['text'][s[0][0]:s[0][1]]
                }
                snippets.append(result_summary)
        json_r['snippets'] = snippets

#        if q['answerReady']:
        if True:
#            input_sentences = [s['text'] for s in snippets if (s['text'] not in gold_snippet_negatives) and (len(word_tokenize(s['text'])) <= 50)]
            input_sentences = [s['text'] for s in snippets if s['text'] not in gold_snippet_negatives]

            m_summary = multi_summarise(question, input_sentences, nnc=nnc, n=nanswers[q['type']])
            print(m_summary)
            m_summary_text = ' '.join([t for t, n, score in m_summary])
            json_r['ideal_answer'] = m_summary_text
            if q['type'] == 'yesno':
                json_r['exact_answer'] = 'yes'
            else:
                json_r['exact_answer'] = []

        # Remove gold data and truncate lists to conform with requirements
        if feedback_found:
            print("from %i, documents", len(json_r['documents']))
            documents_gold = [d['id'] for d in question_feedback['documents']]
            json_r['documents'] = [d for d in json_r['documents'] if d not in documents_gold]
            print("to %i, documents", len(json_r['documents']))
            print("from %i, snippets", len(json_r['snippets']))
            snippets_gold = [d['text'] for d in question_feedback['snippets']]
            json_r['snippets'] = [d for d in json_r['snippets'] if d['text'] not in snippets_gold]
            print("to %i, snippets", len(json_r['snippets']))
        json_r['documents'] = json_r['documents'][:10]
        json_r['snippets'] = json_r['snippets'][:10]
    else:
        print("No results found; ignoring the question")
        json_r['documents'] = []
        json_r['snippets'] = []
        if q['type'] == 'yesno':
            json_r['exact_answer'] = 'yes'
        else:
            json_r['exact_answer'] = []
        json_r['ideal_answer'] = ''

    json_results.append(json_r)

result = {'questions': json_results}
with open('round4_mq4.json','w') as f:
    json.dump(result, f, indent=2)
