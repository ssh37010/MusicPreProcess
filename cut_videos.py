import cv2
import zlib
import subprocess
import argparse
import os
import json
from tqdm import tqdm

parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/0217_Violin',
                    help="root path for a single data collection trial")
parser.add_argument('--sync_dir', type=str, default='outputs/synchronization',
                    help="path for sync folder")
parser.add_argument('--timestamp_file', type=str, default='Ego/gp05/timestamps.json',
                    help="path for timestamp file")
parser.add_argument('--ego_dir', type=str, default='Ego/gp05',
                    help="path for ego camera folder")
parser.add_argument('--width', type=int, default=1920,
                    help="width for merged video")
parser.add_argument('--height', type=int, default=1080,
                    help="height for merged video")
parser.add_argument('--save_dir', type=str, default='outputs/video_clips',
                    help="path for sync folder")
args = parser.parse_args()


def trim_video_with_ffmpeg(inputFile, startTime_video_sec, duration_sec, outputFile):
    cmd = "ffmpeg -i {} -ss {} -t {} -c copy {}".format(inputFile, startTime_video_sec, duration_sec, outputFile)
    print("Running cmd: {}".format(cmd))
    subprocess.run(cmd, shell=True)


if __name__ == "__main__":

    print('Synchronization images for {}'.format(args.path))
    reference_time_video_id = 0 # use ego camera as reference camera
    # seperator_ms = [((2 * 60) + 45) * 1000, ((5 * 60) + 15) * 1000]  # demo time

    sync_file = os.path.join(args.path, args.sync_dir, 'sync.json')
    assert os.path.exists(sync_file), sync_file

    timestamp_file = os.path.join(args.path, args.timestamp_file)
    assert os.path.exists(timestamp_file), timestamp_file

    with open(sync_file) as file:
        T_qr_video_list = json.load(file)
    input_video_path_list = [key for key in T_qr_video_list.keys()]

    with open(timestamp_file) as file:
        timestamps = json.load(file)

    # # merge all videos
    # for prefix in ['Ego', 'Exo']:
    #     prefix_dir = os.path.join(args.path, prefix)
    #     cam = sorted(os.listdir(prefix_dir))
    #     cam = [c for c in cam if c[:2]=='gp']
    #     for sub in cam:
    #         video_dir = os.path.join(prefix_dir, sub)
    #         video_list = sorted(os.listdir(video_dir))
    #         video_list = [video for video in video_list if video[-3:]=='MP4']
    #         file_list = ['file '+os.path.join(video_dir, video)+'\n' for video in video_list]
    #         with open(os.path.join(video_dir, 'video_list.txt'), 'w') as file:
    #             file.writelines(file_list)
    #         cmd = 'ffmpeg -f concat -safe 0 -i {} -vf scale={}:{} {}/merged.MP4'.format(
    #             os.path.join(video_dir, 'video_list.txt'), args.width, args.height, video_dir)
    #         os.system(cmd)

    # get separator time for merged videos
    offset = 0
    timestamps_merged_ms = []
    for key in timestamps.keys():
        ts = [(t+offset)*1000 for t in timestamps[key]]
        timestamps_merged_ms = timestamps_merged_ms + ts
        video_path = os.path.join(args.path, args.ego_dir, key)
        cap = cv2.VideoCapture(video_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count - 1)
        offset = offset + float(cap.get(cv2.CAP_PROP_POS_MSEC))

    seperator_ms = timestamps_merged_ms
    assert len(seperator_ms) % 2 == 0, 'Problematic timestamps'
    nclips = int(len(seperator_ms)/2)

    for idx in range(nclips):

        startTime_refvideo_ms = seperator_ms[idx*2]
        endTime_refvideo_ms = seperator_ms[idx*2+1]

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
            trim_video_with_ffmpeg(os.path.join(os.path.dirname(inputFile), 'merged.MP4'), startTime_thisVideo_sec, duration_sec, outputFile)