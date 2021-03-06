#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import argparse
import os
import os.path
import posixpath
import shutil
import sys
import urllib.parse
import urllib.request
from typing import Any, Dict, Iterable, Iterator, Mapping, Optional, Tuple

import ffmpeg
import youtube_dl
from tqdm import tqdm


class VideoFile:
    def __init__(self, filename):
        self._filename = filename
        self._input = ffmpeg.input(filename)
        self._info = ffmpeg.probe(filename)

    @property
    def filename(self) -> str:
        return self._filename

    @property
    def ffmpeg_input(self) -> Any:
        return self._input

    @property
    def info(self) -> Mapping[str, Any]:
        return self._info

    @property
    def height(self) -> int:
        video_stream = next(
            stream
            for stream in self._info["streams"]
            if stream["codec_type"] == "video"
        )
        return int(video_stream["height"])

    @property
    def contains_audio(self) -> bool:
        for stream in self._info["streams"]:
            if stream["codec_type"] == "audio":
                return True
        return False


def main():
    args = parse_command_line()

    output_dir = os.path.dirname(os.path.abspath(args.output_filename))

    if args.keep_originals or len(args.playlists) == 1:
        video_files = tuple(download(args.playlists, output_dir))
        if len(video_files) == 1:
            move(video_files[0], args.output_filename)
            return
    else:
        video_files = tuple(get_final_urls(args.playlists))
    assert len(video_files) >= 1

    merge(
        video_files,
        args.output_filename,
        args.crf,
        args.preset,
        args.x265,
    )


def download(urls: Iterable[str], output_dir: str) -> Iterator[str]:
    for url in urls:
        url_filename = filename_from_url(url)
        if is_playlist_file(url_filename):
            filename = download_playlist(url, output_dir)
        else:
            filename = os.path.join(output_dir, url_filename)
            download_file(url, filename)
        yield filename


def get_final_urls(urls: Iterable[str]) -> Iterator[str]:
    for url in urls:
        url_filename = filename_from_url(url)
        if is_playlist_file(url_filename):
            final_url = get_playlist_final_url(url)
        else:
            final_url = url
        yield final_url


def get_playlist_final_url(url: str) -> str:
    with youtube_dl.YoutubeDL() as ydl:
        info = ydl.extract_info(url, download=False)
        return info["url"]


def filename_from_url(url: str) -> str:
    path = urllib.parse.urlparse(url).path
    return posixpath.basename(path)


def is_playlist_file(filename: str) -> bool:
    _, extension = posixpath.splitext(filename)
    return extension.lower() == ".m3u8"


def download_playlist(url: str, output_dir: str) -> str:
    with youtube_dl.YoutubeDL(
        {
            "restrictfilenames": True,
            "outtmpl": os.path.join(output_dir, "%(title)s-%(id)s.%(ext)s"),
        }
    ) as ydl:
        info = ydl.extract_info(url)
        filename = ydl.prepare_filename(info)
        return filename


def download_file(url: str, output_filename: str):
    progress_bar: Optional[tqdm] = None
    try:

        def reporthook(blocks_transferred: int, block_size: int, total_size: int):
            nonlocal progress_bar
            if progress_bar is None:
                progress_bar = tqdm(total=total_size, unit="B", unit_scale=True)
            progress_bar.update(block_size)

        urllib.request.urlretrieve(url, output_filename, reporthook)
    finally:
        if progress_bar is not None:
            progress_bar.close()


def move(source: str, destination: str):
    source_ext = os.path.splitext(source)[1]
    destination_ext = os.path.splitext(destination)[1]
    if source_ext.lower() == destination_ext.lower():
        shutil.move(source, destination)
    else:
        shutil.move(source, destination + source_ext)


def merge(
    video_files: Iterable[str],
    output_filename: str,
    crf: int,
    preset: str,
    x265: bool,
):
    inputs = tuple(VideoFile(filename) for filename in video_files)

    final_video = process_video(inputs)

    final_audio = process_audio(inputs)
    if final_audio:
        final_streams = [final_video, final_audio[0]]
        final_audio_params = final_audio[1]
    else:
        final_streams = [final_video]
        final_audio_params = {}

    output_stream = ffmpeg.output(
        *final_streams,
        output_filename,
        vcodec="libx265" if x265 else "libx264",
        crf=crf,
        preset=preset,
        **final_audio_params,
    )

    output_stream.run()


def process_video(inputs: Iterable[VideoFile]) -> Any:
    height = max(video.height for video in inputs)

    streams = [pad_video_height(video, height) for video in inputs]

    final_video = ffmpeg.filter(streams, "hstack")

    return final_video


def pad_video_height(video: VideoFile, height: int) -> Any:
    stream = video.ffmpeg_input.video
    if video.height != height:
        stream = stream.filter(
            "pad", width=0, height=height, x="(ow-iw)/2", y="(oh-ih)/2"
        )
    return stream


def process_audio(inputs: Iterable[VideoFile]) -> Optional[Tuple[Any, Dict[str, Any]]]:
    audio_streams = [
        video.ffmpeg_input.audio for video in inputs if video.contains_audio
    ]
    if not audio_streams:
        return None

    if len(audio_streams) == 1:
        return audio_streams[0], {"acodec": "copy"}
    else:
        return (
            ffmpeg.filter(audio_streams, "amix", inputs=len(audio_streams)),
            {"acodec": "libopus"},
        )


def parse_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("output_filename", help="Path to the output file")
    parser.add_argument("playlists", nargs="+", help="URLs of m3u8 playlists to merge")

    parser.add_argument("--x265", action="store_true", help="Use x265 instead of x264")

    presets = [
        "ultrafast",
        "superfast",
        "veryfast",
        "faster",
        "fast",
        "medium",
        "slow",
        "slower",
        "veryslow",
        "placebo",
    ]
    parser.add_argument(
        "--preset", choices=presets, default="medium", help="x264/x265 preset"
    )

    parser.add_argument("--crf", type=int, default=23, help="x264/x265 CRF value")

    parser.add_argument(
        "--keep-originals", action="store_true", help="Keep original video files"
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
