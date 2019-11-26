import os
from time import sleep
import subprocess


MOVIE_FOLDER_ORIGINAL = os.environ['MOVIE_FOLDER_ORIGINAL']
MOVIE_FOLDER_LOW = os.environ['MOVIE_FOLDER_LOW']
MOVIE_FOLDER_HIGH = os.environ['MOVIE_FOLDER_HIGH']
MOVIE_FOLDER_DATA = os.environ['MOVIE_FOLDER_DATA']

extensions = ['mov', 'mp4', 'mts']

low_command = 'ffmpeg -i {} -vf scale=720:480 {}'
high_command = 'cp {} {}'

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


def store_file_list(files, name, append=False):
    mode = 'w+' if append else 'w'
    with open(MOVIE_FOLDER_DATA + '/' + name + '.txt', mode) as f:
        f.writelines(f + '\n' for f in files)

def load_file_list(name):
    with open(MOVIE_FOLDER_DATA + '/' + name + '.txt', 'r') as f:
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
    print(command)
    process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()


def loop():
    original_files = list_all_files(MOVIE_FOLDER_ORIGINAL)
    low_files = list_all_files(MOVIE_FOLDER_LOW)
    high_files = list_all_files(MOVIE_FOLDER_HIGH)
    store_file_list(original_files, 'original')
    store_file_list(low_files, 'low')
    store_file_list(high_files, 'high')

    try:
        high_requested = load_file_list('requested')
    except:
        high_requested = []

    try:
        high_error = load_file_list('high_error')
    except:
        high_error = []
    try:
        low_error = load_file_list('low_error')
    except:
        low_error = []
    try:
        high_success = load_file_list('high_success')
    except:
        high_success = []
    try:
        low_success = load_file_list('low_success')
    except:
        low_success = []

    high_batch = list(set(high_requested) - set(high_success) - set(high_error))
    for path in high_batch:
        try:
            process(path, MOVIE_FOLDER_ORIGINAL, MOVIE_FOLDER_HIGH, high_command)
            high_success = high_success + [path]
            store_file_list(high_success, 'high_success')
        except:
            high_error = high_error + [path]
            store_file_list(high_error, 'high_error')

    low_batch = list(set(original_files) - set(low_success) - set(low_error))[:batch_size]
    # print(original_files, low_success, low_error, low_batch)

    for path in low_batch:
        try:
            process(path, MOVIE_FOLDER_ORIGINAL, MOVIE_FOLDER_LOW, low_command)
            low_success = low_success + [path]
            # print("HDHHHHHHHH", low_success)
            store_file_list(low_success, 'low_success')
        except:
            low_error = low_error + [path]
            store_file_list(low_error, 'low_error')

    sleep(2)
    print('Finished Loop')

if __name__ == '__main__':
    ensure_path(MOVIE_FOLDER_DATA)
    ensure_path(MOVIE_FOLDER_ORIGINAL)
    ensure_path(MOVIE_FOLDER_LOW)
    ensure_path(MOVIE_FOLDER_HIGH)
    while True:
        loop()
