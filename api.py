from fastapi import FastAPI, HTTPException, Query
from typing import List

from models.media_item import Library, TVShow, Season, Episode, Movie, Subtitle
from services.subtitle_parser import SubtitleParser
from services.file_parser import FileParser

api = FastAPI()

from fastapi.middleware.cors import CORSMiddleware
api.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

library = Library(movies=[], tv_shows=[])

subtitle_parser = SubtitleParser()
file_parser = FileParser(library, subtitle_parser)

file_parser.parse(r'/mnt/f/TV')


@api.get("/movies", response_model=List[Movie])
def list_movies(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    return library.movies[skip: skip + limit]


@api.get("/tvshows", response_model=List[TVShow])
def list_tv_shows(skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    return library.tv_shows[skip: skip + limit]


@api.get("/tvshows/{tvshow_name}/seasons", response_model=List[Season])
def list_seasons(tvshow_name: str, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    tvshow = next((show for show in library.tv_shows if show.name == tvshow_name), None)
    if not tvshow:
        raise HTTPException(status_code=404, detail="TV Show not found")
    return tvshow.seasons[skip: skip + limit]


@api.get("/tvshows/{tvshow_name}/seasons/{season_name}/episodes", response_model=List[Episode])
def list_episodes(tvshow_name: str, season_name: str, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    tvshow = next((show for show in library.tv_shows if show.name == tvshow_name), None)
    if not tvshow:
        raise HTTPException(status_code=404, detail="TV Show not found")

    season = next((s for s in tvshow.seasons if s.name == season_name), None)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    return season.episodes[skip: skip + limit]



@api.get("/episodes/{episode_name}/subtitles", response_model=List[Subtitle])
def list_subtitles(episode_name: str, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    for tvshow in library.tv_shows:
        for season in tvshow.seasons:
            for episode in season.episodes:
                if episode.name == episode_name:
                    return episode.subtitles[skip: skip + limit]
    raise HTTPException(status_code=404, detail="Episode not found")


@api.get("/movies/{movie_name}/subtitles", response_model=List[Subtitle])
def list_movie_subtitles(movie_name: str, skip: int = Query(0, ge=0), limit: int = Query(10, ge=1)):
    movie = next((m for m in library.movies if m.name == movie_name), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie.subtitles[skip: skip + limit]
