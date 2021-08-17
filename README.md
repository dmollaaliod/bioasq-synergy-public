# bioasq-synergy-public

Experiments for Synergy task of BioASQ8. If you use this code, please cite the following paper:

D. Mollá, U. Khanna, D. Galat, V. Nguyen, M. Rybinski (2021). Query-Focused Extractive Summarisation for
Finding Ideal Answers to Biomedical and COVID-19
Questions. *CLEF2021 Working Notes*. [[local copy](CLEF2021Paper.pdf)]

## Files needed

Besides the files available in this repository, you need to obtain the following files. They are not in the github repository because of the large size of some of them:

- `allMeSH_2016_100.vectors.txt` (1.9GB)
- `task8b_nnc_model_1024.data-00000-of-00002` (1.6GB)
- `task8b_nnc_model_1024.data-00001-of-00002` (4MB)
- `task8b_nnc_model_1024.index` (4KB)

## To run the system
The following code replicates the results of runs MQ1 and MQ2 at round 4. The repository also contains the code for the other runs of round 4. For past rounds, explore the github commmit history.

```
$ conda env create -f environment.yml
$ conda activate bioasq-synergy
(bioasq8-synergy) $ python run_mq1.py
(bioasq8-synergy) $ python run_mq2.py
```

## Results

Read the following paper for the details:

D. Mollá, U. Khanna, D. Galat, V. Nguyen, M. Rybinski (2021). Query-Focused Extractive Summarisation for
Finding Ideal Answers to Biomedical and COVID-19
Questions. *CLEF2021 Working Notes*. [[local copy](CLEF2021Paper.pdf)]

### Document Retrieval (metric: F1)

| Run | Round 1 | Round 2 | Round 3 | Round 4
| --- | --- | --- | --- | --- |
|MQ-1 |0.2474 |0.1654 |0.0973 |0.1053
|MQ-2 |0.2474 |0.1654 |0.0973 |0.1053
|MQ-3 | |0.1654 |0.0973 |0.1053
|MQ-4 | | 0.1654 | |0.1510
|MQ-5 | | | | 0.1762

### Snippet Retrieval (metric: F1)

| Run | Round 1 | Round 2 | Round 3 | Round 4
| --- | --- | --- | --- | --- |
|MQ-1|0.1414|0.0704|0.0462|0.0640
|MQ-2|0.1380|0.0706|0.0462|0.0657
|MQ-3||0.0709|0.0473|0.0634
|MQ-4||0.0695||0.0798
|MQ-5||||0.0912



### Ideal Answers (metric: ROUGE-SU F1)

| Run | Round 1 | Round 2 | Round 3 | Round 4
| --- | --- | --- | --- | --- |
|MQ-1||0.0567|0.0883|0.0971
|MQ-2||0.0565|0.0926|0.0912
|MQ-3||0.0436|0.0467|0.0515
|MQ-4||0.0500||0.0857
|MQ-5||||0.0757
