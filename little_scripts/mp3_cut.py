from pydub import AudioSegment
from os import path, mkdir, chdir
from datetime import datetime


def input_lines() -> list:
    result = list()
    for line in iter(input, ""):
        result.append(line.strip())
    return result


def convert_time(time: str) -> int:
    result = 0
    for n, v in enumerate(time.split(":")[::-1]):
        result += int(v) * 60 ** n
    return result * 1000


def create_segment_list(source: list) -> list:
    result = list()
    for entry in source:
        entry = entry.split(" ", 2)
        time = entry[1]
        track, artist = entry[2].split(" - ")
        result.append([convert_time(time), artist, track])
    return sorted(result)


if __name__ == '__main__':
    start_time_script = datetime.now()
    file_mp3 = input("Input full-path to mp3-file: ")
    file_path, file_name = path.split(file_mp3)
    album = file_name.rsplit(".", 1)[0]
    try:
        mkdir(f"{file_path}/{album}")
        chdir(f"{file_path}/{album}")
    except OSError:
        print(f"Не удалось создать каталог {album}")
#    ► 00:00 Songs name - Artist Name
    segment_list = create_segment_list(input_lines())
    song = AudioSegment.from_mp3(file_mp3)
    length_song = len(song)
    if segment_list[-1][0] != length_song:
        segment_list.append([length_song])
    for n in range(1, len(segment_list)):
        start_time, artist, title = segment_list[n-1]
        stop_time = segment_list[n][0]
        extract = song[start_time:stop_time]
        extract.export(f"{str(n).zfill(3)} {artist} - {title}.mp3", format="mp3", bitrate="320k",
                       tags={"artist": artist, "album": album, "title": title, "track": n})
    print(datetime.now() - start_time_script)
quit()
