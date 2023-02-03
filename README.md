# Music Prepocess

## Input and Output
### Input 
Captured data in the following data structure, and camera intrinsics parameters. 
- [SessionDateDDMMYY]_[SubjectName]_[Instrument]
  - Ego
    - gp05
      - ego_cam001.MP4
    - aria01
      - aria001.MP4
  - Exo
    - gp01
      - cam001.MP4, ...
    - gp02
      - cam002.MP4, ...
    - gp03
      - cam003.MP4, ...
    - gp04
      - cam004.MP4, ...
    - mobile
      - room_scan.MP4

### Output
- An output folder that contains: 
  - Synchronized video clips for exo and ego videos. Each clip contains the player playing scales, Suzuki pieces or free play
  - Calibrated camera pose for exo cameras (one for each exo camera)
  - Calibrated camera pose for ego cameras (one for each frame, one file for each clip)

## Procedure
`DATA_ROOT_FOLDER=/Data/Music/SessionDate200123_Guitar1`  
`CALIB_FILE_FOLDER=/Data/Music/calib_files` (Use SuperView parameter for gp03 now to account for wrong camera configuration in data collection. Need to change back to wide)
### Pre process SuperView videos
Change SuperView from 16:9 to 4:3. This take quite some time.  
`python convert_SuperView_4x3.py --path ${DATA_ROOT_FOLDER} --calib_dir ${CALIB_FILE_FOLDER}`

### Synchronize the videos and generate clips
Synchronize all the videos with their qr_code_timestamp-video_timestamp. This takes quite some time.    
`python synchronization.py --path ${DATA_ROOT_FOLDER}`  
TODO: Generate clips with respect to separator. Merge multiple videos  
`python cut_videos.py --path ${DATA_ROOT_FOLDER}`

### Decode videos to images
Decode exo and ego videos to images  
`python decode_video.py --path ${DATA_ROOT_FOLDER} --decode_mobile --decode_static_exo --decode_ego`

### Metashape reconstruction
#### If without license
Open Metashape GUI and run the following script in GUI  
Build 3D environment from room scan (TODO: which camera is used for room scan)   
`build_3D_world` with `--path ${DATA_ROOT_FOLDER} --calib_dir ${CALIB_FILE_FOLDER}`  
Register static exo cameras  
`register_exo_cameras.py` with `--path ${DATA_ROOT_FOLDER} --calib_dir ${CALIB_FILE_FOLDER}`  
Export exo camera data  
`export_data.py` with `--path ${DATA_ROOT_FOLDER} --prefix exo`  
Ego camera registration and data export. This takes quite some time.  
`register_ego_cameras.py` with `--path ${DATA_ROOT_FOLDER} --calib_dir ${CALIB_FILE_FOLDER} --batch_size 500`
#### If with license


### Parse Metashape output 
Parse exo camera parameters  
`python parse_metashape_output.py --path ${DATA_ROOT_FOLDER} --calib_dir ${CALIB_FILE_FOLDER} --prefix exo`  
Parse ego camera parameters  
`python parse_metashape_output.py --path ${DATA_ROOT_FOLDER} --calib_dir ${CALIB_FILE_FOLDER} --prefix ego`  


