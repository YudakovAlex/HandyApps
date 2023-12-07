import os
import sys
import argparse
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from mutagen.oggvorbis import OggVorbis


AVAILABLE_EXTENSIONS = [".mp3", ".flac", ".ogg"]


def get_mime_type(image_path):
    """
    Determine the MIME type based on the image file extension.
    Currently supports JPEG and PNG.
    """
    _, ext = os.path.splitext(image_path)
    return "image/jpeg" if ext.lower() in ['.jpg', '.jpeg'] else "image/png"


def add_thumbnail_to_flac(file_path, image_data, mime_type):
    """
    Add thumbnail to FLAC file.
    """
    audio = FLAC(file_path)
    pic = Picture()
    pic.data = image_data
    pic.type = 3  # front cover
    pic.mime = mime_type
    audio.add_picture(pic)
    audio.save()


def add_thumbnail_to_mp3(file_path, image_data, mime_type):
    """
    Add thumbnail to MP3 file.
    """
    audio = MP3(file_path, ID3=ID3)
    audio.tags.add(APIC(
        encoding=3,  # utf-8
        mime=mime_type,
        type=3,  # front cover
        desc=u"Cover",
        data=image_data
    ))
    audio.save()


def add_thumbnail_to_ogg(file_path, image_data, mime_type):
    """
    Add thumbnail to OGG file.
    """
    audio = OggVorbis(file_path)
    audio["COVERART"] = image_data.encode("base64").strip()
    audio.save()


def add_thumbnail(file_path, image_path):
    """
    Add a thumbnail to an audio file. Supports FLAC, MP3, WAV, and OGG formats.
    """
    mime_type = get_mime_type(image_path)
    file_type = os.path.splitext(file_path)[1].lower()
    with open(image_path, 'rb') as f:
        image_data = f.read()

    if file_type == ".flac":
        add_thumbnail_to_flac(file_path, image_data, mime_type)
    elif file_type == ".mp3":
        add_thumbnail_to_mp3(file_path, image_data, mime_type)
    elif file_type == ".ogg":
        add_thumbnail_to_ogg(file_path, image_data, mime_type)
    else:
        print("Unsupported file type.")
        return


def parse_arguments():
    """
    Parse command-line arguments using argparse.
    """
    parser = argparse.ArgumentParser(description="Add thumbnails to audio files.")
    parser.add_argument("input_path", help="Input folder or file path")
    parser.add_argument("image_file", help="Path to the image file")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    input_path = args.input_path
    image_file = args.image_file

    # Check if the input path is a file or a folder and generate absolute paths
    if os.path.isdir(input_path):
        audio_files = [os.path.join(input_path, file) for file in os.listdir(input_path) if file.endswith(tuple(AVAILABLE_EXTENSIONS))]
    elif os.path.isfile(input_path) and input_path.endswith(tuple(AVAILABLE_EXTENSIONS)):
        audio_files = [input_path]
    else:
        print("Invalid input. Please provide a valid folder or audio file path.")
        sys.exit(1)

    # Process each audio file
    for audio_file in audio_files:
        try:
            add_thumbnail(audio_file, image_file)
            print(f"Added thumbnail for {audio_file}")
        except Exception as e:
            print(f"Failed to embed thumbnail for {audio_file}: {e}")
