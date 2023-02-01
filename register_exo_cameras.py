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
parser.add_argument('--license_path', type=str, default='/home/chengp/Documents/metashape-pro/metashape.lic',
                    help="metashape license file path")
args = parser.parse_args()


if __name__ == "__main__":

    print('Registering exo cameras for {}'.format(args.path))

    ###################################
    # some parameters
    ###################################
    base_folder = args.path
    exo_dir = os.path.join(base_folder, 'Exo')
    assert os.path.exists(exo_dir), exo_dir
    subs = sorted(os.listdir(exo_dir))
    subs = [sub for sub in subs if sub != 'mobile']
    calib_file = os.path.join(args.calib_dir, 'exo_gp.xml')
    assert os.path.exists(calib_file), calib_file

    save_dir = os.path.join(base_folder, args.save_dir)
    save_file = os.path.join(save_dir, '{}.psx'.format(os.path.basename(base_folder)))
    assert os.path.exists(save_file)

    #### register static aria ####
    doc = Metashape.app.document
    doc.open(save_file)
    chunk = doc.chunk

    print('\t Registering static exo cameras')
    for cam in subs:
        print('\t Registering static exo cameras: {}'.format(cam))
        # prepare file list
        folder_path = os.path.join(exo_dir, cam, 'calib_images')
        assert os.path.exists(folder_path), folder_path
        filelist = os.listdir(folder_path)
        absolute_filelist = [os.path.join(folder_path, filepath) for filepath in filelist]
        absolute_filelist.sort()
        absolute_filelist = absolute_filelist[-20:]
        # add photo
        chunk.addPhotos(absolute_filelist)
        # add camera and assign the photos to it
        sensor = chunk.addSensor()
        calibration = Metashape.Calibration()
        calibration.load(calib_file)
        sensor.label = cam
        sensor.type = Metashape.Sensor.Type.Fisheye
        sensor.width = calibration.width
        sensor.height = calibration.height
        sensor.user_calib = calibration.copy()
        sensor.fixed = True
        print(sensor.type)
        group = chunk.addCameraGroup()
        group.type = Metashape.CameraGroup.Station
        for camera in chunk.cameras:
            if camera.label[:4] == cam:
                camera.sensor = sensor
                camera.group = group
        # match points and align camera
        chunk.matchPhotos(downscale=0, reference_preselection=False, keep_keypoints=True)
        chunk.alignCameras(reset_alignment=False)

    # save project
    doc.save(os.path.join(base_folder, save_file))