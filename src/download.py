from dotenv import dotenv_values
import subprocess as sp
from os import environ, path, makedirs, getenv
import secrets

data_dir = getenv('DATA_PATH')
# data_dir = '/data'
FILES_DIR = path.join(data_dir, 'input_files')

def download(items, params):
    run_name = params.get('run_name', None)
    if run_name == None:
        run_name = secrets.token_hex(4)

    download_dir = FILES_DIR
    # if not path.exists(download_dir):
    #     makedirs(download_dir)

    downloaded_files = []
    for item in items:
        name = item['NAME'].replace(' ', '_')
        link = item['LINK']
        ext = ".mp3"

        output_path = path.join(download_dir, name + ext)

        command = [
            'yt-dlp',
            '-f', 'bestaudio/best',
            '--extract-audio',
            '--audio-format', 'mp3',
            '-o', output_path,
            link
        ]

        try:
            print(f'Downloading file {link}...')
            sp.run(command, check=True)
            print(f"File downloaded successfully to {output_path}")
            downloaded_files.append(output_path)
        except sp.CalledProcessError as e:
            print(f"Error downloading file: {e}")
    
    return downloaded_files


if __name__ == "__main__":
    # test
    items = [{'NAME': 'genocide organ - leichenlinie', 'LINK': 'https://youtu.be/4oqxZvUGXe4?si=6ql80J4T04ZYfORh'}]
    download(items)