from sacred import Experiment
from sacred import Ingredient
import os
import sys
sys.path.insert(0, os.getcwd() + "/wave_u_net")
sys.path.insert(0, os.getcwd() + "/montreal")

from wave_u_net.Config import config_ingredient
from wave_u_net import Evaluate
import wave_u_net

from hmm_vad import run_vad

from montreal.aligner.command_line import align
from argparse import Namespace

def extract_vocals(input_path, output_path=None):
    cfg = wave_u_net.Config.cfg()
    cfg["model_config"].update(wave_u_net.Config.full_44KHz()["model_config"])
    model_config = cfg["model_config"]
    model_path = os.path.join("wave_u_net/checkpoints", "full_44KHz", "full_44KHz-236118") # Load stereo vocal model by default
    Evaluate.produce_source_estimates(model_config, model_path, input_path, output_path)

def run_vad(input_path, output_path=None):
    if output_path is None:
        output_path = input_path
    run_vad(input_path, output_path, 3)

def run_alignment(input_path, output_path):
    args = Namespace(corpus_directory=input_path,
                     dictionary_path="lang/librispeech-lexicon.txt",
                     acoustic_model_path="lang/english.zip",
                     output_directory=output_path,
                     speaker_characters=0,
                     temp_directory="",
                     num_jobs=20,
                     verbose=True,
                     clean=True,
                     debug=True,
                     config_path="align.yaml"
                    )
    args.output_directory = args.output_directory.rstrip('/').rstrip('\\')
    args.corpus_directory = args.corpus_directory.rstrip('/').rstrip('\\')
    align.fix_path()
    align.validate_args(args)
    align.unfix_path()

run_alignment("../corpus", "../output")
