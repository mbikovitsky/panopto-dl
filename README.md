# panopto-dl
Quick and dirty Panopto downloader

## Usage

```
usage: panopto_dl.py [-h] [--camera CAMERA]
                     [--preset {ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow,placebo}]
                     [--crf CRF] [--keep-originals]
                     presentation output_filename

positional arguments:
  presentation          URL of the presentation master.m3u8 playlist
  output_filename       Path to the output file

optional arguments:
  -h, --help            show this help message and exit
  --camera CAMERA       URL of the camera master.m3u8 playlist (default: None)
  --preset {ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow,placebo}
                        x264 preset (default: medium)
  --crf CRF             x264 CRF value (default: 23)
  --keep-originals      Keep original video files (default: False)
```
