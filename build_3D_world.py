import Metashape
import os
import argparse


parser = argparse.ArgumentParser('Music data prepocess')
parser.add_argument('--path', type=str, default='/media/shan/Volume1/Data/Music/SessionDate200123_Guitar1',
                    help="root path for a single data collection trial")
parser.add_argument('--calib_dir', type=str, default='/media/shan/Volume1/Data/Music/calib_files',
                    help="folder for calibration files")
parser.add_argument('--use_cam', type=str, default='gp01',
                    help="define the came")
# parser.add_argument('--license_path', type=str, default='/home/chengp/Documents/metashape-pro/metashape.lic',
#                     help="metashape license file path")
args = parser.parse_args()

# Metashape.License().activate("EU36T-1TAPF-9XUVJ-1SCNN-CBZD8")


if __name__ == "__main__":

    print('Reconstructing 3D for {}'.format(args.path))

    ###################################
    # some parameters
    ###################################
    base_folder = args.path
    image_dir = os.path.join(base_folder, 'Exo', 'mobile', 'calib_images')
    assert os.path.exists(image_dir), image_dir
    calib_file = os.path.join(args.calib_dir, '{}.xml'.format(args.use_cam))
    assert os.path.exists(calib_file), calib_file

    save_dir = os.path.join(base_folder, 'outputs', 'Metashape')
    os.makedirs(save_dir, exist_ok=True)
    save_file = os.path.join(save_dir, '{}.psx'.format(os.path.basename(base_folder)))

    ##################################
    # build 3D environment and register cameras
    ##################################
    # doc = Metashape.Document()
    # chunk = doc.addChunk()
    # doc.save(os.path.join(base_folder, save_file))

    doc = Metashape.app.document
    chunk = doc.chunk

    ### build 3D environment by room scan ####
    print('\t Building environment')
    # prepare file list
    filelist = os.listdir(image_dir)
    absolute_filelist = [os.path.join(image_dir, filepath) for filepath in filelist]
    absolute_filelist.sort()
    # add photo
    chunk.addPhotos(absolute_filelist)
    # add camera and assign the photos to it
    sensor = chunk.addSensor()
    calibration = Metashape.Calibration()
    calibration.load(calib_file)
    sensor.label = 'mobile_gp'
    sensor.type = Metashape.Sensor.Type.Fisheye
    sensor.width = calibration.width
    sensor.height = calibration.height
    sensor.user_calib = calibration.copy()
    print(sensor.type)
    for camera in chunk.cameras:
        camera.sensor = sensor
    # match points and align camera
    chunk.matchPhotos(downscale=0, reference_preselection=False, keep_keypoints=True)
    chunk.alignCameras(reset_alignment=False)
    # save project
    # doc.save(os.path.join(base_folder, save_file))


    ### reconstruct dense cloud ####
    print('\t Reconstructing dense point cloud')
    # # reload from saved project
    # doc = Metashape.app.document
    # doc.open(os.path.join(base_folder, save_file))
    # chunk = doc.chunk

    # build depth maps and dense point cloud
    chunk.buildDepthMaps(downscale=1)
    chunk.buildDenseCloud() # optionally
    # build mesh model
    chunk.buildModel(surface_type=Metashape.Arbitrary, interpolation=Metashape.EnabledInterpolation,
                     source_data=Metashape.DepthMapsData)
    doc.save(os.path.join(base_folder, save_file))