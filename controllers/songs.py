from flask import Blueprint, render_template, request
from models.songs import Song

bp = Blueprint('songs', __name__)

@bp.route('/songs')
def index():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    emotion = request.args.get('emotion', '')
    genre = request.args.get('genre', '')
    sort = request.args.get('sort', 'artist')
    
    songs, total = Song.search(
        search=search,
        emotion=emotion,
        genre=genre,
        sort=sort,
        page=page
    )
    
    # Get unique emotions and genres for dropdowns
    emotions = Song.get_unique_emotions()
    genres = Song.get_unique_genres()
    
    total_pages = (total + 49) // 50

    return render_template('songs.html',
                         songs=songs,
                         current_page=page,
                         total_pages=total_pages,
                         search=search,
                         emotions=emotions,
                         genres=genres,
                         selected_emotion=emotion,
                         selected_genre=genre,
                         sort=sort)
