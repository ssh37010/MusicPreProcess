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
parser.add_argument('--save_dir', type=str, default='outputs/synchronization',
                    help="path for save folder")
args = parser.parse_args()

def get_delta_timestamp_from_qrcode(input_video_path):
    cap = cv2.VideoCapture(input_video_path)
    qr_detector = cv2.QRCodeDetector()

    # qr_timestamp = T_qr_video + video_timestamp
    T_qr_video = -1

    pbar = tqdm(total=10 * 60 * 1000)
    while(cap.isOpened()):
        frame_exist, frame = cap.read()
        if frame_exist:
            qr_val, _, _ = qr_detector.detectAndDecode(frame)
            video_timestamp_ms = float(cap.get(cv2.CAP_PROP_POS_MSEC))
            pbar.update(16.66)
            # print(video_timestamp_ms)
            if len(qr_val) > 0:
                vals = qr_val.split("-")
                if vals[1] == str(zlib.adler32(vals[0].encode('ascii'))):
                    qr_timestamp_ms = float(vals[0])
                    T_qr_video = qr_timestamp_ms - video_timestamp_ms
                    break

        else:
            break

    cap.release()
    return T_qr_video

if __name__ == "__main__":

    print('Synchronization images for {}'.format(args.path))

    input_video_path_list = []
    ego_dir = os.path.join(args.path, 'Ego')
    ego_subs = sorted(os.listdir(ego_dir))
    for sub in ego_subs:
        files = sorted(os.listdir(os.path.join(ego_dir, sub)))
        files = [file for file in files if file.endswith('.MP4') and file[:4]=='proc']
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
    # T_qr_video_list['/media/shan/Volume1/Data/Music/SessionDate200123_Piano/Exo/gp04/cam004_1.MP4'] = 1674257014254.0667
    # T_qr_video_list['/media/shan/Volume1/Data/Music/SessionDate200123_Piano/Exo/gp03/cam003_1.MP4'] = 1674257031450.2
    # T_qr_video_list['/media/shan/Volume1/Data/Music/SessionDate200123_Piano/Exo/gp02/cam002_1.MP4'] = 1674257034205.6667
    # T_qr_video_list['/media/shan/Volume1/Data/Music/SessionDate200123_Piano/Exo/gp01/cam001_1.MP4'] = 1674257021016.4167
    for video_path in input_video_path_list:
        T_qr_video = get_delta_timestamp_from_qrcode(video_path)
        print("Got time offset {} for video {}".format(T_qr_video, video_path))

        assert T_qr_video != -1, 'No QR code detected for {}. Synchronization failed'
        T_qr_video_list[video_path] = T_qr_video

    os.makedirs(os.path.join(args.path, args.save_dir), exist_ok=True)
    save_file = os.path.join(args.path, args.save_dir, 'sync.json')
    with open(save_file, 'w') as file:
        json.dump(T_qr_video_list, file, indent=4)






