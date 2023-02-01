import argparse
import os

parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Guitar1',
                    help="root path for a single data collection trial")

parser.add_argument('--decode_mobile', type=bool, default=False,
                    help="if decode mobile folder")
parser.add_argument('--decode_static_exo', type=bool, default=False,
                    help="if decode static exo folders")
parser.add_argument('--decode_ego', type=bool, default=True,
                    help="if decode ego folders")

parser.add_argument('--ego_name', type=str, default='gp05',
                    help="ego camera name")

parser.add_argument('--exo_width', type=int, default=1920,
                    help="width for decoded exo images")
parser.add_argument('--exo_height', type=int, default=1080,
                    help="width for decoded exo images")
parser.add_argument('--ego_width', type=int, default=1440,
                    help="width for decoded ego images")
parser.add_argument('--ego_height', type=int, default=1080,
                    help="width for decoded ego images")

parser.add_argument('--rate_mobile', type=int, default=10,
                    help="fps for decoding images for 3D environment reconstruction")
parser.add_argument('--rate_static_exo', type=float, default=1/6,
                    help="fps for decoding images for exo cameras registration")
parser.add_argument('--rate_ego', type=float, default=10,
                    help="fps for decoding images for ego cameras registration")
args = parser.parse_args()


if __name__ == "__main__":

    print('Extracting images for {}'.format(args.path))

    if args.decode_mobile:
        print('\t Decoding calibration videos to images')
        # decode images for building 3D environment
        mobile_dir = os.path.join(args.path, 'Exo', 'mobile')
        assert os.path.exists(mobile_dir), mobile_dir
        mobile_file = sorted(os.listdir(mobile_dir))
        mobile_file = [file for file in mobile_file if file[-3:] == 'MP4']
        assert len(mobile_file) == 1, 'fail to find the calibration file (must be one file)'
        mobile_path = os.path.join(mobile_dir, mobile_file[0])
        image_dir = os.path.join(mobile_dir, 'calib_images')
        os.makedirs(image_dir, exist_ok=True)
        cmd = 'ffmpeg -i {} -vf scale={}:{} -r {} {}/%06d.png'.format(
            mobile_path, args.exo_width, args.exo_height, args.rate_mobile, image_dir
        )
        os.system(cmd)

    # decode images for registering static exo cameras
    if args.decode_static_exo:
        print('\t Decoding images for exo cameras calibration')
        exo_dir = os.path.join(args.path, 'Exo')
        subs = sorted(os.listdir(exo_dir))
        subs = [sub for sub in subs if sub != 'mobile']
        for sub in subs:
            print('\t\t Decoding {}'.format(sub))
            sub_dir = os.path.join(exo_dir, sub)
            videos = sorted(os.listdir(sub_dir))
            videos = [video for video in videos if video[-3:] == 'MP4']
            assert len(videos) > 0, 'missing videos file for {}'.format(sub)
            video_path = os.path.join(sub_dir, videos[0])
            sub_image_dir = os.path.join(sub_dir, 'calib_images')
            os.makedirs(sub_image_dir, exist_ok=True)
            cmd = 'ffmpeg -i {} -vf scale={}:{} -r {} {}/{}_%06d.png'.format(
            video_path, args.exo_width, args.exo_height, args.rate_static_exo, sub_image_dir, sub
            )
            os.system(cmd)

    # extract ego videos for camera registeration
    if args.decode_ego:
        print('\t Decoding images for ego camera calibration')
        ego_dir = os.path.join(args.path, 'outputs', 'video_clips', args.ego_name)
        assert os.path.exists(ego_dir), ego_dir
        ego_files = sorted(os.listdir(ego_dir))

        save_dir = os.path.join(ego_dir, 'images')
        os.makedirs(save_dir, exist_ok=True)
        for ego_file in ego_files:
            video_path = os.path.join(ego_dir, ego_file)
            cmd = 'ffmpeg -i {} -vf scale={}:{} -r {} {}/{}_%06d.png'.format(
            video_path, args.ego_width, args.ego_height, args.rate_ego, save_dir, ego_file[:-4]
            )
            os.system(cmd)
