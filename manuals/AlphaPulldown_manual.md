# AlphaPulldown Manual

[add version]<br>
_Note: AlphaPulldown fully ***maintains backward compatibility*** with input files and scripts from versions 1.x. For instructions on using older files and scripts, please refer to the sections marked "Older Version."_

## What is AlphaPulldown?

AlphaPulldown is an implementation of [AlphaFold-Multimer](https://github.com/google-deepmind/alphafold) designed for customizable high-throughput screening of protein-protein interactions. Besides, AlphaPulldown provides additional customizations of the AlphaFold which include custom structural templates, MMseqs2 multiple sequence alignment (MSA), protein fragment predictions, and implementation of cross-link mass spec data using [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main), [add Integrates experimental models into AlphaFold pipeline using custom multimeric databases].
 
The original AlphaFold-Multimer end-to-end protein complex prediction pipeline may be split into two main steps: the databases search step that generates Features and MSA and protein structure prediction itself. AlphaPluldown executes these steps as independent scripts which is more suitable for modeling a large number of protein complexes. Additionally, AlphaPluldown provides two options for the downstream analysis of the resulting protein models.

Let's take a closer look at the features AlphaPuldown has on top of the Alphafold:

1) **Features and MSA**: At this step for every queried protein sequence AlphaFold searches for preinstalled databases using HMMER and calculates multiple sequence alignment (MSA) for all finden homologues. Additionally, AlphaFold searches for homolog structures that will be used as templates for features generation. This step requires only CPU to run.<br>

   a) To speed up the search process MMSeq2 instead of HHMER can be used
   b) There are a few steps that can be customized at this thing: ${\color{red} Welcome}$
  

3) **Structre prediciton**: TBD

## Contents


installation [link]

## Introduction 

## Compute multiple sequence alignment (MSA) and template features (CPU stage)
TBD
## Predict structures (GPU stage)

## Analysis and Visualization
### Results table
### Jupyter notebook

## SnakeMake running
