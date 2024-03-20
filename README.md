# AlphaPulldown

AlphaPulldown is an implementation of [AlphaFold](https://github.com/google-deepmind/alphafold), designed for customizable high-throughput screening of protein-protein interactions. 

It offers the following features:

* **Сonvenient command line interface**: The prediction requires only an input _fasta file_ with all proteins of interest and a _description file_ of protein combinations to predict
* **Optimized CPU/GPU usage**: AlphaPulldown splits the AlphaFold pipeline into two parts: the MSA and feature generation step for every protein sequence, which requires only CPU, and the subsequent step of GPU-intensive model prediction.
* **No MSA recalculation**: The same CPU-stage generated features can be reused for numerous model predictions, significantly speeding up the screening process.
* **Protein fragments modeling**: AlphaPulldown allows indicating a region of protein you want to model (e.g., ProteinA,8-142). In this case, there is no need to recalculate the CPU stage; the pipeline works with the features generated from the full-length protein sequence.
* **Custom templates**: Instead of the default PDB search for templates, you can provide any custom PDF/CIF files.
* **Results Table**: Provides a summary of all predicted models results in one CSV table with AlphaFold scores, pDockQ and mpDockQ, PI-score, and various physical parameters of the interface.
* **Interactive Jupyter Notebook**: Provides interactive analysis of the resulting PAE plots and models in one window.
* **_NEW:_** Integrates cross-link mass spec data with AlphaFold predictions via [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main) models
* **_NEW:_** Integrates experimental models into AlphaFold pipeline using custom multimeric databases

Please refer to the manual to explore all the possibilities of AlphaPulludown.

## Pre-installation
Check if you have downloaded necessary parameters and databases (e.g. BFD, MGnify etc.) as instructed in [AlphFold's documentation](https://github.com/deepmind/alphafold). You should have a directory like below:
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
## Create Anaconda environment

**Firstly**, install [Anaconda](https://www.anaconda.com/) and create AlphaPulldown environment, gathering necessary dependencies 
```bash
conda create -n AlphaPulldown -c omnia -c bioconda -c conda-forge python==3.10 openmm==8.0 pdbfixer==1.9 kalign2 cctbx-base pytest importlib_metadata hhsuite
```

**Optionally**, if you do not have it yet on your system, install [HMMER](http://hmmer.org/documentation.html) from Anaconda
```bash
source activate AlphaPulldown
conda install -c bioconda hmmer
```
This usually works, but on some compute systems users may wish to use other versions or optimized builds of already installed HMMER and HH-suite.

## Installation using pip

Activate the AlphaPulldown environment and install AlphaPulldown
```bash
source activate AlphaPulldown

python3 -m pip install alphapulldown==1.0.4
pip install jax==0.4.23 jaxlib==0.4.23+cuda11.cudnn86 -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
```

**For older versions of AlphaFold**: 
If you haven't updated your databases according to the requirements of AlphaFold 2.3.0, you can still use AlphaPulldown with your older version of AlphaFold database. Please follow the installation instructions on the [dedicated branch](https://github.com/KosinskiLab/AlphaPulldown/tree/AlphaFold-2.2.0)

## How to develop
Follow the instructions at [Developing guidelines](./manuals/Developing.md)

------

## Manuals
AlphaPulldown supports four different modes of massive predictions: 

* ```pulldown``` - to screen a list of "bait" proteins against a list or lists of other proteins
* ```all_vs_all``` - to model all pairs of a protein list
* ```homo-oligomer``` - to test alternative oligomeric states
* ```custom``` - to model any combination of proteins and their fragments, such as a pre-defined list of pairs or fragments of a complex

AlphaPulldown will return models of all interactions, summarize results in a score table, and will provide a [Jupyter](https://jupyter.org/) notebook for an interactive analysis, including PAE plots and 3D displays of models colored by chain and pLDDT score.

## Examples

Example 1 is a case where ```pulldown``` mode is used. Manual: [example_1](./manuals/example_1.md)

Example 2 is a case where ```custom``` and ```homo-oligomer``` modes are used. Manual: [example_2](./manuals/example_2.md) 

Example 3 is demonstrating the usage of multimeric templates for guiding AlphaFold predictions. Manual: [example_3](./manuals/example_3.md) 

```all_vs_all``` mode can be viewed as a special case of the ```pulldown``` mode thus the instructions of this mode are added as Appendix in both manuals mentioned above. 

## Citations
If you use this package, please cite as the following:
```python
@Article{AlphaPUlldown,
  author  = {Dingquan Yu, Grzegorz Chojnowski, Maria Rosenthal, and Jan Kosinski},
  journal = {Bioinformatics},
  title   = {AlphaPulldown—a python package for protein–protein interaction screens using AlphaFold-Multimer},
  year    = {2023},
  volume  = {39},
  issue  = {1},
  doi     = {https://doi.org/10.1093/bioinformatics/btac749}
}
```
