import Metashape
import os
import argparse

parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Guitar1',
                    help="root path for a single data collection trial")
parser.add_argument('--prefix', type=str, default='exo',
                    help="ego or exo camera")
parser.add_argument('--license_path', type=str, default='/home/chengp/Documents/metashape-pro/metashape.lic',
                    help="metashape license file path")
args = parser.parse_args()


if __name__ == "__main__":

    print('Exporting data for {}'.format(args.path))

    base_folder = args.path
    save_dir = os.path.join(base_folder, 'outputs', 'Metashape')
    save_file = os.path.join(save_dir, '{}.psx'.format(os.path.basename(base_folder)))
    assert os.path.exists(save_file)

    exo_dir = os.path.join(base_folder, 'Exo')
    assert os.path.exists(exo_dir), exo_dir
    subs = sorted(os.listdir(exo_dir))
    subs = [sub for sub in subs if sub != 'mobile']

    ##################################
    # export camera data
    ##################################
    doc = Metashape.app.document
    doc.open(save_file)
    chunk = doc.chunk

    # chunk.exportCameras(os.path.join(save_dir, '{}_camera_pose.xml'.format(args.prefix)))
    # export to txt
    for sub in subs:
        cam_pose_filename = os.path.join(save_dir, '{}_{}_cam_pose.txt'.format(args.prefix, sub))
        file = open(cam_pose_filename, "wt")
        for camera in chunk.cameras:

            if camera.label[:4] != sub:
                continue

            if not camera.transform:
                continue
            Twc = camera.transform
            calib = camera.sensor.calibration
            file.write(
                "{:6d}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t{:.6f}\t\n".format(
                    camera.key, Twc[0, 0], Twc[1, 0], Twc[2, 0], Twc[0, 1], Twc[1, 1], Twc[2, 1], Twc[0, 2], Twc[1, 2],
                    Twc[2, 2], Twc[0, 3], Twc[1, 3], Twc[2, 3]))
        file.flush()
        file.close()

    # export image name
    for sub in subs:
        im_name_filename = os.path.join(save_dir, '{}_{}_im_name.txt'.format(args.prefix, sub))
        file = open(im_name_filename, "wt")
        for camera in chunk.cameras:

            if camera.label[:4] != sub:
                continue

            if not camera.transform:
                continue
            path = camera.photo.path
            file.write("{:6d}\t{:s}\n".format(camera.key, path))
        file.flush()
        file.close()