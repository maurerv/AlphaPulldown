#!/usr/bin/env python3

# Author Dingquan Yu
# This script is just to create msa and structural features for each sequences and store them in pickle
#

from alphapulldown.objects import MonomericObject
from alphapulldown.utils import parse_fasta, save_meta_data, create_uniprot_runner
from alphapulldown.create_fake_template_db import create_db
import alphafold
from alphafold.data.pipeline import DataPipeline
from alphafold.data.tools import hmmsearch
from alphafold.data import templates
from colabfold.utils import DEFAULT_API_SERVER
from absl import logging, app
import importlib
import os
import pickle
import sys
import contextlib
from datetime import datetime
from pathlib import Path
from colabfold.utils import DEFAULT_API_SERVER
import tempfile
import csv

@contextlib.contextmanager
def output_meta_file(file_path):
    """function that create temp file"""
    with open(file_path, "w") as outfile:
        yield outfile.name


def load_module(file_name, module_name):
    spec = importlib.util.spec_from_file_location(module_name, file_name)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


PATH_TO_RUN_ALPHAFOLD = os.path.join(
    os.path.dirname(alphafold.__file__), "run_alphafold.py"
)

try:
    run_af = load_module(PATH_TO_RUN_ALPHAFOLD, "run_alphafold")
except FileNotFoundError:
    PATH_TO_RUN_ALPHAFOLD = os.path.join(
        os.path.dirname(os.path.dirname(alphafold.__file__)), "run_alphafold.py"
    )

    run_af = load_module(PATH_TO_RUN_ALPHAFOLD, "run_alphafold")


flags = run_af.flags
flags.DEFINE_bool("save_msa_files", False, "save msa output or not")
flags.DEFINE_bool(
    "skip_existing", False, "skip existing monomer feature pickles or not"
)
flags.DEFINE_integer(
    "job_index", None, "index of job in the description file, starting from 1"
)
flags.DEFINE_string(
    "new_uniclust_dir", None, "directory where new version of uniclust is stored"
)
flags.DEFINE_bool("use_mmseqs2",False,"Use mmseqs2 remotely or not. Default is False")

flags.DEFINE_string("description_file", None, "Path to the text file with descriptions")

flags.DEFINE_string("path_to_fasta", None, "Path to directory with fasta files")

flags.DEFINE_string("path_to_mmt", None, "Path to directory with multimeric template mmCIF files")

FLAGS = flags.FLAGS
MAX_TEMPLATE_HITS = 20

flags_dict = FLAGS.flag_values_dict()

