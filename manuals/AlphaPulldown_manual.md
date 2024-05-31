# AlphaPulldown Manual

`version 2.0.0 (beta)`

> AlphaPulldown fully **maintains backward compatibility** with input files and scripts from versions 1.x. For instructions on using older files and scripts, please refer to the sections marked "Older Version".

## About AlphaPulldown

AlphaPulldown is an implementation of [AlphaFold2-Multimer](https://github.com/google-deepmind/alphafold) designed for customizable high-throughput screening of protein-protein interactions. Besides, AlphaPulldown provides additional customizations of the AlphaFold which include custom structural multimeric templates (TrueMultimer), MMseqs2 multiple sequence alignment (MSA) and [ColabFold](https://github.com/sokrypton/ColabFold) databases, proteins fragments predictions, and implementation of cross-link mass spec data using [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main).

AlphaPulldown can be used in two ways: as a set of **Python scripts**, which this manual covers, and as a **Snakemake pipeline**. For details on using the Snakemake pipeline, please refer to the separate GitHub [**repository**](https://github.com/KosinskiLab/AlphaPulldownSnakemake).

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/AP_pipeline_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/AP_pipeline.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/AP_pipeline.png">
</picture>
 
The original [AlphaFold2-Multimer](https://github.com/google-deepmind/alphafold) protein complex prediction pipeline may be split into two steps: **(1)** the databases search step that generates Features and MSA for every individual protein sequence and **(2)** protein complex structure prediction itself. AlphaPluldown executes these steps as independent scripts which is more efficient for modeling a large number of protein complexes. Additionally, **(3)** AlphaPluldown provides two options for the downstream analysis of the resulting protein models.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/AP_modes_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/AP_modes.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/AP_modes.png">
</picture>

A key strength of AlphaPulldown is its ability to flexibly define how proteins are combined for structure prediction of protein complexes. Here are the three main approaches you can use:

* **Single file**(custom mode): Create a file where each row lists the protein sequences you want to predict together.
* **Multiple Files**(pulldown mode): Provide several files, each containing protein sequences. AlphaPulldown will automatically generate all possible combinations by pairing rows of protein names from each file.
* **All versus all**: AlphaPulldown will generate all possible non-redundant combinations of proteins in the list. 

AlphaPulldown work pipeline is the following:

1) **Features and MSA**: At this step for every queried protein sequence AlphaFold searches for preinstalled databases using HMMER and calculates multiple sequence alignment (MSA) for all finden homologues. Additionally, AlphaFold searches for homolog structures that will be used as templates for features generation. This step requires only CPU to run.<be>
There are a few customizable options for this step:

   * To speed up the search process [MMSeq2](https://doi.org/10.1038/s41592-022-01488-1) instead of deafult HHMER can be used.<br>
   * Use custom MSA.
   * Use a custom structural template. Including a multimeric one (TrueMultimer mode).
  

2) **Structure prediction**: At this step, the AlaphaFold neural network runs and produces the final protein structure, which requires GPU computational powers.
   Here, AlphaPulldown allows:
   * Read all combinations of proteins to predict from one file or generate combinations of proteins using `pulldown` or `all_versus_all` modes.
   * Specify the number of residues that correspond to the part of the protein you want to predict.
   * Adjust MSA depth (allows control over how much the initial MSA influences the final model).
   * Crosslinking data implementation with [AlphaLink2](https://github.com/Rappsilber-Laboratory/AlphaLink2/tree/main).

3) **Results analysis**: The results for all predicted models could be systematized using one of the following options:
   * Table that contains various scores and physical parameters of protein complexes' interaction.
   * Jupyter notebook with interactive 3D models and PAE plots.
<br>

## Installation

#### 0. Alphafold databases

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
   
> [!NOTE]
> Since the local installation of all genetic databases is space-consuming, you can download the alternatively use the [remotely-run MMseqs2 and ColabFold databases](https://github.com/sokrypton/ColabFold). Follow the corresponding [instruction](#13-run-using-mmseqs2-and-colabfold-databases-faster). Nonetheless, for AlaphaPulldown to function, you have to download the parameters stored in the `params/` directory of AlpahFold.

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
   
   >**For older versions of AlphaFold**
   >
   >If you haven't updated your databases according to the requirements of AlphaFold 2.3.0, you can still use AlphaPulldown with your older version of AlphaFold database. Please follow the installation instructions on the [dedicated branch](https://github.com/KosinskiLab/AlphaPulldown/tree/AlphaFold-2.2.0).

#### 3. Installation for the Analysis step (optional)
For making Results table you need to have Singularity installed ($\text{\color{red}add instructions or link}$).

Download the singularity image: 

* If your results are from AlphaPulldown prior to version 1.0.0: [alpha-analysis_jax_0.3.sif](https://www.embl-hamburg.de/AlphaPulldown/downloads/alpha-analysis_jax_0.3.sif). 
* If your results are from AlphaPulldown with version >=1.0.0: [alpha-analysis_jax_0.4.sif](https://www.embl-hamburg.de/AlphaPulldown/downloads/alpha-analysis_jax_0.4.sif). 

Chrome users may not be able to download it after clicking the link. If so, please right-click and select "Save link as".


### Snakemake pipeline installation
AlphaPulldown Snakemake pipeline is independent and doesn't require the prior installation steps described in this manual. Its installation and running are comprehensibly described in the separate GitHub [**repository**](https://github.com/KosinskiLab/AlphaPulldownSnakemake).

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
At this step, you need to provide a [protein FASTA format](https://www.ncbi.nlm.nih.gov/WebSub/html/help/protein.html) file with all protein sequences that will be used for complexes prediction.
   ```
   >protein_A
   SEQUENCEOFPROTEINA
   >protein_B
   SEQUENCEOFPROTEINB
   ```

Then activate the AlphaPulldown environment and run script `create_individual_features.py` as follows:

   ```bash
   source activate AlphaPulldown
   ```
   ```bash
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
> The name of the pickles will be the same as the descriptions of the sequences  in fasta files (e.g. `>prtoein_A` in the fasta file will yield `protein_A.pkl`). Note that special symbols such as ```| : ; #```, after ```>``` will be replaced with ```_```.

Go to the next step [2.1. Basic run](#2-predict-structures-gpu-stage). For example run please use the following files:

<details>
   
<summary><b>
Example
</b></summary>


</details>
Go to the next step [2.1. Basic run](#2-predict-structures-gpu-stage).

### 1.2. FLAGS

Features calculation script ```create_individual_features.py``` has several optional FLAGS:
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
   
   <summary>
   Flags related to TrueMultimer mode:
   </summary>

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
MMseq2 is another method for homologs search and MSA generation. It offers an alternative to the default HMMer and HHblits used by AlphaFold. The results of these different approaches might lead to slightly different protein structure predictions due to the variations in the captured evolutionary information within the MSAs. AlphaPulldown supports the implementation of MMseq2 search made by ColabFold, which also provides a web server for MSA generation, so no local installation of databases is needed.
>If you used mmseqs2 please remember to cite: 
Mirdita M, Schütze K, Moriwaki Y, Heo L, Ovchinnikov S and Steinegger M. ColabFold: Making protein folding accessible to all.
Nature Methods (2022) doi: 10.1038/s41592-022-01488-1

#### Run MMseqs2 remotely 

>[!Caution]
>To avoid overloading the remote server, do not submit a large number of jobs at the same time. If you want to calculate MSAs for many sequences, please use  [mmseqs2 locally](#run-mmseqs2-locally)

Same as for [1.1 Basic](#11-basic-run) run to run `create_individual_features.py` just add `--use_mmseqs2=True` FALG:
```bash
source activate AlphaPulldown
create_individual_features.py \
  --fasta_paths=example_1_sequences.fasta \
  --data_dir=<path to alphafold databases> \
  --output_dir=<dir to save the output objects> \ 
  --use_mmseqs2=True \
  --max_template_date=<any date you want, format like: 2050-01-01> \ 

```

After the script run is finished, your output_dir will look like this:
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
Go to the next step [2.1. Basic run](#2-predict-structures-gpu-stage)

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
Go to the next step [2.1. Basic run](#2-predict-structures-gpu-stage)

### 1.4 Run with custom templates (TrueMultimer)
Instead of using the default search through the PDB database for structural templates, you can provide a custom database. AlphaPulldown supports a feature called "True Multimer," which allows AlphaFold to use multi-chain structural templates during the prediction process. This can be beneficial for protein complexes where the arrangement of the chains may vary. True Multimer mode will arrange different complex subunits as in the template.  

1. **Prepare a FASTA File:** Create a FASTA file containing all protein sequences that will be used for predictions as outlined in [1.1 Basic run](#11-basic-run).
   ${\color{red} remove\ all\ special\ symbols \from \fasta}$
3. **Create a Template Directory:** Designate a folder (e.g., "templates") to store your custom template files in PDB or CIF format.
4. **Create a description file:** This `description.csv` file links protein sequences to templates:

```
>protein_A,TMPL.cif,A
>protein_B,TMPL.cif,B
```

   * **Column 1** (>protein_A): Must exactly match protein descriptions from your FASTA file. 
   * **Column 2** (TMPL.cif): The filename of your template structure in PDB or CIF format.
   * **Column 3** (A): The chain ID within the template that the query sequence corresponds to.
     
**For Multiple Templates:**  If you want to provide multiple templates for a single protein, add additional rows with the same protein name but different templates and chain IDs:
```
>protein_A,TMPL.cif,A
>protein_A,TMP2.cif,B
>protein_B,TMPL.cif,B
```

>[!Note]
>Your template will be renamed to a PDB code taken from *_entry_id*. If you use a *.pdb file instead of *.cif, AlphaPulldown will first try to parse the PDB code from the file. Then it will check if the filename is 4-letter long. If it is not, it will generate a random 4-letter code and use it as the PDB code.

Now run:

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
Output: Pickle format features for each protein in the `description.csv` file stored in the ```output_dir```. 
${\color{red}Add\ True\ Multimer\ limitations}$ 

Go to the next step [2.X. Template run](#2-predict-structures-gpu-stage) ${\color{red}Correct}$ 

For additional Flags of TrueMultimer mode run refer to [FLAGS](#12-flags)

### 1.5 Older versions
If you are updating from previous versions of AlphaPulldown, and the local databases have not changed, there's no change to how features are generated. Input files and scripts from previous versions will work without modification in the current version.
${\color{red} Correct\ if\ there\ are\ any\ changes}$


## 2. Predict structures (GPU stage)
### 2.1 Basic run
This step requires the pickle files (.pkl) generated during the [first stage](#1-compute-multiple-sequence-alignment-msa-and-template-features-cpu-stage).
Additionally, you'll need to provide a list of protein combinations you intend to predict.

#### Protein Combinations File
Here's how to structure your combinations file `protein_list.txt`, with explanations:

**Prediction of monomers**:
  ```
  protein_A
  protein_B
  protein_C,1-100  
  ```
  * Each line is a separate prediction
  * Lines like `protein_A` will trigger a prediction of the entire sequence.
  * To predict specific residue ranges (e.g., the first 100 residues of protein_C), use the format "protein_C,1-100".

 **Prediction of complexes**:
   ```
   protein_A;protein_B;protein_C
   protein_B;protein_B 
   protein_B,4
   protein_C,2;protein_A
   protein_A,4,1-100;protein_B
   ```
   * Use semicolons (`;`) to separate protein names within a complex.
   * Instead of repeating the protein name for homooligomers, specify the number of copies after the protein's name (e.g., `protein_B,4` for a tetramer).
   * Combine residue ranges and homooligomer notation for specific predictions (e.g., `protein_A,4,1-100;protein_B`).

#### Running Structure Prediction
To predict structures, activate the AlphaPulldown environment and run the script `run_multimer_jobs.py` as follows:
 ```bash
 source activate AlphaPulldown
 ```
```bash
run_multimer_jobs.py \
  --mode=custom \
  --monomer_objects_dir=<dir that stores feature pickle files> \ 
  --protein_lists=<protein_list.txt> \
  --output_path=<path to output directory> \ 
  --num_cycle=<any number e.g. 3> 
```
$\textrm{\color{red}Do we need to specify data dir?}$
$\textrm{\color{red}Can we delete custom mode here?}$

Explanation of arguments:
* Instead of `<dir that stores feature pickle files>` provide the path to the directory containing the `.pkl` feature files generated in the previous step.
* Instead of `<protein_list.txt>` provide the path to a text file containing a list of protein combinations to be modeled.
* Instead of `<path to output directory>` provide the path where subdirectories containing the final structures will be saved.
* `--num_cycle` This flag specifies the number of times the AlphaFold neural network will run, using the output of one cycle as input for the next. Increasing this number may improve the quality of the final structures (especially for large complexes), but it will also increase the runtime.

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

### 2.2 FLAGS

Structures prediction script `run_multimer_jobs.py` has several several optional FLAGS:
$\text{\color{red}add FLAGS}$

### 2.3 Pulldown and All versus all modes
Instead of manually typing all combinations of proteins, AlphaPulldown provides two different modes of automatic generation of such combinations.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../manuals/AP_modes_dark.png">
  <source media="(prefers-color-scheme: light)" srcset="../manuals/AP_modes.png">
  <img alt="Shows an illustrated sun in light mode and a moon with stars in dark mode." src="../manuals/AP_modes.png">
</picture>

#### Multiple inputs "pulldown" mode

This mode allows to provide two or more lists of proteins that will generate all combinations of proteins from one list with all proteins from another list.
If you want to emulate _in silico_ pulldown of some hypothetical protein_A bait against proteins B-G you can use two `protein_list.csv` files:

The first `protein_list1.csv`:
```
protein_A
```

The second `protein_list2.csv`:
```
protein_B
protein_C
protein_D
protein_E
protein_F
protein_G
```

This results in the following combinations of proteins: A-B, A-C, A-D, A-E, A-F, A-G.

Can you add the third `protein_list3.csv`:
```
protein_X
protein_Z
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
protein_A
protein_B
protein_C
protein_D
protein_E
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

### 2.X Older version


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

## SnakeMake of AlphaPulldown
Alternatively, you can integrate AlphaPulldown with the Snakemake pipeline to execute all steps sequentially. For detailed installation and execution instructions, please refer to the [AlphaPulldownSnakemake](https://github.com/KosinskiLab/AlphaPulldownSnakemake) repository.
$\text{\color{red}Must cluster have SLURM to support the pipeline?}$. 

<br>

## Running with SLURM (EMBL cluster)
Computational clusters often use SLURM (Simple Linux Utility for Resource Management) to efficiently manage and schedule jobs. SLURM allows users to allocate resources and run jobs on HPC systems seamlessly; besides, it allows to run all jobs in parallel as a job array. The EMBL cluster utilizes SLURM, and to run AlphaPulldown on this cluster, you need to submit your job scripts through SLURM's scheduling system. This part of the manual will provide the necessary SLURM sbatch scripts to run AlphaPulldown. 
>[!NOTE]
>For more details about the SLURM system on the EMBL cluster, please refer to the [EMBL Cluster wiki](https://wiki.embl.de/cluster/Main_Page) using the EMBL network.

### 1.  Compute multiple sequence alignment (MSA) and template features (CPU stage)

Create the ```create_individual_features_SLURM.sh``` bash file using vi, nano, or any other text editor and place the following code in it. Don't forget to change the input of `create_individual_features.py` script as described [previously in manual](#1-compute-multiple-sequence-alignment-msa-and-template-features-cpu-stage):

```bash
#!/bin/bash

#A typical run takes couple of hours but may be much longer
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
  --fasta_paths=<sequences.fasta> \
  --data_dir=/scratch/AlphaFold_DBs/2.3.2/ \
  --output_dir=<dir to save the output objects> \ 
  --max_template_date=<any date you want, format like: 2050-01-01> \
  --skip_existing \
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


### 2. Predict structures (GPU stage)

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


### 3. Analysis and Visualization
#### Jupyter Notebook remote access 
To create a Jupyter Notebook, follow the instructions provided [previously](#jupyter-notebook). 

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

#### Results table
To create a results table, please refer to the relevant [section of the manual](#results-table).

<br>

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
