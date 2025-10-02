from pydantic import BaseModel
from typing import List, Optional
from models.subtitle import Subtitle


class MediaItem(BaseModel):
    name: str
    path: str
    subtitles: List[Subtitle]

class Movie(MediaItem):
    pass

class Episode(MediaItem):
    pass

class Season(BaseModel):
    name: str
    episodes: List[Episode] = []

    def add_episode(self, episode: Episode):
        self.episodes.append(episode)

class TVShow(BaseModel):
    name: str
    seasons: List[Season] = []

    def add_season(self, season: Season):
        self.seasons.append(season)

class Library(BaseModel):
    movies: List[Movie] = []
    tv_shows: List[TVShow] = []

    def add_movie(self, movie: Movie):
        self.movies.append(movie)

    def add_tv_show(self, tv_show: TVShow):
        self.tv_shows.append(tv_show)