def create_global_arguments(flags_dict, feat, temp_dir=None):
    global uniref90_database_path
    global mgnify_database_path
    global bfd_database_path
    global small_bfd_database_path
    global pdb_seqres_database_path
    global obsolete_pdbs_path
    global pdb70_database_path
    global use_small_bfd
    global uniref30_database_path
    global template_mmcif_dir
    fasta = Path(feat["fasta"]).stem
    templates, chains = feat["templates"], feat["chains"]
    # Path to the Uniref30 database for use by HHblits.
    if FLAGS.uniref30_database_path is None:
        uniref30_database_path = os.path.join(
            FLAGS.data_dir, "uniref30", "UniRef30_2021_03"
        )
    else:
        uniref30_database_path = FLAGS.uniref30_database_path
    flags_dict.update({"uniref30_database_path": uniref30_database_path})

    if FLAGS.uniref90_database_path is None:
        uniref90_database_path = os.path.join(
            FLAGS.data_dir, "uniref90", "uniref90.fasta"
        )
    else:
        uniref90_database_path = FLAGS.uniref90_database_path

    flags_dict.update({"uniref90_database_path": uniref90_database_path})

    # Path to the MGnify database for use by JackHMMER.
    if FLAGS.mgnify_database_path is None:
        mgnify_database_path = os.path.join(
            FLAGS.data_dir, "mgnify", "mgy_clusters_2022_05.fa"
        )
    else:
        mgnify_database_path = FLAGS.mgnify_database_path
    flags_dict.update({"mgnify_database_path": mgnify_database_path})

    # Path to the BFD database for use by HHblits.
    if FLAGS.bfd_database_path is None:
        bfd_database_path = os.path.join(
            FLAGS.data_dir,
            "bfd",
            "bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt",
        )
    else:
        bfd_database_path = FLAGS.bfd_database_path
    flags_dict.update({"bfd_database_path": bfd_database_path})

    # Path to the Small BFD database for use by JackHMMER.
    if FLAGS.small_bfd_database_path is None:
        small_bfd_database_path = os.path.join(
            FLAGS.data_dir, "small_bfd", "bfd-first_non_consensus_sequences.fasta"
        )
    else:
        small_bfd_database_path = FLAGS.small_bfd_database_path
    flags_dict.update({"small_bfd_database_path": small_bfd_database_path})

    if FLAGS.pdb_seqres_database_path is None:
        pdb_seqres_database_path = os.path.join(
            FLAGS.data_dir, "pdb_seqres", "pdb_seqres.txt"
        )
    else:
        pdb_seqres_database_path = FLAGS.pdb_seqres_database_path
    # Path to the Uniclust30 database for use by HHblits.
    # if FLAGS.uniclust30_database_path is None:
    #     uniclust30_database_path = os.path.join(
    #         FLAGS.data_dir, "uniclust30", "uniclust30_2018_08", "uniclust30_2018_08"
    #     )
    # else:
    #     uniclust30_database_path = FLAGS.uniclust30_database_path
    # flags_dict.update({"uniclust30_database_path": uniclust30_database_path})

    # Create fake template database
    #local_path_to_fake_template_db = Path(".") / "fake_template_db" / fasta
    local_path_to_fake_template_db = Path(temp_dir.name) / "fake_template_db" / fasta
    logging.info(f"Path to local database: {local_path_to_fake_template_db}")
    create_db(local_path_to_fake_template_db, templates, chains)
    pdb_seqres_database_path = os.path.join(local_path_to_fake_template_db, "pdb_seqres", "pdb_seqres.txt")
    template_mmcif_dir = os.path.join(local_path_to_fake_template_db, "pdb_mmcif", "mmcif_files")
    obsolete_pdbs_path = os.path.join(local_path_to_fake_template_db, "pdb_mmcif", "obsolete.dat")
    # Update flags_dict.
    flags_dict.update({"fasta_path": fasta})
    flags_dict.update({"multimeric_template": templates})
    flags_dict.update({"multimeric_chains": chains})
    flags_dict.update({"template_mmcif_dir": template_mmcif_dir})
    flags_dict.update({"obsolete_pdbs_path": obsolete_pdbs_path})

    # Path to pdb70 database
    if FLAGS.pdb70_database_path is None:
        pdb70_database_path = os.path.join(FLAGS.data_dir, "pdb70", "pdb70")
    else:
        pdb70_database_path = FLAGS.pdb70_database_path
    flags_dict.update({"pdb70_database_path": pdb70_database_path})

    use_small_bfd = FLAGS.db_preset == "reduced_dbs"


def create_pipeline():
    monomer_data_pipeline = DataPipeline(
        jackhmmer_binary_path=FLAGS.jackhmmer_binary_path,
        hhblits_binary_path=FLAGS.hhblits_binary_path,
        uniref90_database_path=uniref90_database_path,
        mgnify_database_path=mgnify_database_path,
        bfd_database_path=bfd_database_path,
        uniref30_database_path=uniref30_database_path,
        small_bfd_database_path=small_bfd_database_path,
        use_small_bfd=use_small_bfd,
        use_precomputed_msas=FLAGS.use_precomputed_msas,
        template_searcher=hmmsearch.Hmmsearch(
            binary_path=FLAGS.hmmsearch_binary_path,
            hmmbuild_binary_path=FLAGS.hmmbuild_binary_path,
            database_path=pdb_seqres_database_path,
        ),
        template_featurizer=templates.HmmsearchHitFeaturizer(
            mmcif_dir=template_mmcif_dir,
            max_template_date=FLAGS.max_template_date,
            max_hits=MAX_TEMPLATE_HITS,
            kalign_binary_path=FLAGS.kalign_binary_path,
            obsolete_pdbs_path=obsolete_pdbs_path,
            release_dates_path=None,
        ),
    )
    return monomer_data_pipeline


def check_existing_objects(output_dir, pickle_name):
    """check whether the wanted monomer object already exists in the output_dir"""
    return os.path.isfile(os.path.join(output_dir, pickle_name))


def create_and_save_monomer_objects(m, pipeline, flags_dict,use_mmseqs2=False):
    logging.info("You are using the new version")
    if FLAGS.skip_existing and check_existing_objects(
        FLAGS.output_dir, f"{m.description}.pkl"
    ):
        logging.info(f"Already found {m.description}.pkl in {FLAGS.output_dir} Skipped")
        pass
    else:
        metadata_output_path = os.path.join(
            FLAGS.output_dir,
            f"{m.description}_feature_metadata_{datetime.date(datetime.now())}.txt",
        )
        with output_meta_file(metadata_output_path) as meta_data_outfile:
            save_meta_data(flags_dict, meta_data_outfile)

        if not use_mmseqs2:
            m.make_features(
                pipeline,
                output_dir=FLAGS.output_dir,
                use_precomputed_msa=FLAGS.use_precomputed_msas,
                save_msa=FLAGS.save_msa_files,
            )
        else:
            logging.info("running mmseq now")
            m.make_mmseq_features(DEFAULT_API_SERVER=DEFAULT_API_SERVER,
            pdb70_database_path=pdb70_database_path,
            template_mmcif_dir=template_mmcif_dir,
            max_template_date=FLAGS.max_template_date,
            output_dir=FLAGS.output_dir,
            obsolete_pdbs_path=FLAGS.obsolete_pdbs_path
            )
        pickle.dump(m, open(f"{FLAGS.output_dir}/{m.description}.pkl", "wb"))
        del m


