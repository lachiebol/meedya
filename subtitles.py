import re
from collections import defaultdict
import logging
import os


log_file = "subtitle_merger.log"
logging.basicConfig(
    filename=log_file,
    filemode='a',
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)




logging.getLogger().addHandler(logging.StreamHandler())

def main():
    logging.info("Starting subtitle merge process...")
    files = os.listdir(r'/mnt/f/TV')
    for file in files:
        show_path = rf"/mnt/f/TV/{file}"
        if not os.path.isdir(show_path):
            logging.debug(f"Skipping {file}, not a directory.")
            continue

        seasons = os.listdir(show_path)
        for season in seasons:
            season_path = rf"{show_path}/{season}"
            if not os.path.isdir(season_path):
                logging.warning(f"{season} is not a directory, skipping...")
                continue
            try:
                episodes = find_episode_subtitles(season_path)
                for episode, data in episodes.items():
                    episode_name = data["video"]
                    subtitles = data["subtitles"]
                    

                    if not episode_name:
                        logging.debug(f"No video found for episode {episode} in {season}")
                        continue

                    lang_tags = list(subtitles.keys())

                    if any("combined" in tag for tag in lang_tags):
                        logging.info(f"Skipping {episode_name} in {season}, already combined.")
                        continue

                    if len(lang_tags) == 2:
                        sub1 = subtitles[lang_tags[0]]
                        sub2 = subtitles[lang_tags[1]]

                        if sub1 and sub2:
                            logging.info(f"Combining subtitles for {episode_name} in {season}: {lang_tags}")
                            merge_subtitles(
                                rf"{season_path}/{sub1}",
                                rf"{season_path}/{sub2}",
                                season_path
                            )
                    else:
                        logging.debug(f"Episode {episode} in {season} has {len(lang_tags)} subtitle(s): {lang_tags}")
            except Exception as e:
                logging.error(f"Error processing {season_path}: {e}")


def find_episode_subtitles(folder, video_exts=(".mkv", ".mp4", ".avi"), sub_ext=".srt"):
    episodes = defaultdict(lambda: {"video": None, "subtitles": {}})


    for filename in os.listdir(folder):
        lower = filename.lower()
        name, ext = os.path.splitext(filename)

        if ext in video_exts:
            episodes[name]["video"] = filename
            continue

        if lower.endswith(sub_ext):
            match = re.match(r"(.+?)\.((?:\w+\.)*\w+)\.srt", filename)
            if match:
                stem, lang_tag = match.groups()
                episodes[stem]["subtitles"][lang_tag] = filename

    return episodes


def merge_subtitles(file1, file2):
    logging.debug(f"Reading subtitle files: {file1}, {file2}")
    try:
        with open(file1, 'r', encoding='utf-8') as f1, open(file2, 'r', encoding='utf-8') as f2:
            basefile_array = f1.readlines()
            otherfile_array = f2.readlines()
    except FileNotFoundError as e:
        logging.error(f"File not found: {e}")
        return

    basefile_indexes, basefile_timestamps, basefile_subtitles = extract_subtitles(basefile_array)
    otherfile_indexes, otherfile_timestamps, otherfile_subtitles = extract_subtitles(otherfile_array)

    newfile_indexes, newfile_timestamps, newfile_subtitles = [], [], []

    for i in range(len(basefile_timestamps)):
        nearest_timestamp = find_closest_timestamp(otherfile_timestamps, basefile_timestamps[i])
        newfile_indexes.append(i)
        if nearest_timestamp:
            nearest_subtitle_index = otherfile_timestamps.index(nearest_timestamp)
            newfile_timestamps.append(basefile_timestamps[i])
            if nearest_subtitle_index > len(otherfile_subtitles) - 1:
                logging.warning(f"No matching subtitle for timestamp {basefile_timestamps[i]} in {file2}")
                newfile_subtitles.append(basefile_subtitles[i])
            else:
                combined_subtitle = f"{basefile_subtitles[i]}/n{otherfile_subtitles[nearest_subtitle_index]}"
                newfile_subtitles.append(combined_subtitle)

    output_file = file1.rsplit('.', 1)[0] + '_combined.srt'

    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            for index, timestamp, subtitle in zip(newfile_indexes, newfile_timestamps, newfile_subtitles):
                f.write(f"{index + 1}/n")
                f.write(f"{timestamp}/n")
                f.write(f"{subtitle}/n/n")
        logging.info(f"Combined subtitles written to {output_file}")
    except Exception as e:
        logging.error(f"Error writing combined file {output_file}: {e}")


def find_closest_timestamp(timestamps, target_timestamp, tolerance=1):
    for timestamp in timestamps:
        if timestamp.startswith(target_timestamp):
            return timestamp
        try:
            start_time, end_time = timestamp.split(' --> ')
            start_time_seconds = timestamp_to_seconds(start_time)
            end_time_seconds = timestamp_to_seconds(end_time)

            target_start_time, target_end_time = target_timestamp.split(' --> ')
            target_start_seconds = timestamp_to_seconds(target_start_time)
            target_end_seconds = timestamp_to_seconds(target_end_time)

            if abs(target_start_seconds - start_time_seconds) <= tolerance or abs(target_end_seconds - end_time_seconds) <= tolerance:
                return timestamp
        except Exception as e:
            logging.warning(f"Invalid timestamp format encountered: {timestamp} or {target_timestamp}: {e}")
    return None


def extract_subtitles(file_array):
    indexes = []
    timestamps = []
    subtitles = []
    current_subtitle = []

    for line in file_array:
        line = line.strip()
        if not line:
            continue
        if line.isdigit():
            if current_subtitle:
                subtitles.append('/n'.join(current_subtitle))
                current_subtitle = []
            indexes.append(int(line))
        elif '-->' in line:
            timestamps.append(line)
        else:
            current_subtitle.append(line)

    if current_subtitle:
        subtitles.append('/n'.join(current_subtitle))

    return indexes, timestamps, subtitles


def timestamp_to_seconds(timestamp):
    h, m, s_ms = timestamp.split(":")
    s, ms = s_ms.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


if __name__ == "__main__":
    main()
