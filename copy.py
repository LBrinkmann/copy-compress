import os
import random
import sys
from time import sleep
import subprocess
from shutil import copyfile



DEVICE_NAMES = os.environ['DEVICE_NAMES'].split(',')
DEVICE_PATH = os.environ['DEVICE_PATH']

extensions = ['mov', 'mp4', 'mts']

low_command = 'ffmpeg -i "{}"  -vf scale=720:480 "{}"'


high_command = 'ffmpeg -i "{}" -vf scale=1080:720 "{}"'

batch_size = 1


def list_all_files(path):
    files = []
    for r, d, f in os.walk(path):
        for ff in f:
            filename, ext = os.path.splitext(ff)
            if ext[1:].lower() in extensions:
                rel_r = r[len(path) + 1:]
                files.append(os.path.join(rel_r, ff))
    return files


def store_file_list(directory, files, name, append=False):
    mode = 'w+' if append else 'w'
    directory = os.path.join(directory, 'sync/data')
    ensure_path(directory)
    filename = os.path.join(directory, name + '.txt')
    with open(filename, mode) as f:
        for l in files:
            l = l + '\n'
            f.write(l)

def load_file_list(directory, name):
    filename = os.path.join(directory, 'sync/data', name + '.txt')
    with open(filename, 'r') as f:
        return [l[:-1] for l in f.readlines()]

def ensure_path(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def process(path, source, destination, command):
    in_file = os.path.join(source, path)
    path_woext, ext = os.path.splitext(path)
    folder, filename = os.path.split(path_woext)
    out_folder = os.path.join(destination, folder)
    ensure_path(out_folder)
    out_path = path_woext + '.mp4'
    out_file = os.path.join(destination, out_path)
    command = command.format(in_file, out_file)
    resp = subprocess.run(command, stdout=subprocess.PIPE, shell=True, check=True, text=True)



def loop(directory):

    original_dir = os.path.join(directory, 'film')
    low_dir = os.path.join(directory, 'sync/low')
    high_dir = os.path.join(directory, 'sync/high')
    ensure_path(original_dir)
    ensure_path(low_dir)
    ensure_path(high_dir)

    original_files = list_all_files(original_dir)
    # print(original_files)

    low_files = list_all_files(low_dir)
    high_files = list_all_files(high_dir)


    store_file_list(directory, original_files, 'original')
    store_file_list(directory, low_files, 'low')
    store_file_list(directory, high_files, 'high')

    try:
        high_requested = load_file_list(directory, 'requested')
    except:
        high_requested = []

    try:
        high_error = load_file_list(directory, 'high_error')
    except:
        high_error = []
    try:
        low_error = load_file_list(directory, 'low_error')
    except:
        low_error = []
    try:
        high_success = load_file_list(directory, 'high_success')
    except:
        high_success = []
    try:
        low_success = load_file_list(directory, 'low_success')
    except:
        low_success = []

    high_batch = list(set(high_requested) - set(high_success) - set(high_error))
    # random.shuffle(high_batch)

    for path in high_batch:
        try:
            process(path, original_dir, high_dir, high_command)
            high_success = high_success + [path]
            store_file_list(directory, high_success, 'high_success')
            print('Successfully compressed (high)' + path)
        except:
            high_error = high_error + [path]
            print('Error compressing (high)' + path)
            store_file_list(directory, high_error, 'high_error')
            # raise Error('HELP')

    low_batch = list(set(original_files) - set(low_success) - set(low_error))
    # random.shuffle(low_batch)

    for path in low_batch[:batch_size]:
        try:
            process(path, original_dir, low_dir, low_command)
            low_success = low_success + [path]
            store_file_list(directory, low_success, 'low_success')
            print('Successfully compressed (low)' + path)
        except:
            low_error = low_error + [path]
            print('Error compressing (low)' + path)
            store_file_list(directory, low_error, 'low_error')

    sleep(2)
    print('Finished Loop')

if __name__ == '__main__':
    while True:
        for d in DEVICE_NAMES:
            directory = os.path.join(DEVICE_PATH, d)
            if os.path.exists(directory):
                foto_dir = os.path.join(directory, 'foto')
                ensure_path(foto_dir)
                print("Compression files in " + directory)
                loop(directory)

