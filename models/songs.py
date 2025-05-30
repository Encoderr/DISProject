from database import db_connection

class Song:
    def __init__(self, id, artist, title, emotion, valence, genre, year, key, tempo):
        self.id = id
        self.artist = artist
        self.title = title
        self.emotion = emotion
        self.valence = valence
        self.genre = genre
        self.year = year
        self.key = key
        self.tempo = tempo

    @staticmethod
    def get_all(page=1, per_page=50):
        conn = db_connection()
        cur = conn.cursor()
        offset = (page - 1) * per_page
        
        cur.execute('''
            SELECT * FROM songs 
            ORDER BY artist, title
            LIMIT %s OFFSET %s
        ''', (per_page, offset))
        
        songs = [Song(*row) for row in cur.fetchall()]
        
        # Get total count
        cur.execute('SELECT COUNT(*) FROM songs')
        total = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return songs, total

    @staticmethod
    def get_by_emotion(emotion, page=1, per_page=50):
        conn = db_connection()
        cur = conn.cursor()
        offset = (page - 1) * per_page
        
        cur.execute('''
            SELECT * FROM songs 
            WHERE emotion = %s
            ORDER BY artist, title
            LIMIT %s OFFSET %s
        ''', (emotion, per_page, offset))
        
        songs = [Song(*row) for row in cur.fetchall()]
        
        # Get filtered count
        cur.execute('SELECT COUNT(*) FROM songs WHERE emotion = %s', (emotion,))
        total = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return songs, total
    @staticmethod
    def search(search='', emotion='', genre='', sort='artist', page=1, per_page=50):
        conn = db_connection()
        cur = conn.cursor()
        
        query = '''
            SELECT * FROM songs 
            WHERE 1=1
        '''
        params = []
        
        if search:
            query += ''' AND (
                artist ILIKE %s 
                OR title ILIKE %s
            )'''
            search_term = f'%{search}%'
            params.extend([search_term, search_term])
        
        if emotion:
            query += ' AND emotion = %s'
            params.append(emotion)
        
        if genre:
            query += ' AND genre = %s'
            params.append(genre)
        
        query += f' ORDER BY {sort}'
        
        offset = (page - 1) * per_page
        query += ' LIMIT %s OFFSET %s'
        params.extend([per_page, offset])
        
        cur.execute(query, params)
        songs = [Song(*row) for row in cur.fetchall()]
        
        # Get total count with same filters
        count_query = f'''
            SELECT COUNT(*) FROM songs 
            WHERE 1=1
            {' AND (artist ILIKE %s OR title ILIKE %s)' if search else ''}
            {' AND emotion = %s' if emotion else ''}
            {' AND genre = %s' if genre else ''}
        '''
        count_params = []
        if search:
            count_params.extend([f'%{search}%', f'%{search}%'])
        if emotion:
            count_params.append(emotion)
        if genre:
            count_params.append(genre)
        
        cur.execute(count_query, count_params)
        total = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        return songs, total

    @staticmethod
    def get_unique_emotions():
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT emotion FROM songs ORDER BY emotion')
        emotions = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return emotions

    @staticmethod
    def get_unique_genres():
        conn = db_connection()
        cur = conn.cursor()
        cur.execute('SELECT DISTINCT genre FROM songs ORDER BY genre')
        genres = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        return genres
