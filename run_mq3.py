"""Run MQ-3 for the Synergy task"""

import os
import json

from multisummarise import qsummarise as single_summarise
from multisummarise import bioasq_summarise as multi_summarise
from nnc import LSTMSimilarities

from nltk import sent_tokenize

import search

nnc = LSTMSimilarities(hidden_layer=50, build_model=False, positions=True)
nnc.fit(None, None, None, restore_model=True, verbose=0, savepath="task8b_nnc_model_1024")

# Retrieve the documents
if not os.path.exists("testset4_search_results.json"):
    print("Retrieving the documents")
    search.search(inputfile="BioASQ-taskSynergy-testset4.json",
                  outputfile="testset4_search_results.json",
                  num_hits=200)
with open("testset4_search_results.json") as f:
    search_results = json.load(f)

# Load input snippets from Dima's system
with open("testset4-top5-cross-encoder.json") as f:
    dima_json = json.load(f)

input_data = {}
for q in dima_json['questions']:
    input_data[q['id']] = q['snippets']


nanswers={"summary": 6,
          "factoid": 2,
          "yesno": 2,
          "list": 3}

with open("BioASQ-taskSynergy-testset4.json") as f:
    questions = json.load(f)['questions']

with open("BioASQ-taskSynergy-feedback_round4.json") as f:
    feedback = json.load(f)['questions']

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

    if q['id'] in search_results:
        result = search_results[q['id']]

        print("Processing %i results from a total of %i" % (result['articlesPerPage'], result['size']))
        print(len(result['documents']))

        json_r['documents'] = [d['cord_uid'] for d in result['documents']]
        snippets = []
        for d in result['documents']:
            if d['cord_uid'] in gold_document_negatives:
                # print("Ignoring document negative", d['cord_uid'])
                continue

            single_summary = single_summarise(question, d['documentAbstract'])
            for s in single_summary:
                result_summary = {
                    'document': d['cord_uid'],
                    'beginSection': 'abstract',
                    'endSection': 'abstract',
                    'offsetInBeginSection': s[0][0],
                    'offsetInEndSection': s[0][1],
                    'text': d['documentAbstract'][s[0][0]:s[0][1]]
                }
                snippets.append(result_summary)

        # Generate snippets for submission
        input_sentences = [s['text'] for s in snippets if s['text'] not in gold_snippet_negatives]
        candidates_sentences = [nnc.cleantext(s) for s in input_sentences]
        candidates_sentences_ids = list(range(len(input_sentences)))
        predictions = [p[0] for p in nnc.predict(candidates_sentences,
                                                [nnc.cleantext(question)] * len(input_sentences),
                                                X_positions=candidates_sentences_ids)]
        predictions_unranked = zip(candidates_sentences_ids, predictions)
        predictions_ranked = sorted(predictions_unranked, key=lambda x: x[1], reverse=True)
        sorted_snippets = [snippets[x[0]] for x in predictions_ranked]
    
        # Generate ideal answers
    #    if q['answerReady']:
        if True:
            sent_tokenised = []
            for s in input_data[q['id']]:
                sent_tokenised += sent_tokenize(s)
            input_sentences = [s for s in sent_tokenised if s not in gold_snippet_negatives]
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
            print("from %i, snippets", len(sorted_snippets))
            snippets_gold = [d['text'] for d in question_feedback['snippets']]
            sorted_snippets = [d for d in sorted_snippets if d['text'] not in snippets_gold]
            print("to %i, snippets", len(sorted_snippets))
        json_r['documents'] = json_r['documents'][:10]
        json_r['snippets'] = sorted_snippets[:10]
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
with open('round4_mq3.json','w') as f:
    json.dump(result, f, indent=2)
