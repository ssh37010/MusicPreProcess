import Metashape
import os
import argparse


parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Guitar1',
                    help="root path for a single data collection trial")
parser.add_argument('--calib_dir', type=str, default='/media/shan/Volume1/Data/Music/calib_files',
                    help="folder for calibration files")
parser.add_argument('--save_dir', type=str, default='outputs/Metashape',
                    help="folder for save files")
parser.add_argument('--ego_video_dir', type=str, default='outputs/video_clips/gp05',
                    help="folder for ego video clips")
parser.add_argument('--batch_size', type=int, default=500,
                    help="max number of images for registration")
parser.add_argument('--prefix', type=str, default='ego',
                    help="ego or exo")
parser.add_argument('--license_path', type=str, default='/home/chengp/Documents/metashape-pro/metashape.lic',
                    help="metashape license file path")
args = parser.parse_args()


if __name__ == "__main__":

    print('Registering ego cameras for {}'.format(args.path))

    base_folder = args.path
    save_dir = os.path.join(base_folder, args.save_dir)
    save_file = os.path.join(save_dir, '{}.psx'.format(os.path.basename(base_folder)))
    assert os.path.exists(save_file)
    doc = Metashape.app.document
    doc.open(save_file)
    chunk = doc.chunk

    calib_file = os.path.join(args.calib_dir, 'SuperView_gp.xml')
    assert os.path.exists(calib_file), calib_file

    ego_video_dir = os.path.join(args.path, args.ego_video_dir)
    assert os.path.exists(ego_video_dir), ego_video_dir
    ego_video_files = sorted(os.listdir(ego_video_dir))
    ego_video_files = [file for file in ego_video_files if file.endswith('MP4')]

    im_file_list = sorted(os.listdir(os.path.join(ego_video_dir, 'images')))
    for video in ego_video_files:
        sub_file_list = [os.path.join(ego_video_dir, 'images', file) for file in im_file_list if file[:10] == video[:10]]

        num_batch = int(len(sub_file_list)/args.batch_size) + 1

        for idx in range(num_batch):
            start_id = idx * args.batch_size
            end_id = min(len(sub_file_list), (idx+1) * args.batch_size)

            # add photo
            chunk.addPhotos(sub_file_list[start_id:end_id])
            # add camera and assign the photos to it
            sensor = chunk.addSensor()
            calibration = Metashape.Calibration()
            calibration.load(calib_file)
            sensor.label = 'head_mounted_gopro'
            sensor.type = Metashape.Sensor.Type.Fisheye
            sensor.width = calibration.width
            sensor.height = calibration.height
            sensor.user_calib = calibration.copy()
            sensor.fixed = True
            print(sensor.type)
            for camera in chunk.cameras:
                if camera.label[:10] == video[:10]:
                    camera.sensor = sensor
            # match points and align camera
            chunk.matchPhotos(downscale=0, reference_preselection=False, keep_keypoints=True)
            chunk.alignCameras(reset_alignment=False)

            # save camera pose
            cam_pose_filename = os.path.join(save_dir, '{}_{}_cam_pose_{:03d}.txt'.format(args.prefix, video[:10], idx))
            file = open(cam_pose_filename, "wt")
            for camera in chunk.cameras:

                if camera.label[:10] != video[:10]:
                    continue

                if not camera.transform:
                    continue
                Twc = camera.transform
                calib = camera.sensor.calibration
                file.write(
                    "{:6d}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t\n".format(
                        camera.key, Twc[0, 0], Twc[1, 0], Twc[2, 0], Twc[0, 1], Twc[1, 1], Twc[2, 1], Twc[0, 2],
                        Twc[1, 2],
                        Twc[2, 2], Twc[0, 3], Twc[1, 3], Twc[2, 3]))
            file.flush()
            file.close()

            # save image name
            im_name_filename = os.path.join(save_dir, '{}_{}_im_name_{:03d}.txt'.format(args.prefix, video[:10], idx))
            file = open(im_name_filename, "wt")
            for camera in chunk.cameras:

                if camera.label[:10] != video[:10]:
                    continue

                if not camera.transform:
                    continue
                path = camera.photo.path
                file.write("{:6d}\t{:s}\n".format(camera.key, path))
            file.flush()
            file.close()

            # remove camera
            remove_list = [camera for camera in chunk.cameras if camera.label[:10] == video[:10]]
            chunk.remove(remove_list)