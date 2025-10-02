from collections import defaultdict
import os
import re
from typing import DefaultDict, TypedDict, Dict, Optional, Tuple
from models.media_item import Episode, Library, Movie, Season, TVShow
from services.subtitle_parser import SubtitleParser
from utils.logger import logger

class ContentEntry(TypedDict):
    video: Optional[str]
    subtitles: Dict[str, str]

class FileParser:
    def __init__(self, library: Library,subtitle_parser: SubtitleParser) -> None:
        self.library=library
        self.subtitle_parser=subtitle_parser

    def parse(self, directory: str):
        files = os.listdir(directory)
        for file in files:
            path = rf"{directory}/{file}"
            if not os.path.isdir(path):
                logger.debug(f"Skipping {file}, not a directory.")
                continue

            if(self.__is_tv_show_folder(path)):
                tv_show = TVShow(name=file,seasons=[])
                self.__process_tv_show(path,file)
                pass
            else:
                self.__process_movie(path,file)
            
                # Is Movie


    def __process_tv_show(self, path: str, tv_show_name: str):
        
        tv_show=TVShow(name=tv_show_name,seasons=[])
        self.library.add_tv_show(tv_show)

        # If a TV show, then we can assume the next level of folders are seasons.

        seasons = os.listdir(path)
        for season_name in seasons:

            season = Season(name=season_name,episodes=[])
            tv_show.add_season(season)

            season_path = rf"{path}/{season_name}"
            content = self.__find_content(season_path)
            for episode, data in content.items():
                subtitles=[]
                video_path=f"{season_path}/{data['video']}"
                for _,subtitle_file in data['subtitles'].items():
                    subtitle=self.subtitle_parser.parse_srt_file(subtitle_file)
                    subtitles.append(subtitle)

                episode = Episode(name=episode,path=video_path,subtitles=subtitles)
                season.add_episode(episode)

    
    def __process_movie(self, path: str, movie_name: str):
        content=self.__find_content(path)  

        subtitles=[]
        for _, data in content.items():
            for _,subtitle_file in data['subtitles']:
                subtitle=self.subtitle_parser.parse_srt_file(subtitle_file)
                subtitles.append(subtitle)

            movie = Movie(name=movie_name,path=path,subtitles=subtitles)
            
            self.library.add_movie(movie)




    def __is_tv_show_folder(self, folder_path: str) -> bool:
        for entry in os.scandir(folder_path):
            if entry.is_dir():
                return True
        return False
    
    def __find_content(self, path: str, video_exts: Tuple=(".mkv", ".mp4", ".avi"), sub_ext: str=".srt") -> DefaultDict[str, ContentEntry]:
        content: DefaultDict[str, ContentEntry] = defaultdict(
            lambda: {"video": None, "subtitles": {}}
        )


        for filename in os.listdir(path):
            lower = filename.lower()
            name, ext = os.path.splitext(filename)

            if ext in video_exts:
                content[name]["video"] = filename
                continue

            if lower.endswith(sub_ext):
                match = re.match(r"(.+?)\.((?:\w+\.)*\w+)\.srt", filename)
                if match:
                    stem, lang_tag = match.groups()
                    content[stem]["subtitles"][lang_tag] = f"{path}/{filename}"

        return content






