import cv2
import zlib
import subprocess
import argparse
import os
import json
from tqdm import tqdm

parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Guitar1',
                    help="root path for a single data collection trial")
parser.add_argument('--sync_dir', type=str, default='outputs/synchronization',
                    help="path for sync folder")
parser.add_argument('--save_dir', type=str, default='outputs/video_clips',
                    help="path for sync folder")
args = parser.parse_args()


def trim_video_with_ffmpeg(inputFile, startTime_video_sec, duration_sec, outputFile):
    cmd = "ffmpeg -i {} -ss {} -t {} -c copy {}".format(inputFile, startTime_video_sec, duration_sec, outputFile)
    print("Running cmd: {}".format(cmd))
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":

    print('Synchronization images for {}'.format(args.path))
    # time range for reference video
    # TODO: get separator time from QR code
    reference_time_video_id = 0
    # seperator_ms = [((2*60) + 50)*1000, ((7*60) + 30)*1000, ((8*60) + 40)*1000] # 2:50, 7:30, 8:40 for Piano
    seperator_ms = [((3*60) + 19)*1000, ((8*60) + 2)*1000] # 3:19, 8:20 for Guitar1

    sync_file = os.path.join(args.path, args.sync_dir, 'sync.json')
    assert os.path.exists(sync_file), sync_file

    with open(sync_file) as file:
        T_qr_video_list = json.load(file)
    input_video_path_list = [key for key in T_qr_video_list.keys()]

    for idx in range(len(seperator_ms)-1):

        startTime_refvideo_ms = seperator_ms[idx]
        endTime_refvideo_ms = seperator_ms[idx+1]

        # get reference qr timestamp in ms
        startTime_qr_reftime_ms = T_qr_video_list[input_video_path_list[reference_time_video_id]] + startTime_refvideo_ms
        endTime_qr_reftime_ms = T_qr_video_list[input_video_path_list[reference_time_video_id]] + endTime_refvideo_ms

        for inputFile in input_video_path_list:

            T_qr_video = T_qr_video_list[inputFile]

            startTime_thisVideo_ms = startTime_qr_reftime_ms - T_qr_video
            endTime_thisVideo_ms = endTime_qr_reftime_ms - T_qr_video

            duration_ms = endTime_thisVideo_ms - startTime_thisVideo_ms
            startTime_thisVideo_sec = startTime_thisVideo_ms / 1000.0
            endTime_thisVideo_sec = endTime_thisVideo_ms / 1000.0
            duration_sec = duration_ms / 1000.0
            if duration_sec < 0:
                print("WARNING: wrong duration_sec {}".format(duration_sec))
                break
            # crop the video
            sub = os.path.basename(os.path.dirname(inputFile))
            sub_dir = os.path.join(args.path, args.save_dir, sub)
            os.makedirs(sub_dir, exist_ok=True)
            outputFile = os.path.join(sub_dir, "cropId_{:03d}.MP4".format(idx))
            trim_video_with_ffmpeg(inputFile, startTime_thisVideo_sec, duration_sec, outputFile)