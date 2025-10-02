from typing import List, Tuple
from models.subtitle import Subtitle
from models.subtitle import SubtitleEntry
from utils.logger import logger  # your custom logger import

class SubtitleParser:

    def __init__(self):
        logger.info("SubtitleParser initialized")
    
    def parse_srt_file(self, file_path: str) -> Subtitle:
        logger.info(f"Parsing SRT file: {file_path}")
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                file_array = file.readlines()
        except Exception as e:
            logger.error(f"Failed to read file '{file_path}': {e}")
            raise
        
        indexes, timestamps, subtitles = self.__extract_subtitles(file_array)
        logger.debug(f"Extracted {len(indexes)} indexes, {len(timestamps)} timestamps, and {len(subtitles)} subtitles")
        
        entries = []
        for i in range(len(indexes)):
            entry=SubtitleEntry(index=indexes[i],timestamp=timestamps[i] if i < len(timestamps) else '',text=subtitles[i] if i < len(subtitles) else '')
            entries.append(entry)
        
        subtitle = Subtitle(file_path=file_path, format='srt')
        subtitle.entries = entries
        logger.info(f"Completed parsing '{file_path}', total entries: {len(entries)}")
        return subtitle
    
    def __extract_subtitles(self, file_array: List[str]) -> Tuple[List[int], List[str], List[str]]:
        indexes = []
        timestamps = []
        subtitles = []
        current_subtitle = []
        
        logger.debug("Beginning subtitle extraction from file lines")
        for line in file_array:
            line = line.strip()
            if not line:
                continue
            if line.isdigit():
                if current_subtitle:
                    subtitles.append('\n'.join(current_subtitle))
                    logger.debug(f"Added subtitle block: {subtitles[-1][:30]}...")
                    current_subtitle = []
                indexes.append(int(line))
                logger.debug(f"Found subtitle index: {line}")
            elif '-->' in line:
                timestamps.append(line)
                logger.debug(f"Found timestamp line: {line}")
            else:
                current_subtitle.append(line)
        
        if current_subtitle:
            subtitles.append('\n'.join(current_subtitle))
            logger.debug(f"Added final subtitle block: {subtitles[-1][:30]}...")
        
        logger.debug(f"Extraction done: {len(indexes)} indexes, {len(timestamps)} timestamps, {len(subtitles)} subtitle blocks")
        return indexes, timestamps, subtitles

