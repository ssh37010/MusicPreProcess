import os
import argparse
import numpy as np
import json
import xml.etree.ElementTree as ET

parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Piano',
                    help="root path for a single data collection trial")
parser.add_argument('--calib_dir', type=str, default='/media/shan/Volume1/Data/Music/calib_files',
                    help="folder for calibration files")
parser.add_argument('--metashape_dir', type=str, default='outputs/Metashape',
                    help="folder for metashape results")
parser.add_argument('--save_dir', type=str, default='outputs/calib_results',
                    help="folder for results")
parser.add_argument('--prefix', type=str, default='ego',
                    help="ego or exo cameras")
parser.add_argument('--ego_name', type=str, default='gp05',
                    help="ego camera name")
parser.add_argument('--ego_video_dir', type=str, default='outputs/video_clips/gp05',
                    help="folder for ego video clips")
args = parser.parse_args()

if __name__ == "__main__":

    print('Prepocess data for {}'.format(args.path))

    if args.prefix == 'exo':

        exo_dir = os.path.join(args.path, 'Exo')
        exo_subs = sorted(os.listdir(exo_dir))
        exo_subs = [sub for sub in exo_subs if sub!='mobile']

        metashape_dir = os.path.join(args.path, args.metashape_dir)

        extri_data = {}
        for sub in exo_subs:
            im_name_filename = os.path.join(metashape_dir, '{}_{}_im_name.txt'.format(args.prefix, sub))
            assert os.path.exists(im_name_filename), im_name_filename
            cam_pose_filename = os.path.join(metashape_dir, '{}_{}_cam_pose.txt'.format(args.prefix, sub))
            assert os.path.exists(cam_pose_filename), cam_pose_filename

            with open(im_name_filename, 'r') as file:
                im_name = file.readlines()
            with open(cam_pose_filename, 'r') as file:
                cam_pose = file.readlines()
            assert len(im_name) == len(cam_pose), 'Wrong export data'

            idx = int(len(im_name)/2)
            param = np.array(cam_pose[idx].split('\t')[1:-1]).astype(float)
            param = np.reshape(param, (4,3)).T
            param = np.concatenate([param, [[0.0, 0.0, 0.0, 1.0]]], axis=0)
            extri_data[sub] = np.linalg.inv(param) # T_camera_world

        os.makedirs(os.path.join(args.path, args.save_dir), exist_ok=True)

        # write instrinsics
        dict_file = {'names': exo_subs}
        instri_file = os.path.join(args.calib_dir, 'exo_gp.xml')
        assert os.path.exists(instri_file), instri_file
        tree = ET.parse(instri_file)
        root = tree.getroot()
        for child in root:
            dict_file[child.tag] = child.text
        intri_file = os.path.join(args.path, args.save_dir, '{}_intri.json'.format(args.prefix))
        with open(intri_file, 'w') as file:
            json.dump(dict_file, file, indent=4)

        # write extrinsics
        extri_file = os.path.join(args.path, args.save_dir, '{}_extri.json'.format(args.prefix))
        dict_file = {'names': exo_subs}
        for sub in exo_subs:
            dict_file[sub] = {'T_camera_world':extri_data[sub].tolist()}
        with open(extri_file, 'w') as file:
            json.dump(dict_file, file, indent=4)


    if args.prefix == 'ego':

        ego_video_dir = os.path.join(args.path, args.ego_video_dir)
        assert os.path.exists(ego_video_dir), ego_video_dir
        ego_video_files = sorted(os.listdir(ego_video_dir))
        ego_video_files = [file for file in ego_video_files if file.endswith('MP4')]

        for video in ego_video_files:
            im_name_filelist = sorted(os.listdir(os.path.join(args.path, args.metashape_dir)))
            im_name_filelist = [file for file in im_name_filelist if file[4:-8]==video[:10]+'_im_name']
            cam_pose_filelist = sorted(os.listdir(os.path.join(args.path, args.metashape_dir)))
            cam_pose_filelist = [file for file in cam_pose_filelist if file[4:-8]==video[:10]+'_cam_pose']
            assert len(im_name_filelist) == len(cam_pose_filelist), 'wrong ego calibration output'

            extri_data = {}
            for batch_idx in range(len(im_name_filelist)):
                im_name_filename = os.path.join(args.path, args.metashape_dir, im_name_filelist[batch_idx])
                cam_pose_filename = os.path.join(args.path, args.metashape_dir, cam_pose_filelist[batch_idx])

                with open(im_name_filename, 'r') as file:
                    im_name = file.readlines()
                with open(cam_pose_filename, 'r') as file:
                    cam_pose = file.readlines()
                assert len(im_name) == len(cam_pose), 'Wrong export data'

                for idx in range(len(im_name)):
                    param = np.array(cam_pose[idx].split('\t')[1:-1]).astype(float)
                    param = np.reshape(param, (4, 3)).T
                    param = np.concatenate([param, [[0.0, 0.0, 0.0, 1.0]]], axis=0)
                    key = im_name[idx].split('\t')[-1][:-1]
                    extri_data[key] = np.linalg.inv(param)  # T_camera_world

            os.makedirs(os.path.join(args.path, args.save_dir), exist_ok=True)

            # write instrinsics
            dict_file = {'names': args.ego_name}
            instri_file = os.path.join(args.calib_dir, 'SuperView_gp.xml')
            assert os.path.exists(instri_file), instri_file
            tree = ET.parse(instri_file)
            root = tree.getroot()
            for child in root:
                dict_file[child.tag] = child.text
            intri_file = os.path.join(args.path, args.save_dir, '{}_intri.json'.format(args.prefix))
            with open(intri_file, 'w') as file:
                json.dump(dict_file, file, indent=4)

            # write extrinsics
            extri_file = os.path.join(args.path, args.save_dir, '{}_extri_{}.json'.format(args.prefix, video[:10]))
            dict_file = {'names': args.ego_name}
            for key in extri_data.keys():
                dict_file[key] = {'T_camera_world': extri_data[key].tolist()}
            with open(extri_file, 'w') as file:
                json.dump(dict_file, file, indent=4)
