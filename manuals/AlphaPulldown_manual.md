# AlphaPulldown Manual

[add version]

AlphaPulldown is an implementation of [AlphaFold](https://github.com/google-deepmind/alphafold) designed for customizable high-throughput screening of protein-protein interactions. Besides, AlphaPulldown provides additional customizations of the AlphaFold which include custom structural templates, MMseqs2 multiple sequence alignment (MSA), protein fragment predictions, and implementation of cross-link mass spec data using [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main), [add Integrates experimental models into AlphaFold pipeline using custom multimeric databases].

The original AlphaFold-Multimer end-to-end protein complex prediction pipeline may be split into two main steps:

1) **Features and MSA**: At this step for every queried protein sequence AlphaFold searches for preinstalled databases using HMMER and calculates multiple sequence alignment for all finden homologues. Additionally, AlphaFold searches for homolog structures that will be used as templates for features generation. This step requires only CPU to run.

2) **Structuer prediciton**: TBD

installation [link]

## Introduction 

## Compute multiple sequence alignment (MSA) and template features (CPU stage)
TBD
## Predict structures (GPU stage)

## Analysis and Visualization
### Results table
### Jupyter notebook

## SnakeMake running
