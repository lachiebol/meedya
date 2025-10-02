from typing import Dict, Any, List, Optional
from models.subtitle import Subtitle,SubtitleEntry
from utils.logger import logger  

class SubtitleMerger:
    def __init__(self):
        logger.info("SubtitleMerger initialized")

    def merge(self, base_subtitle: Subtitle, merge_subtitle: Subtitle) -> None:
        logger.info(f"Starting merge: base={base_subtitle.file_path}, merge={merge_subtitle.file_path}")

        new_subtitle = Subtitle(file_path="", format="srt", language="combined")

        base_entries = base_subtitle.entries
        merge_entries = merge_subtitle.entries

        new_entries = []
        for i in range(len(base_entries)):
            subtitle = base_entries[i]
            nearest_subtitle = self.__find_closest_subtitle(subtitle, merge_entries)

            if nearest_subtitle:
                nearest_subtitle_index = merge_entries.index(nearest_subtitle)
                if nearest_subtitle_index > len(merge_entries) - 1:
                    logger.warning(f"No matching subtitle for timestamp {subtitle['timestamp']} in {merge_subtitle.file_path}")
                    new_text = subtitle.text
                else:
                    new_text = f"{subtitle.text}\n{nearest_subtitle.text}"
            else:
                logger.debug(f"No close subtitle found for base entry index {i} timestamp {subtitle['timestamp']}")
                new_text = subtitle["text"]



            entry=SubtitleEntry(index=i+1,timestamp=subtitle['timestamp'],text=new_text)

            new_entries.append(entry)

        new_subtitle.entries = new_entries

        output_file = base_subtitle.file_path.rsplit('.', 1)[0] + '_combined.srt'
        logger.info(f"Saving merged subtitle to {output_file}")
        new_subtitle.save(output_file)
        logger.info("Merge completed successfully")

    def __find_closest_subtitle(self, base_subtitle_entry: SubtitleEntry, target_subtitle_entries: List, tolerance: int = 1) -> Optional[SubtitleEntry]:
        for entry in target_subtitle_entries:
            if entry["timestamp"].startswith(base_subtitle_entry.timestamp):
                logger.debug(f"Exact timestamp match found: {entry['timestamp']}")
                return entry
            start_time, end_time = base_subtitle_entry.timestamp.split(' --> ')
            start_time_seconds = self.__timestamp_to_seconds(start_time)
            end_time_seconds = self.__timestamp_to_seconds(end_time)

            target_start_time, target_end_time = entry["timestamp"].split(' --> ')
            target_start_seconds = self.__timestamp_to_seconds(target_start_time)
            target_end_seconds = self.__timestamp_to_seconds(target_end_time)

            if abs(target_start_seconds - start_time_seconds) <= tolerance or abs(target_end_seconds - end_time_seconds) <= tolerance:
                logger.debug(f"Close timestamp match found within tolerance: base {base_subtitle_entry.timestamp}, target {entry['timestamp']}")
                return entry

        logger.debug(f"No close subtitle found for timestamp {base_subtitle_entry.timestamp}")
        return None

    def __timestamp_to_seconds(self, timestamp: str) -> float:
        h, m, s_ms = timestamp.split(":")
        s, ms = s_ms.split(",")
        total_seconds = int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        logger.debug(f"Converted timestamp {timestamp} to seconds: {total_seconds}")
        return total_seconds
