from sacred import Experiment
from sacred import Ingredient
import os
import sys
sys.path.insert(0, os.getcwd() + "/wave_u_net")
sys.path.insert(0, os.getcwd() + "/montreal")

from wave_u_net.Config import config_ingredient
from wave_u_net import Evaluate
import wave_u_net

import hmm_vad
import energy_vad

from montreal.aligner.command_line import align
import argparse

from praatio import tgio

import numpy as np
import shutil
import soundfile as sf
import librosa

def extract_vocals(input_path, output_path=None):
    cfg = wave_u_net.Config.cfg()
    cfg["model_config"].update(wave_u_net.Config.full_44KHz()["model_config"])
    model_config = cfg["model_config"]
    model_path = os.path.join("wave_u_net/checkpoints", "full_44KHz", "full_44KHz-236118") # Load stereo vocal model by default
    Evaluate.produce_source_estimates(model_config, model_path, input_path, output_path)

def run_vad(input_path, output_path=None):
    if output_path is None:
        output_path = input_path
    align.fix_path()
    energy_vad.run_vad(input_path, output_path)
    align.unfix_path()
    return hmm_vad.run_vad(output_path, output_path, 3)

def run_alignment(input_path, output_path):
    args = argparse.Namespace(corpus_directory=input_path,
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

def parse_textgrid(input_path, segments):
    tg = tgio.openTextgrid(input_path)
    res = []
    if segments is None:
        for i in tg.tierDict["words"].entryList:
            res.append((i.label, i.start))
        return res
    seg_num = 0
    time_offset = segments[0][0]
    for i in tg.tierDict["words"].entryList:
        t = i.start
        cur_seg = segments[seg_num]
        end_time = cur_seg[0] + cur_seg[1]
        if t + time_offset > end_time:
            seg_num += 1
            time_offset += segments[seg_num][0] - end_time
        res.append((i.label, t + time_offset))
    return res

def align_lyrics(audio_path, lyrics_path):
    tmpdir = 'tmp'
    if not os.path.exists(tmpdir):
        os.makedirs(tmpdir)
    extract_vocals(audio_path, tmpdir)
    orig_name = os.path.basename(audio_path)
    out = os.path.join(tmpdir, orig_name + "_vocals.wav")
    aud, sr = librosa.core.load(out, sr=None)
    aud = librosa.core.resample(aud, sr, 48000)
    librosa.output.write_wav(out, aud, sr=48000)
    aud, sr = sf.read(out)
    maxv = np.iinfo(np.int16).max
    sf.write(out, (aud * maxv).astype(np.int16), 48000, subtype='PCM_16')
    vad_out = os.path.join(tmpdir, orig_name + "_vad.wav")
    segments = run_vad(out, vad_out)
    lyrics_file = os.path.splitext(vad_out)[0] + '.lab'
    shutil.copyfile(lyrics_path, lyrics_file)
    run_alignment(tmpdir, os.path.join(tmpdir, 'out'))
    result = parse_textgrid(os.path.join(tmpdir, 'out', os.path.splitext(os.path.basename(vad_out))[0] + ".TextGrid"), segments)
    print(segments)
    print(result)
    return result

if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--audio_path', type=str, required=True)
    parser.add_argument('--lyrics_path', type=str, required=True)
    args = parser.parse_args(sys.argv[1:])
    align_lyrics(args.audio_path, args.lyrics_path)
