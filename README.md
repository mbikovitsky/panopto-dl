# panopto-dl
Quick and dirty Panopto downloader

## Usage

```
panopto_dl.py [-h]
              [--preset {ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow,placebo}]
              [--crf CRF] [--keep-originals]
              output_filename playlists [playlists ...]

positional arguments:
  output_filename       Path to the output file
  playlists             URLs of m3u8 playlists to merge

optional arguments:
  -h, --help            show this help message and exit
  --preset {ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow,placebo}
                        x264 preset (default: medium)
  --crf CRF             x264 CRF value (default: 23)
  --keep-originals      Keep original video files (default: False)
```
