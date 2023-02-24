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
parser.add_argument('--ego_start_sec', type=int, default=30,
                    help="The estimated time in sec when the sync QR code is captured for ego camera "
                         "(must be earlier than the actual time). Can speed up the performance. ")
parser.add_argument('--exo_start_sec', type=int, default=30,
                    help="The estimated time in sec when the sync QR code is captured for exo camera "
                         "(must be earlier than the actual time). Can speed up the performance. ")
parser.add_argument('--save_dir', type=str, default='outputs/synchronization',
                    help="path for save folder")
args = parser.parse_args()

def get_delta_timestamp_from_qrcode(input_video_path, start_sec):
    print('\t {}'.format(input_video_path))
    cap = cv2.VideoCapture(input_video_path)
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_sec*cap.get(cv2.CAP_PROP_FPS) - 1)

    qr_detector = cv2.QRCodeDetector()

    # qr_timestamp = T_qr_video + video_timestamp
    T_qr_video = -1

    pbar = tqdm(total=10 * 60 * 1000)
    pbar.update(start_sec * 1000)
    while(cap.isOpened()):
        frame_exist, frame = cap.read()
        if frame_exist:
            try:
                qr_val, _, _ = qr_detector.detectAndDecode(frame)
            except:
                print('Invalid QR code')
            video_timestamp_ms = float(cap.get(cv2.CAP_PROP_POS_MSEC))
            pbar.update(16.6)
            # print(video_timestamp_ms)
            if len(qr_val) > 0:
                vals = qr_val.split("-")
                if vals[1] == str(zlib.adler32(vals[0].encode('ascii'))):
                    qr_timestamp_ms = float(vals[0]) * 1000 /29 # new synchronization video with 29fps
                    T_qr_video = qr_timestamp_ms - video_timestamp_ms
                    # print(T_qr_video)
                    break

        else:
            break

    cap.release()
    return T_qr_video

if __name__ == "__main__":

    print('Synchronization videos for {}'.format(args.path))

    input_video_path_list = []
    ego_dir = os.path.join(args.path, 'Ego')
    ego_subs = sorted(os.listdir(ego_dir))
    for sub in ego_subs:
        files = sorted(os.listdir(os.path.join(ego_dir, sub)))
        # files = [file for file in files if file.endswith('.MP4') and file[:4]=='proc'] # for SuperView
        files = [file for file in files if file.endswith('.MP4')] # for SuperView
        assert len(files)>0, sub
        input_video_path_list.append(os.path.join(ego_dir, sub, files[0]))

    exo_dir = os.path.join(args.path, 'Exo')
    exo_subs = sorted(os.listdir(exo_dir))
    exo_subs = [sub for sub in exo_subs if sub!='mobile']
    for sub in exo_subs:
        files = sorted(os.listdir(os.path.join(exo_dir, sub)))
        files = [file for file in files if file.endswith('.MP4')]
        assert len(files)>0, sub
        input_video_path_list.append(os.path.join(exo_dir, sub, files[0]))


    T_qr_video_list = {}
    for video_path in input_video_path_list:
        T_qr_video = get_delta_timestamp_from_qrcode(video_path, min(args.ego_start_sec, args.exo_start_sec))
        print("\t Got time offset {}".format(T_qr_video))

        assert T_qr_video != -1, 'No QR code detected for {}. Synchronization failed'
        T_qr_video_list[video_path] = T_qr_video

    os.makedirs(os.path.join(args.path, args.save_dir), exist_ok=True)
    save_file = os.path.join(args.path, args.save_dir, 'sync.json')
    with open(save_file, 'w') as file:
        json.dump(T_qr_video_list, file, indent=4)






