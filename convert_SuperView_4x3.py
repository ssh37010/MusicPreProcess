import argparse
import os

parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Guitar1',
                    help="root path for a single data collection trial")
parser.add_argument('--calib_dir', type=str, default='/media/shan/Volume1/Data/Music/calib_files',
                    help="folder for calibration files")
parser.add_argument('--ego_name', type=str, default='gp05',
                    help="ego camera name")
args = parser.parse_args()

if __name__ == "__main__":

    print('Prepocessing SuperView videos for {}'.format(args.path))

    ego_dir = os.path.join(args.path, 'Ego', 'gp05')
    assert os.path.exists(ego_dir), ego_dir

    ego_videos = sorted(os.listdir(ego_dir))
    ego_videos = [video for video in ego_videos if video[:4]!='proc']
    for video in ego_videos:
        video_path = os.path.join(ego_dir, video)
        save_path = os.path.join(ego_dir, 'proc_'+video)
        print('\t video {} -> {}'.format(video_path, save_path))
        cmd = 'ffmpeg -i {} -i {}/xmap.pgm -i {}/ymap.pgm -lavfi remap {}'.format(
              video_path, args.calib_dir, args.calib_dir, save_path)
        os.system(cmd)


