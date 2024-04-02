# AlphaPulldown Manual

`[add version]`<br>
> __Note__: AlphaPulldown fully **maintains backward compatibility** with input files and scripts from versions 1.x. For instructions on using older files and scripts, please refer to the sections marked "Older Version."``
## About AlphaPulldown

AlphaPulldown is an implementation of [AlphaFold-Multimer](https://github.com/google-deepmind/alphafold) designed for customizable high-throughput screening of protein-protein interactions. Besides, AlphaPulldown provides additional customizations of the AlphaFold which include custom structural templates, MMseqs2 multiple sequence alignment (MSA), protein fragment predictions, and implementation of cross-link mass spec data using [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main), [add Integrates experimental models into AlphaFold pipeline using custom multimeric databases].
![AP_pipeline](../manuals/AP_pipeline.png)
 
The original AlphaFold-Multimer end-to-end protein complex prediction pipeline may be split into two main steps: **(1)** the databases search step that generates Features and MSA and **(2)** protein structure prediction itself. AlphaPluldown executes these steps as independent scripts which is more suitable for modeling a large number of protein complexes. Additionally, **(3)** AlphaPluldown provides two options for the downstream analysis of the resulting protein models.


![AP_modes](../manuals/AP_modes.png)
AlphaPulldown operates in four different modes, each suitable for a particular task: `custom` - user manually enters all combinations of proteins to model, `all_vs_all` - all combinations of lines from the input file are predicted, `pulldown` - every protein is precited in combination with the "bait", `homo-oligomer` models proteins homo-oligomers.


Let's take a closer look at the AlphaPuldown pipeline:


1) **Features and MSA**: At this step for every queried protein sequence AlphaFold searches for preinstalled databases using HMMER and calculates multiple sequence alignment (MSA) for all finden homologues. Additionally, AlphaFold searches for homolog structures that will be used as templates for features generation. This step requires only CPU to run.<be>
There are a few customizable options for this step:

   * To speed up the search process MMSeq2 ${\color{red} [add link]}$ instead of HHMER can be used.<br>
   * Use custom MSA ${\color{red} [add link]}$.
   * _NEW:_ Use a custom structural template ${\color{red} [add link]}$. Including true multimer.
  

2) **Structure prediction**: At this step, the AlaphaFold neural network runs and produces the final protein structure, which requires GPU computational powers.
   Here, AlphaPulldown allows:
   * Read all combinations of proteins to predict from one file
   * Specify the number of residues that correspond to the part of the protein you want to predict
   * Adjust MSA depth (allows control over how much the initial MSA influences the final model)
   * Crosslinking data implementation with [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main).

3) **Results analysis**: The results for all predicted models could be systematized using one of the following two options:
   * Table that contains various scores and physical parameters of protein complexes' interaction.
   * Jupyter notebook with interactive 3D models and PAE plots.

## Installation

### Alphafold databases
For the standard MSA and features calculation, AlphaPulldow requires Genetic databases. Check if you have downloaded necessary parameters and databases (e.g. BFD, MGnify etc.) as instructed in [AlphFold's documentation](https://github.com/deepmind/alphafold). You should have a directory like below:

<details>

<summary><b>
 Databases directory
</b></summary>

 ```
 alphafold_database/                             # Total: ~ 2.2 TB (download: 438 GB)
    bfd/                                   # ~ 1.7 TB (download: 271.6 GB)
        # 6 files.
    mgnify/                                # ~ 64 GB (download: 32.9 GB)
        mgy_clusters_2018_12.fa
    params/                                # ~ 3.5 GB (download: 3.5 GB)
        # 5 CASP14 models,
        # 5 pTM models,
        # 5 AlphaFold-Multimer models,
        # LICENSE,
        # = 16 files.
    pdb70/                                 # ~ 56 GB (download: 19.5 GB)
        # 9 files.
    pdb_mmcif/                             # ~ 206 GB (download: 46 GB)
        mmcif_files/
            # About 180,000 .cif files.
        obsolete.dat
    pdb_seqres/                            # ~ 0.2 GB (download: 0.2 GB)
        pdb_seqres.txt
    small_bfd/                             # ~ 17 GB (download: 9.6 GB)
        bfd-first_non_consensus_sequences.fasta
    uniclust30/                            # ~ 86 GB (download: 24.9 GB)
        uniclust30_2018_08/
            # 13 files.
    uniprot/                               # ~ 98.3 GB (download: 49 GB)
        uniprot.fasta
    uniref90/                              # ~ 58 GB (download: 29.7 GB)
        uniref90.fasta
 ```
</details>

> [!TIP] 
> Since local installation of all genetic databases is space-consuming, you can alternatively use the remotely-run MMseqs2 and ColabFold databases ${\color{red} [add\ link]}$.

## Compute multiple sequence alignment (MSA) and template features (CPU stage)
TBD
## Predict structures (GPU stage)

## Analysis and Visualization
### Results table
### Jupyter notebook

## SnakeMake running
