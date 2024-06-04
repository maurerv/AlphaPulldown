`version 2.0.0 (beta)`

> AlphaPulldown fully **maintains backward compatibility** with input files and scripts from versions 1.x.

# Table of contents 


# About AlphaPulldown

AlphaPulldown is an implementation of [AlphaFold-Multimer](https://github.com/google-deepmind/alphafold) designed for customizable high-throughput screening of protein-protein interactions. Besides, AlphaPulldown provides additional customizations of the AlphaFold which include custom structural multimeric templates (TrueMultimer), MMseqs2 multiple sequence alignment (MSA) and [ColabFold](https://github.com/sokrypton/ColabFold) databases, proteins fragments predictions, and implementation of cross-link mass spec data using [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main).

AlphaPulldown can be used in two ways: as a set of **Python scripts**, which this manual covers, and as a **Snakemake pipeline**. For details on using the Snakemake pipeline, please refer to the separate GitHub [**repository**](https://github.com/KosinskiLab/AlphaPulldownSnakemake).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/AP_pipeline_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/AP_pipeline.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/AP_pipeline.png">
</picture>
 
The original [AlphaFold-Multimer](https://github.com/google-deepmind/alphafold) protein complex prediction pipeline may be split into two steps: **(1)** the databases search step that generates Features and MSA for every individual protein sequence and **(2)** protein complex structure prediction itself. AlphaPulldown executes these steps as independent scripts, enhancing efficiency for modeling many protein complexes. Additionally, **(3)** AlphaPulldown  offers two options for downstream analysis of the resulting protein models.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/AP_modes_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/AP_modes.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/AP_modes.png">
</picture>

A key strength of AlphaPulldown is its ability to flexibly define how proteins are combined for the structure prediction of protein complexes. Here are the three main approaches you can use:

* **Single file** (custom mode): Create a file where each row lists the protein sequences you want to predict together.
* **Multiple Files** (pulldown mode): Provide several files, each containing protein sequences. AlphaPulldown will automatically generate all possible combinations by pairing rows of protein names from each file.
* **All versus all**: AlphaPulldown will generate all possible non-redundant combinations of proteins in the list. 

The AlphaPulldown workflow is as follows:

1) **Features and MSA**:   In this step, AlphaFold searches preinstalled databases using HMMER for each queried protein sequence and calculates multiple sequence alignments (MSAs) for all found homologs. It also searches for homolog structures to use as templates for feature generation. This step only requires CPU.

   Customizable options include:
   * To speed up the search process, [MMSeq2](https://doi.org/10.1038/s41592-022-01488-1) can be used instead of the default HHMER.
   * Use custom MSA.
   * Use a custom structural template, including a multimeric one (TrueMultimer mode).
  
3) **Structure prediction**: In this step, the AlphaFold neural network runs and produces the final protein structure, requiring GPU.
   AlphaPulldown allows:
   * Reading all combinations of proteins to predict from one file or generating combinations of proteins using `pulldown` or `all_versus_all` modes.
   * Specify the number of residues that correspond to the part of the protein you want to predict.
   * Adjusting MSA depth to control the influence of the initial MSA on the final model.
   * Implementing crosslinking data with [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main).

4) **Results analysis**: The results for all predicted models can be systematized using one of the following options:
   * A table containing various scores and physical parameters of protein complex interactions.
   * A Jupyter notebook with interactive 3D protein models and PAE plots.
     
<br>

# Snakemake AlphaPulldown 

AlphaPulldown is available as a Snakemake pipeline, allowing you to sequentially execute  **(1)** Features and MSA generation, **(2)** Structure prediction, and  **(3)** Results analysis without manual intervention between steps. For detailed installation and execution instructions, please refer to the [AlphaPulldownSnakemake](https://github.com/KosinskiLab/AlphaPulldownSnakemake) repository. 

>[!Warning]
>The Snakemake version of AlphaPulldown differs slightly from the conventional scripts-based AlphaPulldown in terms of input file specifications.

$\text{\color{red} Write which scripts and modes are not possible to run with the Snakmake, e.g. Alphalink2 }$

For downstream analysis of SnakeMake-AlphaPulldown results, please refer to this part of the manual: [Downstream analysis](#add_link).
<br>
<br>

# Scripts-Based AlphaPulldown

AlphaPulldown can be used as a set of Python scripts for every particular step. [**(1)**](#1-compute-multiple-sequence-alignment-msa-and-template-features-cpu-stage) `create_individual_features.py` [**(2)**](#2-predict-structures-gpu-stage) `run_multimer_jobs.py` [**(3)**](#addname) `create_notebook.py` and `alpha-analysis.sif` image.

## Installation

#### 0. Alphafold databases

For the standard MSA and features calculation, AlphaPulldown requires genetic databases. Check if you have downloaded the necessary parameters and databases (e.g., BFD, MGnify, etc.) as instructed in [AlphaFold's documentation](https://github.com/deepmind/alphafold). You should have a directory like below:

   <details>
   <summary>
   <b>Databases directory</b>
   </summary>
   
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
   
> [!NOTE] 
> Since the local installation of all genetic databases is space-consuming, you can alternatively use the [remotely-run MMseqs2 and ColabFold databases](https://github.com/sokrypton/ColabFold). Follow the corresponding [instructions](#13-run-using-mmseqs2-and-colabfold-databases-faster). However, for AlphaPulldown to function, you must download the parameters stored in the `params/` directory of AlphaFold database.

$\text{\color{red}Do people need to download anything else in case of MMseq2 run?}$

#### 1. Create Anaconda environment

  **Firstly**, install [Anaconda](https://www.anaconda.com/) and create AlphaPulldown environment, gathering necessary dependencies:
  ```bash
  conda create -n AlphaPulldown -c omnia -c bioconda -c conda-forge python==3.10 openmm==8.0 pdbfixer==1.9 kalign2 cctbx-base pytest importlib_metadata hhsuite
  ```
       
  **Optionally**, if you do not have it yet on your system, install [HMMER](http://hmmer.org/documentation.html) from Anaconda:
  
  ```bash
  source activate AlphaPulldown
  conda install -c bioconda hmmer
  ```
  This usually works, but on some compute systems users may wish to use other versions or optimized builds of already installed HMMER and HH-suite.

#### 2. Installation using pip

   Activate the AlphaPulldown environment and install AlphaPulldown:
   ```bash
   source activate AlphaPulldown
   python3 -m pip install alphapulldown==1.0.4
   pip install jax==0.4.23 jaxlib==0.4.23+cuda11.cudnn86 -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html
   ```
$\text{\color{red}Change the version of AlphaPulldown}$
   
   >[!NOTE] 
   >**For older versions of AlphaFold**:
   >If you haven't updated your databases according to the requirements of AlphaFold 2.3.0, you can still use AlphaPulldown with your older version of AlphaFold database. Please follow the installation instructions on the [dedicated branch](https://github.com/KosinskiLab/AlphaPulldown/tree/AlphaFold-2.2.0).

#### 3. Installation for the Analysis step (optional)
For making the Results table, you need to have Singularity installed ($\text{\color{red}add instructions or link}$).

Download the singularity image: 

* If your results are from AlphaPulldown prior to version 1.0.0: [alpha-analysis_jax_0.3.sif](https://www.embl-hamburg.de/AlphaPulldown/downloads/alpha-analysis_jax_0.3.sif). 
* If your results are from AlphaPulldown with version >=1.0.0: [alpha-analysis_jax_0.4.sif](https://www.embl-hamburg.de/AlphaPulldown/downloads/alpha-analysis_jax_0.4.sif). 

Chrome users may not be able to download it after clicking the link. If so, please right-click and select "Save link as".

#### 4. Installation for cross-link input data by AlphaLink2 (optional)

1. Compile [UniCore](https://github.com/dptech-corp/Uni-Core).
    ```bash
    source activate AlphaPulldown
    git clone https://github.com/dptech-corp/Uni-Core.git
    cd Uni-Core
    python setup.py install --disable-cuda-ext
        
    # test whether unicore is successfully installed
    python -c "import unicore"
    ```
    You may see the following warning but it's fine:

    ```
    fused_multi_tensor is not installed corrected
    fused_rounding is not installed corrected
    fused_layer_norm is not installed corrected
    fused_softmax is not installed corrected
    ```
    
2. Make sure you have PyTorch corresponding to the CUDA version installed. For example, [PyTorch 1.13.0+cu117](https://pytorch.org/get-started/previous-versions/) 
and CUDA/11.7.0
$\text{\color{red}add pip install torch==1.13.1 torchvision==0.14.1 torchaudio==0.13.1}$
4. Download the PyTorch checkpoints from [Zenodo](https://zenodo.org/records/8007238), unzip it, then you should obtain a file named: ```AlphaLink-Multimer_SDA_v3.pt```

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
       
6. Before pushing to the remote or submitting pull request
      
    ```
    pip install .
    pytest -s test/
    ```
    to install the package and test. Pytest for predictions only work if slurm is available. Check the created log files in your current directory.
</details>
       
<br>

## 1. Compute multiple sequence alignment (MSA) and template features (CPU stage)
### 1.1. Basic run

This is a general example of `create_individual_features.py` usage. For information on running specific tasks or parallel execution on a cluster, please refer to the corresponding sections.

#### Input
At this step, you need to provide a [protein FASTA format](https://www.ncbi.nlm.nih.gov/WebSub/html/help/protein.html) file with all protein sequences that will be used for complex prediction.

Example of a FASTA file (`sequences.fasta`):

   ```
   >proteinA
   SEQUENCEOFPROTEINA
   >proteinB
   SEQUENCEOFPROTEINB
   ```
#### Script Execution

Activate the AlphaPulldown environment and run the script `create_individual_features.py` as follows:

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

Features calculation script ```create_individual_features.py``` has several optional FLAGS:

 <details>
   <summary>
    Full list of arguments (FLAGS):
   </summary>
   
* `--save_msa_files`: By default is **False** to save storage stage but can be changed into **True**. If it is set to ```True```, the program will 
   create individual folder for each protein. The output directory will look like:
   
   ```
    output_dir
         |- proteinA.pkl
         |- proteinA
               |- uniref90_hits.sto
               |- pdb_hits.sto
               |- etc.
         |- proteinB.pkl
         |- proteinB
               |- uniref90_hits.sto
               |- pdb_hits.sto
               |- etc.
   ```
    
    
   If ```save_msa_files=False``` then the ```output_dir``` will look like:
   
   ```
    output_dir
         |- proteinA.pkl
         |- proteinB.pkl
   ```

 * `--use_precomputed_msas`: Default value is ```False```. However, if you have already had msa files for your proteins, please set the parameter to be True and arrange your msa files in the format as below:
   
   ```
    example_directory
         |- proteinA 
               |- uniref90_hits.sto
               |- pdb_hits.sto
               |- ***.a3m
               |- etc
         |- proteinB
               |- ***.sto
               |- etc
   ```
   
   Then, in the command line, set the ```output_dir=/path/to/example_directory```

* `--skip_existing`: Default is ```False``` but if you have run the 1st step already for some proteins and now add new proteins to the list, you can change ```skip_existing``` to ```True``` in the
  command line to avoid rerunning the same procedure for the previously calculated proteins.

* `--seq_index`: Default is `None` and the program will run predictions one by one in the given files. However, you can set ```seq_index``` to 
   different number if you wish to run an array of jobs in parallel then the program will only run the corresponding job specified by the ```seq_index```. e.g. the programme only calculate features for the 1st protein in your fasta file if ```seq_index``` is set to be 1. See also the Slurm sbatch script above for example how to use it for parallel execution. :exclamation: ```seq_index``` starts from 1.
  
* `--use_mmseqs2`: Use mmseqs2 remotely or not. 'true' or 'false', default is 'false' ${\color{red} [add\ description]}$

FLAGS related to TrueMultimer mode:

* `--path_to_mmt`: Path to directory with multimeric template mmCIF files".
  
* `--description_file`: Path to the text file with descriptions. ${\color{red} [add\ description]}$

* `--threshold_clashes` :Threshold for VDW overlap to identify clashes. The VDW overlap between two atoms is defined as the sum of their VDW radii minus the distance between their centers.
  If the overlap exceeds this threshold, the two atoms are considered to be clashing.
  A positive threshold is how far the VDW surfaces are allowed to interpenetrate before considering the atoms to be clashing.
  (default: 1000, i.e. no threshold, for thresholding, use 0.6-0.9)
  
* `--hb_allowance`: Additional allowance for hydrogen bonding (default: 0.4) ${\color{red} [add\ description]}$

* `--plddt_threshold`: Threshold for pLDDT score (default: 0)
 </details>

#### Output
The result of ```create_individual_features.py``` run is pickle format features for each protein from the input fasta file (e.g. `sequence_name_A.pkl` and `sequence_name_B.pkl`) stored in the ```output_dir```. 

> [!NOTE]
> The name of the pickles will be the same as the descriptions of the sequences  in fasta files (e.g. `>prtoein_A` in the fasta file will yield `proteinA.pkl`). Note that special symbols such as ```| : ; #```, after ```>``` will be replaced with ```_```.

#### Next step
Proceed to the next step [2.1 Basic Run](#21-basic-run).

### 1.2. Example run with SLURM (EMBL cluster)

If you run AlphaPulldown on a computer cluster, you may want to execute feature creation in parallel. Here, we provide an example of code that is suitable for a cluster that utilizes SLURM Workload Manager. 
> **For EMBL staff:**  For more details about the SLURM on the EMBL cluster, please refer to the [EMBL Cluster wiki](https://wiki.embl.de/cluster/Main_Page) using the EMBL network.

#### Input

For the following example, we will use [`example_2_sequences.fasta`](../example_data/example_2_sequences.fasta) as input. 

#### Script Execution

Create the ```create_individual_features_SLURM.sh``` bash file using vi, nano, or any other text editor and place the following code in it. Don't forget to change the input of `create_individual_features.py` script as described [previously in manual](#1-compute-multiple-sequence-alignment-msa-and-template-features-cpu-stage):

```bash
#!/bin/bash

#A typical run takes a couple of hours but may be much longer
#SBATCH --job-name=array
#SBATCH --time=10:00:00

#log files:
#SBATCH -e logs/create_individual_features_%A_%a_err.txt
#SBATCH -o logs/create_individual_features_%A_%a_out.txt

#qos sets priority
#SBATCH --qos=low

#Limit the run to a single node
#SBATCH -N 1

#Adjust this depending on the node
#SBATCH --ntasks=8
#SBATCH --mem=64000

module load HMMER/3.4-gompi-2023a
module load HH-suite/3.3.0-gompi-2023a
module load Anaconda3
source activate AlphaPulldown

# CUSTOMIZE THE FOLLOWING SCRIPT PARAMETERS FOR YOUR SPECIFIC TASK:
####
create_individual_features.py \
  --fasta_paths=example_1_sequences.fasta \
  --data_dir=/scratch/AlphaFold_DBs/2.3.2/ \
  --output_dir=/scratch/mydir/test_AlphaPulldown/ \ 
  --max_template_date=2050-01-01 \
  --skip_existing=True \
  --seq_index=$SLURM_ARRAY_TASK_ID
#####
```

Make the script executable by running:

```bash
chmod +x create_individual_features_SLURM.sh
```

Next, execute the following commands, replacing `<sequences.fasta>` with the path to your input FASTA file:

```bash
mkdir logs
#Count the number of jobs corresponding to the number of sequences:
count=`grep ">" <sequences.fasta> | wc -l`
#Run the job array, 100 jobs at a time:
sbatch --array=1-$count%100 create_individual_features_SLURM.sh
```
 <details>
   
   <summary>
   If you have several FASTA files, use the following commands:
   </summary>

Example for two files (for more files create `count3`, `count4`, etc. variables and add them as a term to the sum of counts):
 ```bash
mkdir logs
#Count the number of jobs corresponding to the number of sequences:
count1=`grep ">" <sequences1.fasta> | wc -l`
count2=`grep ">" <sequences2.fasta> | wc -l`
count=$(( $count1 + $count2 )) 
#Run the job array, 100 jobs at a time:
sbatch --array=1-$count%100 create_individual_features_SLURM.sh
```
 </details>

 #### Next step
 Proceed to the next step [2.2 Example run with SLURM (EMBL cluster)](#add_link).


### 1.3. Run with custom MSA

To run `create_individual_features.py` with the custom MSA. Prepare the A3M formatted MSA files for every protein. The names of these files should correspond to names from the FASTA file. Move these files to the output directory:

```
output_dir
    |-proteinA.a3m
    |-proteinB.a3m
    |-proteinC.a3m
    |-proteinD.a3m
    ...
```

Run `create_individual_features.py` as described in [1.1. Basic run](#11-basic-run) with additionl FLAGS `--save_msa_files` and `--use_precomputed_msas`. 

$\text{\color{red} Check if it wroks}$


### 1.4. Run using MMseqs2 and ColabFold Databases (Faster)

MMseqs2 is another method for homolog search and MSA generation. It offers an alternative to the default HMMER and HHblits used by AlphaFold. The results of these different approaches might lead to slightly different protein structure predictions due to variations in the captured evolutionary information within the MSAs. AlphaPulldown supports the implementation of MMseqs2 search made by ColabFold, which also provides a web server for MSA generation, so no local installation of databases is needed.

> **Cite:** If you use MMseqs2, please remember to cite:
Mirdita M, Schütze K, Moriwaki Y, Heo L, Ovchinnikov S, Steinegger M. ColabFold: Making protein folding accessible to all. Nature Methods (2022) doi: 10.1038/s41592-022-01488-1

#### Run MMseqs2 Remotely

>[!Caution]
>To avoid overloading the remote server, do not submit a large number of jobs simultaneously. If you want to calculate MSAs for many sequences, please use [MMseqs2 locally](#run-mmseqs2-locally).

Script execution

To run `create_individual_features.py` using MMseqs2 remotely, add the `--use_mmseqs2=True` flag:
```bash
source activate AlphaPulldown
create_individual_features.py \
  --fasta_paths=<sequences.fasta> \
  --data_dir=<path to alphafold databases> \
  --output_dir=<dir to save the output objects> \ 
  --use_mmseqs2=True \
  --max_template_date=<any date you want, format like: 2050-01-01> \ 
```

After the script run is finished, your `output_dir` will look like this:

```bash
output_dir
    |-proteinA.a3m
    |-proteinA_env/
    |-proteinA.pkl
    |-proteinB.a3m
    |-proteinB_env/
    |-proteinB.pkl
    ...
```

Proceed to the next step [2.1 Basic Run](#21-basic-run).

#### Run MMseqs2 Locally

AlphaPulldown does **NOT** provide an interface or code to run MMseqs2 locally, nor will it install MMseqs2 or any other required programs. The user must install MMseqs2, ColabFold databases, ColabFold search, and other required dependencies and run MSA alignments first. An example guide can be found on the [ColabFold GitHub](https://github.com/sokrypton/ColabFold).

Suppose you have successfully run MMseqs2 locally using the `colab_search` program; it will generate an A3M file for each protein of your interest. Thus, your `output_dir` should look like this:

```
output_dir
    |-0.a3m
    |-1.a3m
    |-2.a3m
    |-3.a3m
    ...
```

These a3m files from `colabfold_search` are inconveniently named. Thus, we have provided a `rename_colab_search_a3m.py` script to help you rename all these files. Simply run:

```bash
# within the same conda env where you have installed AlphaPulldown
cd output_dir
rename_colab_search_a3m.py
```
Then your ```output_dir``` will become:

```
output_dir
    |-proteinA.a3m
    |-proteinB.a3m
    |-proteinC.a3m
    |-proteinD.a3m
    ...
```
Here, `protein_A`, `protein_B`, etc., correspond to the names in your input FASTA file (e.g., `>protein_A` will give you `protein_A.a3m`, `>protein_B` will give you `protein_B.a3m`, etc.). 
After this, go back to your project directory with the original FASTA file and point to this directory in the command:

```bash
source activate AlphaPulldown
create_individual_features.py \
  --fasta_paths=<sequences.fasta> \
  --data_dir=<path to alphafold databases> \
  --output_dir=<output_dir> \ 
  --skip_existing=False \
  --use_mmseqs2=True \
  --seq_index=<any number you want or skip the flag to run all one after another>
```

AlphaPulldown will automatically search each protein's corresponding a3m files. In the end, your output_dir will look like:

```
output_dir
    |-proteinA.a3m
    |-proteinA.pkl
    |-proteinB.a3m
    |-proteinB.pkl
    |-proteinC.a3m
    |-proteinC.pkl
    ...
```

Proceed to the next step [2.1 Basic Run](#21-basic-run).

### 1.5. Run with custom templates (TrueMultimer)
Instead of using the default search through the PDB database for structural templates, you can provide a custom database. AlphaPulldown supports a feature called "True Multimer," which allows AlphaFold to use multi-chain structural templates during the prediction process. This can be beneficial for protein complexes where the arrangement of the chains may vary. True Multimer mode will arrange different complex subunits as in the template. 

#### Input

1. **Prepare a FASTA File:** Create a FASTA file containing all protein sequences that will be used for predictions as outlined in [1.1 Basic run](#11-basic-run).
   ${\color{red} remove\ all\ special\ symbols \from \fasta}$
3. **Create a Template Directory:** Designate a folder (e.g., "templates") to store your custom template files in PDB or CIF format.
4. **Create a description file:** This `description.csv` file links protein sequences to templates:

```
>proteinA,TMPL.cif,A
>proteinB,TMPL.cif,B
```

   * **Column 1** (>proteinA): Must exactly match protein descriptions from your FASTA file. 
   * **Column 2** (TMPL.cif): The filename of your template structure in PDB or CIF format.
   * **Column 3** (A): The chain ID within the template that the query sequence corresponds to.
     
**For Multiple Templates:**  If you want to provide multiple templates for a single protein, add additional rows with the same protein name but different templates and chain IDs:
```
>proteinA,TMPL.cif,A
>proteinA,TMP2.cif,B
>proteinB,TMPL.cif,B
```

>[!Note]
>Your template will be renamed to a PDB code taken from *_entry_id*. If you use a *.pdb file instead of *.cif, AlphaPulldown will first try to parse the PDB code from the file. Then it will check if the filename is 4-letter long. If it is not, it will generate a random 4-letter code and use it as the PDB code.

#### Script Execution

```bash
  create_individual_features.py \
    --fasta_paths=<sequences.fasta> \
    --path_to_mmt=<path to template directory>/ \
    --description_file=<description.csv> \
    --data_dir=<path to alphafold databases> \
    --output_dir=<dir to save the output objects> \ 
    --max_template_date=<any date you want, format like: 2050-01-01> \
    --save_msa_files=True \
    --use_precomputed_msas=True \
    --skip_existing=True
```
For FLAGS explanation, see [1.1. Basis run](#11-basic-run).

#### Output

Pickle format features for each protein in the `description.csv` file stored in the ```output_dir```. 
${\color{red}Add\ True\ Multimer\ limitations}$ 

#### Next step

Go to the next step [2.X. Template run](#2-predict-structures-gpu-stage) ${\color{red}Correct}$ 

<br>

## 2. Predict structures (GPU stage)
### 2.1. Basic run
This step requires the pickle files (.pkl) generated during the [first stage](#1-compute-multiple-sequence-alignment-msa-and-template-features-cpu-stage).
Additionally, you'll need to provide a list of protein combinations you intend to predict.

#### Input

Here's how to structure your combinations file `protein_list.txt`, with explanations:

**Prediction of monomers**:
  ```
  proteinA
  proteinB
  proteinC,1-100  
  ```
  * Each line is a separate prediction
  * Lines like `proteinA` will trigger a prediction of the entire sequence.
  * To predict specific residue ranges (e.g., the first 100 residues of proteinC), use the format "proteinC,1-100".

 **Prediction of complexes**:
   ```
   proteinA;proteinB;proteinC
   proteinB;proteinB 
   proteinB,4
   proteinC,2;proteinA
   proteinA,4,1-100;proteinB
   ```
   * Use semicolons (`;`) to separate protein names within a complex.
   * Instead of repeating the protein name for homo-oligomers, specify the number of copies after the protein's name (e.g., `proteinB,4` for a tetramer).
   * Combine residue ranges and homooligomer notation for specific predictions (e.g., `proteinA,4,1-100;proteinB`).

#### Script Execution Structure Prediction
To predict structures, activate the AlphaPulldown environment and run the script `run_multimer_jobs.py` as follows:

```bash
source activate AlphaPulldown
run_multimer_jobs.py \
  --mode=custom \
  --monomer_objects_dir=<dir that stores feature pickle files> \
  --data_dir=<path to alphafold databases> \
  --protein_lists=<protein_list.txt> \
  --output_path=<path to output directory> \ 
  --num_cycle=<any number e.g. 3> \
  --num_predictions_per_model=1 
```

Explanation of arguments:
* Instead of `<dir that stores feature pickle files>` provide the path to the directory containing the `.pkl` feature files generated in the [previous step](#11-basic-run). The path is the same as `--output_dir` for `create_individual_features.py`.
* Instead of `<protein_list.txt>` provide the path to a text file containing a list of protein combinations to be modeled.
* Instead of `<path to output directory>` provide a path where subdirectories containing the final structures will be saved.
* Instead of `<path to alphafold databases>` provide a path to the genetic database (see [0. Alphafold-databases](#installation) of the installation part).
* `--num_cycle`: specifies the number of times the AlphaFold neural network will run, using the output of one cycle as input for the next. Increasing this number may improve the quality of the final structures (especially for large complexes), but it will also increase the runtime.
* `--num_predictions_per_model`: Specifies the number of predictions per model. The number of predicted structures N\*5.  The default value is 1, which gives 5 structures.

$\text{\color{red} Correct FLAGS description}$

<details>
   <summary>
    Full list of arguments (FLAGS):
   </summary>

* `--alphalink_weight:` Path to AlphaLink neural network weights
* `--data_dir:` Path to params directory
* `--job_index:` index of sequence in the fasta file, starting from 1 (an integer)
* `--mode:` <pulldown|all_vs_all|homo-oligomer|custom>: choose the mode of running multimer jobs (default: 'pulldown')
* `--models_to_relax:` <None|All|Best>: Which models to relax. Default is None, meaning no model will be relaxed (default: 'None')
* `--monomer_objects_dir:` a list of directories where monomer objects are stored (a comma separated list)
* `--oligomer_state_file:` path to oligomer state files
* `--output_path:` output directory where the region data is going to be stored
* `--protein_lists:` protein list files (a comma separated list)
* `--unifold_model_name:` <multimer_af2|multimer_ft|multimer|multimer_af2_v3|multimer_af2_model45_v3>: choose unifold model structure (default: 'multimer_af2')
* `--unifold_param:` Path to UniFold neural network weights
* `--[no]use_alphalink:` Whether AlphaLink models are going to be used. Default is False (default: 'false')
* `--[no]use_unifold:` Whether UniFold models are going to be used. Default is False (default: 'false')

absl.app:

* `-?,--[no]help:` show this help (default: 'false')
* `--[no]helpfull:` show full help (default: 'false')
* `--[no]helpshort:` show this help (default: 'false')
* `--[no]helpxml:` like --helpfull, but generates XML output (default: 'false')
* `--[no]only_check_args:` Set to true to validate args and exit (default: 'false')
* `--[no]pdb:` Alias for --pdb_post_mortem (default: 'false')
* `--[no]pdb_post_mortem:` Set to true to handle uncaught exceptions with PDB post mortem (default: 'false')
* `--profile_file:` Dump profile information to a file (for python -m pstats). Implies --run_with_profiling.
* `--[no]run_with_pdb:` Set to true for PDB debug mode (default: 'false')
* `--[no]run_with_profiling:` Set to true for profiling the script. Execution will be slower, and the output format might change over time (default: 'false')
* `--[no]use_cprofile_for_profiling:` Use cProfile instead of the profile module for profiling. This has no effect unless --run_with_profiling is set (default: 'true')

absl.logging:
* `--[no]alsologtostderr:` also log to stderr? (default: 'false')
* `--log_dir:` directory to write logfiles into (default: '')
* `--logger_levels:` Specify log level of loggers. The format is a CSV list of `name:level`. Where `name` is the logger name used with `logging.getLogger()`, and `level` is a level name (INFO, DEBUG, etc). e.g. `myapp.foo:INFO,other.logger:DEBUG` (default: '')
* `--[no]logtostderr:` Should only log to stderr? (default: 'false')
* `--[no]showprefixforinfo:` If False, do not prepend prefix to info messages when it's logged to stderr, --verbosity is set to INFO level, and python logging is used (default: 'true')
* `--stderrthreshold:` log messages at this level, or more severe, to stderr in addition to the logfile. Possible values are 'debug', 'info', 'warning', 'error', and 'fatal'. Obsoletes --alsologtostderr. Using --alsologtostderr cancels the effect of this flag. Please also note that this flag is subject to --verbosity and requires logfile not be stderr (default: 'fatal')
* `-v,--verbosity:` Logging verbosity level. Messages logged at this level or lower will be included. Set to 1 for debug logging. If the flag was not set or supplied, the value will be changed from the default of -1 (warning) to 0 (info) after flags are parsed (default: '-1') (an integer)

absl.testing.absltest:
* `--test_random_seed:` Random seed for testing. Some test frameworks may change the default value of this flag between runs, so it is not appropriate for seeding probabilistic tests (default: '301') (an integer)
* `--test_randomize_ordering_seed:` If positive, use this as a seed to randomize the execution order for test cases. If "random", pick a random seed to use. If 0 or not set, do not randomize test case execution order. This flag also overrides the TEST_RANDOMIZE_ORDERING_SEED environment variable (default: '')
* `--test_srcdir:` Root of directory tree where source files live (default: '')
* `--test_tmpdir:` Directory for temporary testing files (default: '/tmp/absl_testing')
* `--xml_output_file:` File to store XML test results (default: '')

alphapulldown.scripts.run_structure_prediction:
* `--[no]benchmark:` Run multiple JAX model evaluations to obtain a timing that excludes the compilation time, which should be more indicative of the time required for inferencing many proteins (default: 'false')
* `--[no]compress_result_pickles:` Whether the result pickles are going to be gzipped. Default is False (default: 'false')
* `--crosslinks:` Path to crosslink information pickle for AlphaLink
* `--data_directory:` Path to directory containing model weights and parameters
* `--description_file:` Path to the text file with multimeric template instruction
* `--desired_num_msa:` A desired number of msa to pad (an integer)
* `--desired_num_res:` A desired number of residues to pad (an integer)
* `--features_directory:` Path to computed monomer features; repeat this option to specify a list of values
* `--fold_backend:` Folding backend that should be used for structure prediction (default: 'alphafold')
* `-i,--input:` Folds in format [fasta_path:number:start-stop],; repeat this option to specify a list of values
* `--model_names:` Names of models to use, e.g. model_2_multimer_v3 (default: all models)
* `--model_preset:` <monomer|monomer_casp14|monomer_ptm|multimer>: Choose preset model configuration - the monomer model, the monomer model with extra ensembling, monomer model with pTM head, or multimer model (default: 'monomer')
* `--msa_depth:` Number of sequences to use from the MSA (by default is taken from AF model config) (an integer)
* `--[no]msa_depth_scan:` Run predictions for each model with logarithmically distributed MSA depth (default: 'false')
* `--[no]multimeric_template:` Whether to use multimeric templates (default: 'false')
* `--[no]no_pair_msa:` Do not pair the MSAs when constructing multimer objects (default: 'false')
* `--num_cycle:` Number of recycles, defaults to 3 (default: '3') (an integer)
* `--num_predictions_per_model:` Number of predictions per model, defaults to 1 (default: '1') (an integer)
* `-o,--output_directory:` Path to output directory. Will be created if not exists
* `--path_to_mmt:` Path to directory with multimeric template mmCIF files
* `--protein_delimiter:` Delimiter for proteins of a single fold (default: '+')
* `--random_seed:` The random seed for the data pipeline. By default, this is randomly generated. Note that even if this is set, Alphafold may still not be deterministic, because processes like GPU inference are nondeterministic (an integer)
* `--[no]remove_result_pickles:` Whether the result pickles are going to be removed (default: 'true')
* `--[no]skip_templates:` Do not use template features when modelling (default: 'false')
* `--[no]use_ap_style:` Change output directory to include a description of the fold as seen in previous alphapulldown versions (default: 'false')
* `--[no]use_gpu_relax:` Whether to run Amber relaxation on GPU. Default is True (default: 'true')

tensorflow.python.ops.parallel_for.pfor:
* `--[no]op_conversion_fallback_to_while_loop:` DEPRECATED: Flag is ignored (default: 'true')

tensorflow.python.tpu.client.client:
* `--[no]hbm_oom_exit:` Exit the script when the TPU HBM is OOM (default: 'true')
* `--[no]runtime_oom_exit:` Exit the script when the TPU runtime is OOM (default: 'true')

tensorflow.python.tpu.tensor_tracer_flags:
* `--delta_threshold:` Log if history based diff crosses this threshold (default: '0.5') (a number)
* `--[no]tt_check_filter:` Terminate early to check op name filtering (default: 'false')
* `--[no]tt_single_core_summaries:` Report single core metric and avoid aggregation (default: 'false')

absl.flags:
* `--flagfile:` Insert flag definitions from the given file into the command line (default: '')
* `--undefok:` comma-separated list of flag names that it is okay to specify on the command line even if the program does not define a flag with that name. IMPORTANT: flags in this list that have arguments MUST use the --flag=value format (default: '')
  
</details>

#### Output

The `run_multimer_jobs.py` script generates a set of directories for each specified protein complex.
Full structure of the output directories is the following:
```
<complex_name>/
    <complex_name>_ranked_{0,1,2,3,4}.png
    ranked_{0,1,2,3,4}.pdb
    ranking_debug.json
    result_model_{1,2,3,4,5}_*.pkl
    timings.json
    unrelaxed_model_{1,2,3,4,5}_*.pdb
```
Please refer to the [AlphaFold manual](https://github.com/google-deepmind/alphafold) for more details on output files.

**Key files**:
* `ranked_{0,1,2,3,4}.pdb`: Structure files ranked from best to worst predicted quality.
*  `<complex_name>_ranked_{0,1,2,3,4}.png`: Plots of predicted aligned errors (PAE) providing a visual representation of the structure's confidence.

> [!Caution]
> AlphaPulldown is designed for screening, so its default output doesn't relax structures. To relax the top-ranked structure (`ranked_0.pdb`), you can run AlphaPulldown with the `--models_to_relax=best` flag.

### 2.2. Example run with SLURM (EMBL cluster).

If you run AlphaPulldown on a computer cluster, you may want to execute feature creation in parallel. Here, we provide an example of code that is suitable for a cluster that utilizes SLURM Workload Manager.

#### Input

For this step, you need an example input file: [`custom_mode.txt`](../example_data/custom_mode.txt) and features (`.pkl`) files generated in the previous step [1.2 Example run with SLURM (EMBL cluster)](12-example-run-with-slurm-embl-cluster).

#### Script Execution

Create the ```run_multimer_jobs_SLURM.sh``` script and place the following code in it. Don't forget to change the input of `run_multimer_jobs.sh` script as described [previously in manual](#2-predict-structures-gpu-stage):

```bash
#!/bin/bash

#A typical run takes couple of hours but may be much longer
#SBATCH --job-name=array
#SBATCH --time=2-00:00:00

#log files:
#SBATCH -e logs/run_multimer_jobs_%A_%a_err.txt
#SBATCH -o logs/run_multimer_jobs_%A_%a_out.txt

#qos sets priority
#SBATCH --qos=low

#SBATCH -p gpu
#lower end GPUs might be sufficient for pairwise screens:
#SBATCH -C "gpu=2080Ti|gpu=3090"

#Reserve the entire GPU so no-one else slows you down
#SBATCH --gres=gpu:1

#Limit the run to a single node
#SBATCH -N 1

#Adjust this depending on the node
#SBATCH --ntasks=8
#SBATCH --mem=64000

module load Anaconda3 
module load CUDA/11.8.0
module load cuDNN/8.7.0.84-CUDA-11.8.0
source activate AlphaPulldown

MAXRAM=$(echo `ulimit -m` '/ 1024.0'|bc)
GPUMEM=`nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits|tail -1`
export XLA_PYTHON_CLIENT_MEM_FRACTION=`echo "scale=3;$MAXRAM / $GPUMEM"|bc`
export TF_FORCE_UNIFIED_MEMORY='1'

# CUSTOMIZE THE FOLLOWING SCRIPT PARAMETERS FOR YOUR SPECIFIC TASK:
####
run_multimer_jobs.py \
  --mode=custom \
  --monomer_objects_dir=<dir that stores feature pickle files> \ 
  --protein_lists=<protein_list.txt> \
  --output_path=<path to output directory> \ 
  --num_cycle=<any number e.g. 3> \
  --data_dir=/scratch/AlphaFold_DBs/2.3.2/ \
  --job_index=$SLURM_ARRAY_TASK_ID
####
```
$\textrm{\color{red}Do we need to specify data dir?}$
$\textrm{\color{red}Can we delete custom mode here?}$
$\textrm{\color{red}Num of pred per model?}$

Make the script executable by running:

```bash
chmod +x run_multimer_jobs_SLURM.sh
```

Next, for `custom` mode, execute the following commands, replacing `<protein_list.txt>` with the path to your protein combinations file:

```bash
mkdir -p logs
#Count the number of jobs corresponding to the number of sequences:
count=`grep -c "" <protein_list.txt>` #count lines even if the last one has no end of line
sbatch --array=1-$count example_data/run_multimer_jobs_SLURM.sh
```

 <details>
   
   <summary>
   Commands for other modes:
   </summary>

For `pulldown` mode for two files (for more files, create `count3`, `count4`, etc. variables and add them as a multiplier to the product):

```bash
mkdir -p logs
#Count the number of jobs corresponding to the number of sequences:
count1=`grep -c "" <protein_list1.txt>` #count lines even if the last one has no end of line
count2=`grep -c "" <protein_list2.txt>` #count lines even if the last one has no end of line
count=$(( $count1 * $count2 ))
sbatch --array=1-$count example_data/run_multimer_jobs_SLURM.sh
```

For `all_vs_all` mode:

```bash
mkdir -p logs
#Count the number of jobs corresponding to the number of sequences:
count1=`grep -c "" <protein_list.txt>` #count lines even if the last one has no end of line
count=$(( $count1 * ( $count1 - 1) / 2 ))
sbatch --array=1-$count example_data/run_multimer_jobs_SLURM.sh
```

 </details>


### 2.3. Pulldown and All versus all modes
Instead of manually typing all combinations of proteins, AlphaPulldown provides two different modes of automatic generation of such combinations.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/AP_modes_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/AP_modes.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/AP_modes.png">
</picture>

#### Multiple inputs "pulldown" mode

This mode allows to provide two or more lists of proteins that will generate all combinations of proteins from one list with all proteins from another list.
If you want to emulate _in silico_ pulldown of some hypothetical proteinA bait against proteins B-G you can use two `protein_list.csv` files:

The first `protein_list1.csv`:
```
proteinA
```

The second `protein_list2.csv`:
```
proteinB
proteinC
proteinD
proteinE
proteinF
proteinG
```

This results in the following combinations of proteins: A-B, A-C, A-D, A-E, A-F, A-G.

Can you add the third `protein_list3.csv`:
```
proteinX
proteinZ
```
And resulting models will contain proteins A-B-X, A-B-Z, A-C-X, A-C-Z...

In fact, you can provide as many files as you wish, the number of combinations you will receive is the product of numbers of lines in the input files.

Lines in files should not necessarily be single proteins. Input files follow the same rules as described for [2.1 Basic run](#21-basic-run). It can contain several protein names, indicate a number of oligomers, and have residue ranges.

To run `run_multimer_jobs.py` in `pulldown` mode use the following script:

```bash
run_multimer_jobs.py \
  --mode=pulldown \
  --monomer_objects_dir=<dir that stores feature pickle files> \ 
  --protein_lists=<protein_list1.csv>,<protein_list2.csv> \
  --output_path=<path to output directory> \
  --data_dir=<path to AlphaFold data directory> \ 
  --num_cycle=<any number e.g. 3> 
```
From [2.1 Basic run](#21-basic-run) this example is different with:
* `--mode=pulldown` flag ($\text{\color{red}don't need to mention it if delete custom mode flag form the basic run}$.) that defines the mode of the run.
* Instead of `<protein_list1.csv>`,`<protein_list2.csv>` provides the paths to the files containing a list of protein combinations to be modeled.
 
#### "all_vs_all" mode

In this mode, AlphaPulldown takes lines from the input `protein_list.csv` file and generates all possible combinations of these lines.

It is useful when you have a set of proteins, and you want to find out which interact with which. If you provide the list of proteins:
```
proteinA
proteinB
proteinC
proteinD
proteinE
```
The resulting models will be combinations of proteins A-B, A-C, A-D, A-E, B-C, B-D, B-E, C-D, C-E, D-E. 

>[!Caution]
> The number of predictions rapidly increases with the number of lines in the input `protein_list.csv`. 

Lines in files should not necessarily be single proteins. Input files follow the same rules as described for [2.1 Basic run](#21-basic-run). It can contain several protein names, indicate a number of oligomers, and have residue ranges.

To run `run_multimer_jobs.py` in `all_vs_all` mode use the following script:

```bash
run_multimer_jobs.py \
  --mode=all_vs_all \
  --monomer_objects_dir=<dir that stores feature pickle files>
  --protein_lists=<protein_list.csv> \
  --output_path=<path to output directory> \ 
  --data_dir=<path to AlphaFold data directory> \ 
  --num_cycle=<any number e.g. 3> 
```

### 2.3. Run with custom templates (TrueMultimer)

### 2.4. Run with crosslinking-dat (AlphaLink2)

As [Stahl et al., 2023](https://www.nature.com/articles/s41587-023-01704-z) showed, integrating cross-link data with AlphaFold could improve the modelling quality in 
some challenging cases. Thus AlphaPulldown has integrated [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main) pipeline 
and allows the user to combine cross-link data with AlphaFold Multimer inference, without the need to calculate MSAs from scratch again.

> **Cite:** If you use AlphaLink2, please remember to cite:
> Stahl, K., Demann, L., Bremenkamp, R., Warneke, R., Hormes, B., Stülke, J., Brock, O., Rappsilber, J., Der, S.-M. ", & Mensch, S. (2024). Modelling protein complexes with crosslinking mass spectrometry and deep learning. BioRxiv, 2023.06.07.544059. https://doi.org/10.1101/2023.06.07.544059

Before using, install AlphaLink2 as described [here](#4-installation-for-cross-link-input-data-by-alphalink2-optional).

#### Input

Besides features (`.pkl`) files generated in the [previous step](#11-basic-run) you need to prepare cross-link input data:

As instructed by [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main), information of cross-linked residues
between 2 proteins, inter-protein crosslinks A->B 1,50 and 30,80 and an FDR=20%, should look like: 

```
{'protein_A': {'protein_B': [(1, 50, 0.2), (30, 80, 0.2)]}}
```

and intra-protein crosslinks follow the same format: 

```
{'protein_A': {'protein_A': [(5, 20, 0.2)]}}
```

The keys in these dictionaries should be the same as your pickle files created by [the first stage of AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown/blob/main/example_1.md). e.g. you should have ```protein_A.pkl``` 
and ```protein_B.pkl``` already calculated. 

Dictionaries like these should be stored in **```.pkl.gz```** files and provided to AlphaPulldown in the next step. You can use the script from [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main)
to prepare these pickle files. 

>[!Warning]
>The dictionaries are 0-indexed, i.e., residues start from 0.

#### Run with AlphaLink2 prediction via AlphaPulldown
Within the same conda environment, run in e.g. ```custom``` mode:

```bash
run_multimer_jobs.py --mode=custom \
--num_predictions_per_model=1 \
--output_path=/scratch/scratch/user/output/models \
--data_dir=/g/alphafold/AlphaFold_DBs/2.3.0/ I am running a few minutes late; my previous meeting is running over.
--protein_lists=custom.txt \
--monomer_objects_dir=/scratch/user/output/features \
--job_index=$SLURM_ARRAY_TASK_ID --alphalink_weight=/scratch/user/alphalink_weights/AlphaLink-Multimer_SDA_v3.pt \
--use_alphalink=True --crosslinks=/path/to/crosslinks.pkl.gz 
```

The other modes provided by AlphaPulldown also work in the same way.

## 3. Analysis and Visualization
The resulting predictions from the [step 2](#2-predict-structures-gpu-stage) can be used directly as they are. However, for evaluation systematization and ranking of the prediction, you can use an interactive [Jupyter Notebook](https://jupyter.org/) and/or table with models scores. 

### Jupyter Notebook

Go to the model's output directory from the [step 2](#2-predict-structures-gpu-stage).
```bash
cd <models_output_dir>
```

And run the script in the activated conda environment:
```bash
source activate AlphaPulldown
create_notebook.py --cutoff=5.0 --output_dir=<models_output_dir>
```
<details>
   
<summary>
Parameters:
</summary>

* `--cutoff`:
  check the value of PAE between chains. In the case of multimers, the analysis program will create the notebook only from models with inter-chain PAE values smaller than the cutoff. Increases this parameter if you miss predictions in your notebook (e.g., 50).
* `--output_dir`:
  Directory where predicted models are stored $\text{\color{red}Why do we need to change the dir then?}$
* `--pae_figsize`:
   Figsize of pae_plot, default is 50
* `--surface_thres` - $\text{\color{red}Add description or delete}$

</details>

This command will yield an `output.ipynb`, which you can open via JupyterLab. JupyterLab is already installed when installing AlphaPulldown with pip. Thus, to view the notebook launch the created notebook:
```bash
jupyter-lab output.ipynb
```
>[!Note]
>If you run AlphaPulldown on a remote computer cluster, you will need a graphical connection, network mount of the remote directory, or a copy of the entire `<models_output_dir>` to open the notebook in a browser.
>
>For an example of how to establish a remote connection, please refer to the [Run on EMBL cluster](#add_link) part of this manual $\text{\color{red}cahnge link}$. 

In the JupyterLab window, choose output.ipynb if it is not opened automatically and then go to the **Run** > **Run All Cells**; after all cells executions for every proteins complex, you will see PAE plots, interactive structures colored by pLDDT, interactive structures colored by a chain.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/Jupyter_results_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/Jupyter_results.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/Jupyter_results.png">
</picture>

<br>
</br>

To zoom in PAE plots, click twice on them. To increase the number of displayed interactive models, add argument `models` to the `parse_results()` or `parse_results_colour_chains()` functions.

```python
parse_results('./ProteinA_and_ProteinB', models=10)
```

> [!WARNING]
> If Jupyter Notebook has too many proteins, some interactive structures may disappear due to memory limitations. To restore the output of the cell, just rerun it by choosing it and going to **Run** > **Run Selected Cell** or pressing **Shift + Enter**.


### Results table

Making a CSV table with structural properties and scores requires the download of the singularity image ```alpha-analysis.sif```. Pleaes refer to the installation [instruction](#3-installation-for-the-analysis-step-optional).

To execute the singularity image (i.e. the sif file) run:

```bash
singularity exec \
    --no-home \
    --bind </path/to/your/output/dir:/mnt> \
    <path to your downloaded image>/alpha-analysis_jax_0.4.sif \
    run_get_good_pae.sh \
    --output_dir=/mnt \
    --cutoff=10
```
$\text{\color{red}What is /path/to/your/output/dir:/mnt}$. 

By default, you will have a csv file named ```predictions_with_good_interpae.csv``` created in the directory ```/path/to/your/output/dir``` as you have given in the command above. ```predictions_with_good_interpae.csv``` reports: 1. iptm, iptm+ptm scores provided by AlphaFold 2. mpDockQ score developed by [Bryant _et al._, 2022](https://gitlab.com/patrickbryant1/molpc)  3. PI_score developed by [Malhotra _et al._, 2021](https://gitlab.com/sm2185/ppi_scoring/-/wikis/home). The detailed explainations on these scores can be found in our paper and an example screenshot of the table is below. ![example](./example_table_screenshot.png)


$\text{\color{red}Change description, add scores}$

<br>

## Running with SLURM (EMBL cluster)
Computational clusters often use SLURM (Simple Linux Utility for Resource Management) to efficiently manage and schedule jobs. SLURM allows users to allocate resources and run jobs on HPC systems seamlessly; besides, it allows to run all jobs in parallel as a job array. The EMBL cluster utilizes SLURM, and to run AlphaPulldown on this cluster, you need to submit your job scripts through SLURM's scheduling system. This part of the manual will provide the necessary SLURM sbatch scripts to run AlphaPulldown. 
>[!NOTE]
>For more details about the SLURM system on the EMBL cluster, please refer to the [EMBL Cluster wiki](https://wiki.embl.de/cluster/Main_Page) using the EMBL network.



<br>

# Downstream analysis

## Jupyther notebook

To create a Jupyter Notebook, follow the instructions provided [previously](#jupyter-notebook). 

**Jupyter Notebook remote access**

To connect remotely, first launch Jupyter Notebook on the cluster. You can choose a different port number if the selected one is already in use:

```bash 
jupyter-lab --no-browser --port=8895 output.ipynb
```
The output of this command will provide you with a link and a token for connection. The token is a unique string that is required for authentication when you first access the Jupyter Notebook interface. Here is an example of what the output might look like:

```
http://localhost:8895/?token=abc123def456
```

Next, establish an SSH tunnel using your local machine's command line. The port numbers should match those used in the previous command. Replace <login> with your EMBL login, or if you are using a different cluster, provide the address of that cluster and your login in the format `<login>@<address>`:

```bash
ssh -N -f -L localhost:8895:localhost:8895 <login>@login01.cluster.embl.de
```

After establishing the SSH tunnel, you can access the Jupyter Notebook in your web browser. Open your browser and navigate to the following URL:

```
http://localhost:8895
```

You will be prompted to enter the token provided earlier when you launched Jupyter Lab on the cluster. Copy and paste the token from the command output into the browser prompt to gain access.

## Results table 

To create a results table, please refer to the relevant [section of the manual](#results-table).

## Results management scripts
AlphaPulldown provides scripts to help optimize data storage and prepare structures for deposition.

### Deceraes the size of AlphaPulldown output
The most space-consuming part of the [structure prediction results](#2-predict-structures-gpu-stage) are pickle files `result_model_{1,2,3,4,5}_*.pkl files`. Please refer to the [AlphaFold manual](https://github.com/google-deepmind/alphafold) for more details on output files. Some information in these files is needed only for very special tasks. The `truncate_pickles.py` script copies the output of AlphaPulldown to a new directory and deletes the specified information from the pickle files. It may decrease the size of the output up to 100 times. 

```bash
source activate AlphaPulldown
truncate_pickles.py \
  --src_dir=</path/to/source> \
  --dst_dir=</path/to/destination> \
  --keys_to_exclude=aligned_confidence_probs,distogram,masked_msa \
  --number_of_threads=4 
```
* `--src_dir=</path/to/source>`: Replace `</path/to/source>` with the path to the structures output directory. This should be the same as the `--output_path` for the `run_multimer_jobs.py` script from the [Predict Structures](#2-predict-structures-gpu-stage) step.
* `--dst_dir=</path/to/destination>`: Replace `</path/to/destination>` with the path of the directory to copy the truncated results to.
* `--keys_to_exclude=aligned_confidence_probs,distogram,masked_msa`: A comma-separated list of keys that should be excluded from the copied pickle files. The default keys are "aligned_confidence_probs,distogram,masked_msa".
* `--number_of_threads=4`: Number of threads to run in parallel. 

### Convert Models from PDB Format to ModelCIF Format

With PDB files now being marked as a legacy format, here is a way to convert PDB files produced by the [AlphaPulldown](https://github.com/KosinskiLab/AlphaPulldown) pipeline into [mmCIF](https://mmcif.wwpdb.org) files, including the [ModelCIF](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Index/) extension.

In addition to the general mmCIF tables, ModelCIF adds information relevant for a modeling experiment. This includes target-sequence annotation and a modeling protocol, describing the process by which a model was created, including software used with its parameters. To help users assess the reliability of a model, various quality metrics can be stored directly in a ModelCIF file or in associated files registered in the main file. ModelCIF is also the preferred format for [ModelArchive](https://www.modelarchive.org).

As AlphaPulldown relies on [AlphaFold](https://github.com/google-deepmind/alphafold) to produce model coordinates, multiple models may be predicted in a single experiment. To accommodate different needs, `convert_to_modelcif.py` offers three major modes:

* Convert all models into ModelCIF in separate files.
* Only convert a specific single model.
* Convert a specific model to ModelCIF but keep additional models in a Zip archive associated with the representative ModelCIF formatted model.

#### Installation

To run `convert_to_modelcif.py`, the Python module [modelcif](https://pypi.org/project/modelcif/) is needed in addition to the regular AlphaPulldown Python environment. It is recommended to install it with the conda command: `conda install -c conda-forge modelcif`.

#### 1. Convert all models to separate ModelCIF files

The most general call of the conversion script, without any non-mandatory arguments, will create a ModelCIF file and an associated Zip archive for each model of each complex found in the `--ap_output` directory:

```bash
source activate AlphaPulldown
convert_to_modelcif.py \
  --ap_output <output path of run_multimer_jobs.py> \
  --monomer_objects_dir <output directory of feature creation>
```

* `--ap_output`: Path to the structures directory. This should be the same as the `--output_path` for the `run_multimer_jobs.py` script from the [Predict Structures](#2-predict-structures-gpu-stage) step.
* `--monomer_objects_dir`: Path to the directory containing the .pkl feature files generated in the [Compute Multiple Sequence Alignment (MSA) and Template Features](#1-compute-multiple-sequence-alignment-msa-and-template-features-cpu-stage) step. This is the same parameter as `--monomer_objects_dir` in the `run_multimer_jobs.py` script.

The output is stored in the path that `--ap_output` points to. After running `convert_to_modelcif.py`, you should find a ModelCIF file and a Zip archive for each model PDB file in the AlphaPulldown output directory:

<details>
   <summary>Output</summary>

```
ap_output
    protein1_and_protein2
        |-ranked_0.cif
        |-ranked_0.pdb
        |-ranked_0.zip
        |-ranked_1.cif
        |-ranked_1.pdb
        |-ranked_1.zip
        |-ranked_2.cif
        |-ranked_2.pdb
        |-ranked_2.zip
        |-ranked_3.cif
        |-ranked_3.pdb
        |-ranked_3.zip
        |-ranked_4.cif
        |-ranked_4.pdb
        |-ranked_4.zip
        ...
    ...
```

 </details>


#### 2. Only convert a specific single model for each complex

If only a single model should be translated to ModelCIF, use the `--model_selected` option. Provide the ranking of the model as the value. For example, to convert the model ranked 0:

```bash
source activate AlphaPulldown
convert_to_modelcif.py \
  --ap_output <output path of run_multimer_jobs.py> \
  --monomer_objects_dir <output directory of feature creation> \
  --model_selected 0
```

This will create only one ModelCIF file and Zip archive in the path pointed at by `--ap_output`:

<details>
   <summary>Output</summary>
  
```
ap_output
    protein1_and_protein2
        |-ranked_0.cif
        |-ranked_0.pdb
        |-ranked_0.zip
        |-ranked_1.pdb
        |-ranked_2.pdb
        |-ranked_3.pdb
        |-ranked_4.pdb
        ...
    ...
```

 </details>

Besides `--model_selected`, the arguments are the same as for scenario 1.


#### 3. Have a representative model and keep associated models

Sometimes you want to focus on a certain model from the AlphaPulldown pipeline but don't want to completely discard the other models generated. For this, `convert_to_modelcif.py` can translate all models to ModelCIF but store the excess in the Zip archive of the selected model. This is achieved by adding the option `--add_associated` together with `--model_selected`.

```bash
source activate AlphaPulldown
convert_to_modelcif.py \
  --ap_output <output path of run_multimer_jobs.py> \
  --monomer_objects_dir <output directory of feature creation> \
  --model_selected 0 \
  --add-associated
```

Arguments are the same as in scenarios 1 and 2 but include `--add_associated`.

The output directory looks similar to when only converting a single model:

<details>
   <summary>Output</summary>

```
ap_output
    protein1_and_protein2
        |-ranked_0.cif
        |-ranked_0.pdb
        |-ranked_0.zip
        |-ranked_1.pdb
        |-ranked_2.pdb
        |-ranked_3.pdb
        |-ranked_4.pdb
        ...
    ...
```

 </details>

But a peek into `ranked_0.zip` shows that it stored ModelCIF files and Zip archives for all remaining models of this modeling experiment:

<details>
   <summary>Output</summary>

```
ranked_0.zip
    |-ranked_0_local_pairwise_qa.cif
    |-ranked_1.cif
    |-ranked_1.zip
    |-ranked_2.cif
    |-ranked_2.zip
    |-ranked_3.cif
    |-ranked_3.zip
    |-ranked_4.cif
    |-ranked_4.zip
```

 </details>

#### Associated Zip Archives

`convert_to_modelcif.py` produces two kinds of output: ModelCIF files and Zip archives for each model. The latter are called "associated files/archives" in ModelCIF terminology. Associated files are registered in their corresponding ModelCIF file by categories [`ma_entry_associated_files`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_entry_associated_files.html) and [`ma_associated_archive_file_details`](https://mmcif.wwpdb.org/dictionaries/mmcif_ma.dic/Categories/ma_associated_archive_file_details.html). Historically, this scheme was created to offload AlphaFold's pairwise alignment error lists, which drastically increase file size. Nowadays, the Zip archives are used for all kinds of supplementary information on models, not handled by ModelCIF.

#### Miscellaneous Options

At this time, there is only one option left unexplained: `--compress`. It tells the script to compress ModelCIF files using Gzip. In the case of `--add_associated`, the ModelCIF files in the associated Zip archive are also compressed.
