#!/usr/bin/env python3.7
# -*- coding: utf-8 -*-

import argparse
import os
import os.path
import shutil
import sys
from typing import Optional, Tuple

import ffmpeg
import youtube_dl


def main():
    args = parse_command_line()

    output_dir = os.path.dirname(os.path.abspath(args.output_filename))

    presentation_filename, camera_filename = download(
        args.presentation, args.camera, output_dir
    )

    if not args.camera:
        shutil.move(presentation_filename, args.output_filename)
        return

    merge(
        presentation_filename,
        camera_filename,
        args.output_filename,
        args.crf,
        args.preset,
    )

    if args.keep_originals:
        return

    os.remove(presentation_filename)
    if args.camera:
        os.remove(camera_filename)


def download(
    presentation_url: str, camera_url: Optional[str], output_dir: str
) -> Tuple[str, Optional[str]]:
    with youtube_dl.YoutubeDL(
        {
            "restrictfilenames": True,
            "outtmpl": os.path.join(output_dir, "%(title)s-%(id)s.%(ext)s"),
        }
    ) as ydl:
        presentation_info = ydl.extract_info(presentation_url)
        presentation_filename = ydl.prepare_filename(presentation_info)

        if camera_url:
            camera_info = ydl.extract_info(camera_url)
            camera_filename = ydl.prepare_filename(camera_info)
        else:
            camera_filename = None

    return presentation_filename, camera_filename


def merge(
    presentation_filename: str,
    camera_filename: str,
    output_filename: str,
    crf: int,
    preset: str,
):
    presentation = ffmpeg.input(presentation_filename)
    camera = ffmpeg.input(camera_filename)

    final_video = process_video(
        presentation, presentation_filename, camera, camera_filename
    )

    final_audio, params = process_audio(
        presentation, presentation_filename, camera, camera_filename
    )

    if final_audio:
        final_streams = [final_video, final_audio]
    else:
        final_streams = [final_video]

    output_stream = ffmpeg.output(
        *final_streams,
        output_filename,
        vcodec="libx264",
        crf=crf,
        preset=preset,
        **params
    )

    output_stream.run()


def process_video(
    presentation, presentation_filename: str, camera, camera_filename: str
):
    presentation_height = video_height(presentation_filename)
    camera_height = video_height(camera_filename)

    camera = camera.video
    presentation = presentation.video

    if presentation_height >= camera_height:
        camera = camera.filter(
            "pad", width=0, height=presentation_height, x="(ow-iw)/2", y="(oh-ih)/2"
        )
    else:
        presentation = presentation.filter(
            "pad", width=0, height=camera_height, x="(ow-iw)/2", y="(oh-ih)/2"
        )

    final_video = ffmpeg.filter([presentation, camera], "hstack")

    return final_video


def video_height(filename: str) -> int:
    video_stream = next(
        stream
        for stream in ffmpeg.probe(filename)["streams"]
        if stream["codec_type"] == "video"
    )
    return int(video_stream["height"])


def process_audio(
    presentation, presentation_filename: str, camera, camera_filename: str
):
    camera_contains_audio = contains_audio(camera_filename)
    presentation_contains_audio = contains_audio(presentation_filename)

    codec = "copy"

    if presentation_contains_audio and camera_contains_audio:
        final_audio = ffmpeg.filter([presentation.audio, camera.audio], "amix")
        codec = "libopus"
    elif camera_contains_audio:
        final_audio = camera.audio
    elif presentation_contains_audio:
        final_audio = presentation.audio
    else:
        final_audio = None

    return final_audio, {"acodec": codec}


def contains_audio(filename: str) -> bool:
    for stream in ffmpeg.probe(filename)["streams"]:
        if stream["codec_type"] == "audio":
            return True
    return False


def parse_command_line() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "presentation", help="URL of the presentation master.m3u8 playlist"
    )
    parser.add_argument("--camera", help="URL of the camera master.m3u8 playlist")

    parser.add_argument("output_filename", help="Path to the output file")

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
        "--preset", choices=presets, default="medium", help="x264 preset"
    )

    parser.add_argument("--crf", type=int, default=23, help="x264 CRF value")

    parser.add_argument(
        "--keep-originals", action="store_true", help="Keep original video files"
    )

    return parser.parse_args()


if __name__ == "__main__":
    sys.exit(main())