def iter_seqs(fasta_fns):
    for fasta_path in fasta_fns:
        with open(fasta_path, "r") as f:
            sequences, descriptions = parse_fasta(f.read())
            for seq, desc in zip(sequences, descriptions):
                yield seq, desc

def parse_txt_file(csv_path, fasta_dir, mmt_dir):
    """
    o csv_path: Path to the text file with descriptions
        features.csv: A coma-separated file with three columns: FASTA file, PDB file, chain ID.
    o fasta_dir: Path to directory with fasta files
    o mmt_dir: Path to directory with multimeric template mmCIF files

    Returns:
        a list of dictionaries with the following structure:
    [{"fasta": fasta_file, "templates": [pdb_files], "chains": [chain_id]}, ...]
    """
    parsed_dict = {}
    with open(csv_path, newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            # skip empty lines
            if not row:
                continue
            if len(row) == 3:
                fasta, template, chain = [item.strip() for item in row]
                if fasta not in parsed_dict:
                    parsed_dict[fasta] = {"fasta": os.path.join(fasta_dir, fasta), "templates": [], "chains": []}
                parsed_dict[fasta]["templates"].append(os.path.join(mmt_dir, template))
                parsed_dict[fasta]["chains"].append(chain)
            else:
                logging.error(f"Invalid line found in the file {csv_path}: {row}")
                exit(1)

    return list(parsed_dict.values())

def main(argv):
    try:
        Path(FLAGS.output_dir).mkdir(parents=True, exist_ok=True)
    except FileExistsError:
        logging.info("Multiple processes are trying to create the same folder now.")

    flags_dict = FLAGS.flag_values_dict()
    feats = parse_txt_file(FLAGS.description_file, FLAGS.path_to_fasta, FLAGS.path_to_mmt)
    for idx, feat in enumerate(feats, 1):
        temp_dir = tempfile.TemporaryDirectory() #for each fasta file, create a temp dir
        if (FLAGS.job_index is None) or (FLAGS.job_index == idx):
            if not os.path.isfile(feat["fasta"]):
                logging.error(f"Fasta file {feat['fasta']} does not exist. Please check your input file.")
                exit(1)
            for temp in feat["templates"]:
                if not os.path.isfile:
                    logging.error(f"Template file {temp} does not exist. Please check your input file.")
                    exit(1)
            logging.info(f"Processing {feat['fasta']}: templates: {feat['templates']} chains: {feat['chains']}")
            create_global_arguments(flags_dict, feat, temp_dir)

            if not FLAGS.use_mmseqs2:
                if not FLAGS.max_template_date:
                    logging.info("You have not provided a max_template_date. Please specify a date and run again.")
                    sys.exit()
                else:
                    pipeline = create_pipeline()
                    uniprot_database_path = os.path.join(FLAGS.data_dir, "uniprot/uniprot.fasta")
                    flags_dict.update({"uniprot_database_path": uniprot_database_path})
                    if os.path.isfile(uniprot_database_path):
                        uniprot_runner = create_uniprot_runner(
                            FLAGS.jackhmmer_binary_path, uniprot_database_path
                        )
                    else:
                        logging.info(
                            f"Failed to find uniprot.fasta under {uniprot_database_path}."
                            "Please make sure your data_dir has been configured correctly."
                        )
                        sys.exit()
            # If we are using mmseqs2, we don't need to create a pipeline
            else:
                pipeline=None
                uniprot_runner=None
                flags_dict=FLAGS.flag_values_dict()
            for curr_seq, curr_desc in iter_seqs([feat['fasta']]):
                if curr_desc and not curr_desc.isspace():
                    curr_monomer = MonomericObject(curr_desc, curr_seq)
                    curr_monomer.uniprot_runner = uniprot_runner
                    create_and_save_monomer_objects(curr_monomer, pipeline,
                    flags_dict, use_mmseqs2=FLAGS.use_mmseqs2)
        temp_dir.cleanup()


if __name__ == "__main__":
    flags.mark_flags_as_required(
        ["description_file", "path_to_fasta", "path_to_mmt", "output_dir", "max_template_date", "data_dir"]
    )
    app.run(main)
