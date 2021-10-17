# panopto-dl

Quick and dirty Panopto downloader

## What does this do?

Given a list of URLs to M3U8 playlists or video files, this script places them
side-by-side into a single video, playing simultaneously; the inputs are stacked
_horizontally_ in order of their appearance on the command-line.

If only a single URL is given, it will be downloaded and moved to the specified location
without any further processing; in this case, if the target filename's extension does
not match the actual downloaded content, the correct extension will be appended.

## Installation

Run `pipenv install` to create a virtualenv for the script.

[`ffmpeg`](https://ffmpeg.org/) and `ffprobe` must be available in `PATH` for the script to work.

_Note_: the Pipfile requires Python 3.7, as that is the version the script has been
developed against and tested on. However, any Python version greater than 3.7 _should_
work as well. Unfortunately, [Pipenv does not support specifying version ranges][2],
so to use a different Python version you'll have to create a virtualenv manually
and install the dependencies from the Pipfile using `pip install`.

## Usage

Note: to run the code inside the virtualenv, use `pipenv run python panopto_dl.py [ARGUMENTS]`.

```
panopto_dl.py [-h] [--x265]
              [--preset {ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow,placebo}]
              [--crf CRF] [--keep-originals]
              output_filename playlists [playlists ...]

positional arguments:
  output_filename       Path to the output file
  playlists             URLs of m3u8 playlists to merge

optional arguments:
  -h, --help            show this help message and exit
  --x265                Use x265 instead of x264 (default: False)
  --preset {ultrafast,superfast,veryfast,faster,fast,medium,slow,slower,veryslow,placebo}
                        x264/x265 preset (default: medium)
  --crf CRF             x264/x265 CRF value (default: 23)
  --keep-originals      Keep original video files (default: False)
```

## Tips

For large output resolutions you may want to try encoding using x265. Passing
`--x265 --crf 28` [should][1] provide the same quality as the default settings,
at half the file size.

[1]: https://trac.ffmpeg.org/wiki/Encode/H.265 "Encode/H.265 - FFmpeg"

[2]: https://stackoverflow.com/a/63515550/851560
