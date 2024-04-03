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
<br>

## Installation

0. #### Alphafold databases

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
   
   > Note: Since the local installation of all genetic databases is space-consuming, you can alternatively use the remotely-run MMseqs2 and ColabFold databases ${\color{red} [add\ link]}$.

1. #### Create Anaconda environment

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

2. #### Installation using pip

   Activate the AlphaPulldown environment and install AlphaPulldown
   ```bash
   source activate AlphaPulldown
   
   python3 -m pip install alphapulldown==1.0.4
   pip install jax==0.4.23 jaxlib==0.4.23+cuda11.cudnn86 -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
   ```
   
   >**For older versions of AlphaFold**
   >
   >If you haven't updated your databases according to the requirements of AlphaFold 2.3.0, you can still use AlphaPulldown with your older version of AlphaFold database. Please follow the installation instructions on the [dedicated branch](https://github.com/KosinskiLab/AlphaPulldown/tree/AlphaFold-2.2.0).

   ### Installation for developers
   <details>
   
   <summary><b>
    Instructions
   </b></summary>

    1. Clone the GitHub repo
        ```
        git clone --recurse-submodules git@github.com:KosinskiLab/AlphaPulldown.git
        cd AlphaPulldown 
        git submodule init
        git submodule update 
        ```
    2. Create the Conda environment as described in [https://github.com/KosinskiLab/AlphaPulldown/blob/installation-intro-update/README.md#create-anaconda-environment](https://github.com/KosinskiLab/AlphaPulldown/tree/main?tab=readme-ov-file#create-anaconda-environment) 
    3. Add AlphaPulldown package and its submodules to the Conda environment
        ```
        source activate AlphaPulldown
        cd AlphaPulldown
        pip install .
        pip install -e alphapulldown/ColabFold --no-deps
        pip install -e alphafold --no-deps
        ```
        You need to do it only once.
    4. When you want to develop, activate the environment, modify files, and the changes should be automatically recognized.
    5. Test your package during development using tests in ```test/```, e.g.:
       ```
       pip install pytest
       pytest -s test/
       pytest -s test/test_predictions_slurm.py
       pytest -s test/test_features_with_templates.py::TestCreateIndividualFeaturesWithTemplates::test_1a_run_features_generation
       ```
    5. Before pushing to the remote or submitting pull request
        ```
        pip install .
        pytest -s test/
        ```
        to install the package and test. Pytest for predictions only work if slurm is available. Check the created log files in your current directory.
        
        
       </details>
       
<br>

## 1. Compute multiple sequence alignment (MSA) and template features (CPU stage)
### 1.1. Basic run
At this step, you need to provide a [protein FASTA format](https://www.ncbi.nlm.nih.gov/WebSub/html/help/protein.html) file with all protein sequences that will be used for complexes prediction.
   ```
   >sequence_name_A
   SEQUENCEA
   >sequence_name_B
   SEQUENCEB
   ```

Then activate the AlphaPulldown environment and run script `create_individual_features.py` with as follows:

   ```bash
   source activate AlphaPulldown
   create_individual_features.py \
     --fasta_paths=<sequences.fasta> \
     --data_dir=<path to alphafold databases> \
     --output_dir=<dir to save the output objects> \ 
     --max_template_date=<any date you want, format like: 2050-01-01> \
   ```
* Instead of `<sequences.fasta>` provide a path to your input fasta file. <br>
* Instead of `<path to alphafold databases>` provide a path to the genetic database (see [0. Alphafold-databases](#installation) of the installation part).<br>
* Instead of `<dir to save the output objects>` provide a path to the output directory, where your features files will be saved. <br>
* A date in the flag `--max_template_date` is needed to restrict the search of protein structures that are deposited before the indicated date. Unless the date is later than the date of your local genomic database's last update, the script will search for templates among all available structures.

The result of ```create_individual_features.py``` run is pickle format features for each protein from the input fasta file (e.g. `sequence_name_A.pkl` and `sequence_name_B.pkl`) stored in the ```output_dir```. 
> [!NOTE]
> The name of the pickles will be the same as the descriptions of the sequences  in fasta files (e.g. `>sequence_name_A` in the fasta file will yield `sequence_name_A.pkl`). Besides, symbol such as ```| : ; #```, after ```>``` will be replaced with ```_```. 

Go to the next step [2.1. Basic run](#2-predict-structures-gpu-stage)

### 1.2. FLAGS

Features calculation script ```create_individual_features.py``` have several optional FLAGS:
* `--save_msa_files`
   By default is **False** to save storage stage but can be changed into **True**. If it is set to ```True```, the programme will 
   create individual folder for each protein. The output directory will look like:
   
   ```
    output_dir
         |- protein_A.pkl
         |- protein_A
               |- uniref90_hits.sto
               |- pdb_hits.sto
               |- etc.
         |- protein_B.pkl
         |- protein_B
               |- uniref90_hits.sto
               |- pdb_hits.sto
               |- etc.
   ```
    
    
   If ```save_msa_files=False``` then the ```output_dir``` will look like:
   
   ```
    output_dir
         |- protein_A.pkl
         |- protein_B.pkl
   ```

 

 * `--use_precomputed_msas`
   Default value is ```False```. However, if you have already had msa files for your proteins, please set the parameter to be True and arrange your msa files in the format as below:
   
   ```
    example_directory
         |- protein_A 
               |- uniref90_hits.sto
               |- pdb_hits.sto
               |-***.a3m
               |- etc
         |- protein_B
               |- ***.sto
               |- etc
   ```
   
   Then, in the command line, set the ```output_dir=/path/to/example_directory```

* `--skip_existing`

  Default is ```False``` but if you have run the 1st step already for some proteins and now add new proteins to the list, you can change ```skip_existing``` to ```True``` in the
  command line to avoid rerunning the same procedure for the previously calculated proteins.

* `--seq_index`
   
   Default is `None` and the program will run predictions one by one in the given files. However, you can set ```seq_index``` to 
   different number if you wish to run an array of jobs in parallel then the program will only run the corresponding job specified by the ```seq_index```. e.g. the programme only calculate features for the 1st protein in your fasta file if ```seq_index``` is set to be 1. See also the Slurm sbatch script above for example how to use it for parallel execution.
   
   :exclamation: ```seq_index``` starts from 1.
* `--use_mmseqs2`
  
  Use mmseqs2 remotely or not. 'true' or 'false', default is 'false' ${\color{red} [add\ description]}$

 <details>
   
   <summary><b>
   Flags related to TrueMultimer mode:
   </b></summary>

* `--path_to_mmt`
  
  Path to directory with multimeric template mmCIF files". ${\color{red} [add\ description]}$
  
* `--description_file`
  
  Path to the text file with descriptions. ${\color{red} [add\ description]}$

* `--threshold_clashes`
  
  Threshold for VDW overlap to identify clashes. The VDW overlap between two atoms is defined as the sum of their VDW radii minus the distance between their centers.
  If the overlap exceeds this threshold, the two atoms are considered to be clashing.
  A positive threshold is how far the VDW surfaces are allowed to interpenetrate before considering the atoms to be clashing.
  (default: 1000, i.e. no threshold, for thresholding, use 0.6-0.9)
  
* `--hb_allowance`
  
  Additional allowance for hydrogen bonding (default: 0.4) ${\color{red} [add\ description]}$

* `--plddt_threshold`
  
  Threshold for pLDDT score (default: 0)
 </details>

### 1.3. Run using MMseqs2 and ColabFold databases (faster):
>If you used mmseqs2 please remember to cite: 
Mirdita M, Schütze K, Moriwaki Y, Heo L, Ovchinnikov S and Steinegger M. ColabFold: Making protein folding accessible to all.
Nature Methods (2022) doi: 10.1038/s41592-022-01488-1

#### Run mmseqs2 remotely 

>[!Caution]
>To avoid overloading the remote server, do not submit a large number of jobs at the same time. If you want to calculate MSAs for many sequences, please use  [mmseqs2 locally](#run-mmseqs2-locally)

Same as for 1.1 Basic run to run `create_individual_features.py` just add `--use_mmseqs2=True` FALG:
```bash
source activate AlphaPulldown
create_individual_features.py \
  --fasta_paths=example_1_sequences.fasta \
  --data_dir=<path to alphafold databases> \
  --output_dir=<dir to save the output objects> \ 
  --use_mmseqs2=True \
  --max_template_date=<any date you want, format like: 2050-01-01> \ 

```

and your output_dir will look like:
```bash
output_dir
    |-protein_A.a3m
    |-protein_A_env/
    |-protein_A.pkl
    |-protein_B.a3m
    |-protein_B_env/
    |-protein_B.pkl
    ...
```

#### Run mmseqs2 locally 

AlphaPulldown does **NOT** provide interface or codes that will run mmseqs2 locally. Neither will it install mmseqs or any other programme required. The user has to
install mmseqs, colabfold databases, colab_search and other required dependencies and run msa alignments first. An example guide can be found on [Colabfold github](https://github.com/sokrypton/ColabFold).

Suppose you have run mmseqs locally successfully using ```colab_search``` programme, for each protein of your interest, it will generate an a3m file. Thus, your output_dir
should look like this:

```
output_dir
    |-0.a3m
    |-1.a3m
    |-2.a3m
    |-3.a3m
    ...
```
These a3m files from```colabfold_search``` are named in such inconvenient way. Thus, we have provided a ```rename_colab_search_a3m.py``` script that will help you rename all these files. Simply run:

```bash
# within the same conda env where you have installed AlphaPulldown
cd output_dir
rename_colab_search_a3m.py
```
Then your ```output_dir``` will become:

```
output_dir
    |-protein_A.a3m
    |-protein_B.a3m
    |-protein_C.a3m
    |-protein_D.a3m
    ...
```
where ```protein_A``` ```protein_B``` ... correspond to the names you have in your input fasta file (">protein_A" will give you "protein_A.a3m", "protein_B" -> "protein_B.a3m" etc.). 
After this, go back to your project directory with the original FASTA file and point to this directory in the command:

```bash
source activate AlphaPulldown
create_individual_features.py \
  --fasta_paths=example_1_sequences.fasta \
  --data_dir=<path to alphafold databases> \
  --output_dir=output_dir \ 
  --skip_existing=False \
  --use_mmseqs2=True \
  --seq_index=<any number you want or skip the flag to run all one after another>
```

and AlphaPulldown will automatically search each protein's corresponding a3m files. In the end, your output_dir will look like:

```
output_dir
    |-protein_A.a3m
    |-protein_A.pkl
    |-protein_B.a3m
    |-protein_B.pkl
    |-protein_C.a3m
    |-protein_C.pkl
    ...
```
1.4 Run with custom templates


## 2. Predict structures (GPU stage)

## 3. Analysis and Visualization
### Results table
### Jupyter notebook

## SnakeMake running
