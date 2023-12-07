import os
import argparse
from shutil import copy2

def extract(m3u_file, destination=None):
    """
    Extracts songs from an M3U playlist and copies them to the specified destination.
    """
    # Determine the directory and base name of the M3U file
    m3u_dir = os.path.dirname(m3u_file)
    m3u_base_name = os.path.splitext(os.path.basename(m3u_file))[0]

    # Default destination directory based on M3U file name
    if not destination:
        destination = os.path.join(m3u_dir, m3u_base_name)

    # Create the destination directory if it doesn't exist
    os.makedirs(destination, exist_ok=True)

    with open(m3u_file, "r") as file:
        for line in file:
            if not line.startswith('#') and line.strip():
                # Extract the song name and construct source and destination paths
                song = os.path.basename(line.strip())
                src = line.strip()
                dest = os.path.join(destination, song)

                # Copy the file
                try:
                    copy2(src, dest)
                except IOError as e:
                    print(f"Error copying {src}: {e}")
    print("Done. Songs copied to " + destination)

def parse_arguments():
    """
    Parses command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Extract songs from an M3U playlist.")
    parser.add_argument("m3u_file", help="Path to the M3U file")
    parser.add_argument("destination", nargs='?', default=None, help="Destination directory (optional)")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    extract(args.m3u_file, args.destination)
    
