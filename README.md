# panopto-dl
Quick and dirty Panopto downloader

## Usage
Note: [`ffmpeg`](https://ffmpeg.org/) and `ffprobe` must be available in `PATH` for the script to work.

Note: the specified URLs will be placed side-by-side into a single video, playing simultaneously;
the inputs will be stacked _horizontally_ in order of their appearance on the command-line.

Note: if only a single URL is given, it will be downloaded and moved to the specified location without
any further processing; if the target filename's extension does not match the actual downloaded content,
the correct extension will be appended.

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
