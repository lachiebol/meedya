
from models.media_item import Library
from services.subtitle_merger import SubtitleMerger
from services.subtitle_parser import SubtitleParser
from services.file_parser import FileParser

from pprint import pprint


def main():
    library=Library(movies=[],tv_shows=[])
    parser = SubtitleParser()
    file_parser= FileParser(library,parser)

    file_parser.parse(r'/mnt/f/TV')


    subtitle_merger = SubtitleMerger()

    movies=library.movies


    tv_shows=library.tv_shows
    
    for tv_show in tv_shows:
        seasons=tv_show.seasons
        for season in seasons:
            episodes=season.episodes
            for episode in episodes:
                
                # We have two subtitles
                if(len(episode.subtitles)==2):
                    print('we have two')
                    print(episode)
                    subtitle_merger.merge(episode.subtitles[0], episode.subtitles[1])






main()
