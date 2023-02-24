# Music Prepocess

## 2-23 updates
- Remove the usage of convert_SuperView_4x3.py. All videos are captured on Wide mode.   
- Updated synchronization.py to new protocol. Add augments ego_start_sec and exo_start_sec for speeding up. Start QR code scanning after ego_start_sec and exo_start_sec. 
- Updated cut_video.py for cutting videos automatically. Add augment timestamp_path to read begin/end time to each section (in sec) for the separator in ego camera. 
- Minor changes in implementation of register_exo_cameras.py to register exo cameras together.
- For testing, use 0217_Violin, rename Ego/gp05/GX010009.MP4 to Ego/gp05/GX030008.MP4, and Ego/gp05/GX020009.MP4 to Ego/gp05/GX040008.MP4
- Additional note: if change decode exo to clipped video, decode just the first clip with fps=5. 

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
`CALIB_FILE_FOLDER=/Data/Music/calib_files` 

### Synchronize the videos and generate clips
Synchronize all the videos with their qr_code_timestamp-video_timestamp.  
Browse the ego and on of the exo videos to have a rough estimate of the time QR code is shown to the cameras and set it to ego_QR_time and exo_QR_time to speed up.  
`python synchronization.py --path ${DATA_ROOT_FOLDER} --ego_start_sec ego_QR_time --exo_start_sec exo_start_time`  
Browse the ego camera videos to get a rough estimate of the time (in sec) of the begin/end for each section. 
Save the timestamps in Ego/gp05/timestamps.json (See examples in the folder).    
Generate clips with respect to separator. Multiple videos are merged and save in this code (which may take quite some time).   
`python cut_videos.py --path ${DATA_ROOT_FOLDER}`

### Decode videos to images
Decode exo and ego videos to images  
`python decode_video.py --path ${DATA_ROOT_FOLDER} --decode_mobile --decode_exo --decode_ego`

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


