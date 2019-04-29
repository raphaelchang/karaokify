import bob.io.audio
import bob.kaldi
import numpy as np
import soundfile as sf

def compute(sig, sr, vad_energy_mean_scale=0.5, vad_energy_th=10, vad_frames_context=100, vad_proportion_th=0.5):
    """ Energy Based Voice Activate Detection algorithm. (based on kaldi)
        Param:
            sig: list or np.array
                the signal, list of samples
            sr: int
                sample rate
            vad_energy_mean_scale: :obj:`float`, optional
                If this is set to s, to get the actual threshold we let m be the mean
                log-energy of the file, and use s*m + vad-energy-th
            vad_energy_th: :obj:`float`, optional
                Constant term in energy threshold for MFCC0 for VAD.
            vad_frames_context: :obj:`int`, optional
                Number of frames of context on each side of central frame,
                in window for which energy is monitored 
            vad_proportion_th: :obj:`float`, optional
                Parameter controlling the proportion of frames within the window that
                need to have more energy than the threshold
    """
    sig = sig.copy()

    VAD_labels = bob.kaldi.compute_vad(sig, sr, 
                                       vad_energy_mean_scale=vad_energy_mean_scale,
                                       vad_energy_th=vad_energy_th, 
                                       vad_frames_context=vad_frames_context, 
                                       vad_proportion_th=vad_proportion_th)
    
    def get_section(arr):
        cur_i = 0
        while(True):
            while(cur_i < len(arr) and arr[cur_i] < 0.5):
                cur_i += 1
            if cur_i >= len(arr):
                break

            left_i = cur_i
            while (cur_i < len(arr) and arr[cur_i] > 0.5):
                cur_i += 1
                
            yield left_i, cur_i
            cur_i += 1

    VAD_WINDOW_SHIFT = 0.010
    ret = []
    for session in get_section(VAD_labels):
        ret.append([int(session[0]*sr*VAD_WINDOW_SHIFT), int(session[1]*sr*VAD_WINDOW_SHIFT)])
    return ret

def run_vad(input_path, output_path, vad_energy_mean_scale=0.5, vad_energy_th=10, vad_frames_context=100, vad_proportion_th=0.5):
    data = bob.io.audio.reader(input_path)
    sig, sr = data.load()[0], data.rate
    vad_result = compute(sig, sr, vad_energy_mean_scale, vad_energy_th, vad_frames_context, vad_proportion_th)
    sig_new = np.zeros_like(sig)
    for s in vad_result:
        sig_new[s[0]:s[1]] = sig[s[0]:s[1]]
    maxv = np.iinfo(np.int16).max
    sf.write(output_path, (sig_new * maxv).astype(np.int16), int(sr), subtype='PCM_16')
