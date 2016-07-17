from subprocess import call
import sys
import numpy as np

from lib.textgrid import IntervalTier, Interval
from lib.textgrid import TextGrid

__author__ = 'yossiadi'


# ---------------------- GENERAL ---------------------- #
def easy_call(command, debug_mode=False):
    try:
        # command = "time " + command
        if debug_mode:
            print >> sys.stderr, command
        call(command, shell=True)
    except Exception as exception:
        print "Error: could not execute the following"
        print ">>", command
        print type(exception)  # the exception instance
        print exception.args  # arguments stored in .args
        exit(-1)


# ---------------------- WAV FILES ---------------------- #
def crop_wav(wav_path, start_trim, end_trim, output_path):
    duration = end_trim - start_trim
    cmd = 'sbin/sox %s %s trim %s %s' % (wav_path, output_path, str(start_trim), str(duration))
    easy_call(cmd)


# get the length of the wav file
def get_wav_file_length(wav_file):
    import wave
    import contextlib
    with contextlib.closing(wave.open(wav_file, 'r')) as f:
        frames = f.getnframes()
        rate = f.getframerate()
        duration = frames / float(rate)
        return duration


def normalize_to_prob(y):
    y_norm = np.copy(y)
    for i in range(len(y)):
        total = 0.0
        for j in range(len(y[i])):
            total += y[i][j]
            y_norm[i][j] = np.exp(y[i][j]) / np.sum(np.exp(y[i][j]))
    return y_norm


def concatenate_x_frames(x, y, num_of_frames, is_y=True):
    """
    Concatenate n frames before and after the current frame
    :param x: The features
    :param y: The labels
    :param num_of_frames: The number pf frames to concatenate
    :param is_y:
    :return: The new features and labels
    """
    if is_y:
        items_x = list()
        items_y = list()

        for item in range(len(x)):
            x_concat = []
            for i in range(num_of_frames, len(x[item]) - num_of_frames):
                tmp_x = None
                is_first = True
                # before the current frame
                for j in range(num_of_frames):
                    tmp_x = np.concatenate((tmp_x, x[item][i - num_of_frames + j].T)) if not is_first else x[item][
                        i - num_of_frames + j]
                    is_first = False
                tmp_x = np.concatenate((tmp_x, x[item][i].T))
                # after the current frame
                for j in range(num_of_frames):
                    tmp_x = np.concatenate((tmp_x, x[item][i + j + 1].T))
                x_concat.append(tmp_x)
            items_y.append(y[item][num_of_frames:len(x[item]) - num_of_frames])
            items_x.append(x_concat)
        return np.array(items_x), np.array(items_y)
    else:
        items_x = list()
        for item in range(len(x)):
            x_concat = []
            for i in range(num_of_frames, len(x[item]) - num_of_frames):
                tmp_x = None
                is_first = True
                # before the current frame
                for j in range(num_of_frames):
                    tmp_x = np.concatenate((tmp_x, x[item][i - num_of_frames + j].T)) if not is_first else x[item][
                        i - num_of_frames + j]
                    is_first = False
                tmp_x = np.concatenate((tmp_x, x[item][i].T))
                # after the current frame
                for j in range(num_of_frames):
                    tmp_x = np.concatenate((tmp_x, x[item][i + j + 1].T))
                x_concat.append(tmp_x)
            items_x.append(x_concat)
        return np.array(items_x)


# ---------------------- TEXT-GRIDS ---------------------- #
def create_text_grid(text_grid_path, label, num_of_frames):
    """
    create TextGrid files from the labels_path file
    :param num_of_frames:
    :param label:
    :param text_grid_path:
    """

    # should be different for every file format
    FRAME_RATE = 10
    MILLISEC_2_SEC = 0.001
    FRAME_CONCAT_ONSET = 0
    FRAME_CONCAT_OFFSET = 0
    v_onset = (label[0] + FRAME_CONCAT_ONSET)
    v_offset = (label[1] + FRAME_CONCAT_OFFSET)
    length = num_of_frames * FRAME_RATE * MILLISEC_2_SEC

    # build TextGrid
    text_grid = TextGrid()
    vowels_tier = IntervalTier(name='Duration', minTime=0.0, maxTime=float(length))
    vowels_tier.addInterval(Interval(0, float(v_onset) * FRAME_RATE * MILLISEC_2_SEC, ""))
    vowels_tier.addInterval(
            Interval(float(v_onset) * FRAME_RATE * MILLISEC_2_SEC, float(v_offset) * FRAME_RATE * MILLISEC_2_SEC, ""))
    vowels_tier.addInterval(Interval(float(v_offset) * FRAME_RATE * MILLISEC_2_SEC, float(length), ""))

    text_grid.append(vowels_tier)
    text_grid.write(text_grid_path)