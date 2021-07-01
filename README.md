# bioasq-synergy-public

Experiments for Synergy task of BioASQ8

## Files needed

Besides the files available in this repository, you need to obtain the following files. They are not in the github repository because of the large size of some of them:

- `allMeSH_2016_100.vectors.txt` (1.9GB)
- `task8b_nnc_model_1024.data-00000-of-00002` (1.6GB)
- `task8b_nnc_model_1024.data-00001-of-00002` (4MB)
- `task8b_nnc_model_1024.index` (4KB)

## To run the system
```
$ conda env create -f environment.yml
$ conda activate bioasq-synergy
(bioasq8-synergy) $ python run_mq1.py
(bioasq8-synergy) $ python run_mq2.py
```
