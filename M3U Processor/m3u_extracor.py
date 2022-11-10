import os
from sys import argv
from shutil import copy2
from tqdm import tqdm

CURR_DIR = os.getcwd()

def extract(m3u_file, destination):
    with open(m3u_file, "r") as f:
        m3u = f.read()
    m3u = m3u.split("\n")
    m3u = [s for s in m3u if s[:1] != "#" and s != ""]
    songs = [s.split("/")[-1] for s in m3u]
    m3u_dir = "/".join(m3u_file.split("/")[:-1])
    if not(destination):
        destination = CURR_DIR + "/Playlist"
    if not os.path.exists(destination):
        os.makedirs(destination)
    for src, song in tqdm(zip(m3u,songs)):
        copy2(m3u_dir + "/" + src, destination + "/" + song)
        
if __name__ == "__main__":
    m3u_f = None
    dest = None
    try:
        m3u_f = argv[1]
        if len(argv) >= 3: 
            dest = argv[2]
    except IndexError as e:
        print("Please provide m3u file name as a parameter")
        exit(1)
    extract(m3u_f, dest)    

