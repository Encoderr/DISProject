import psycopg2
import os
import csv

# Try to get from system environment variable
user = os.environ.get('PGUSER', 'postgres')
password = os.environ.get('PGPASSWORD', 'abc123')
host = os.environ.get('HOST', '127.0.0.1')

def db_connection():
    db = "dbname='spotify_emotions' user=" + user + " host=" + host + " password=" + password
    try:
        conn = psycopg2.connect(db)
        return conn
    except psycopg2.Error as e:
        print(f"Unable to connect to database: {e}")
        raise

def init_db():
    conn = db_connection()
    cur = conn.cursor()
    
    # Create tables
    cur.execute('''CREATE TABLE IF NOT EXISTS emotions (
                id SERIAL PRIMARY KEY,
                emotion_name TEXT NOT NULL UNIQUE
                )''')
    
    cur.execute('''CREATE TABLE IF NOT EXISTS songs (
                id SERIAL PRIMARY KEY,
                artist TEXT NOT NULL,
                title TEXT NOT NULL,
                emotion TEXT NOT NULL,
                valence FLOAT,
                genre TEXT,
                year INTEGER,
                key TEXT,
                tempo FLOAT,
                UNIQUE(artist, title)
            )''')
    
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_songs_emotion 
                   ON songs(emotion)''')
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_songs_artist 
                   ON songs(artist)''')
    cur.execute('''CREATE INDEX IF NOT EXISTS idx_songs_genre 
                   ON songs(genre)''')
    
    conn.commit()

    # First populate emotions table
    emotions = set()
    try:
        with open('light_spotify_dataset.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                emotions.add(row['emotion'])
        
        for emotion in emotions:
            cur.execute('''
                INSERT INTO emotions (emotion_name)
                VALUES (%s)
                ON CONFLICT (emotion_name) DO NOTHING
            ''', (emotion,))
        conn.commit()
    except Exception as e:
        print(f"Error populating emotions: {e}")
        conn.rollback()

    # Then populate songs table
    try:
        with open('light_spotify_dataset.csv', 'r') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                try:
                    # Handle BOM character in CSV
                    artist = row['\ufeffartist'] if '\ufeffartist' in row else row['artist']
                    
                    # Map CSV columns to correct names
                    valence = float(row['variance']) if row['variance'] and row['variance'] != 'NA' else None
                    year = int(row['Release Date']) if row['Release Date'] and row['Release Date'] != 'NA' else None
                    tempo = float(row['Tempo']) if row['Tempo'] and row['Tempo'] != 'NA' else None
                    genre = row['Genre'] if 'Genre' in row else None
                    key = row['Key'] if 'Key' in row else None
                    title = row['song'] if 'song' in row else None

                    if not all([artist, title]):
                        print(f"Skipping row due to missing required fields: {row}")
                        continue

                    cur.execute('''
                        INSERT INTO songs (artist, title, emotion, valence, genre, year, key, tempo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (artist, title) DO NOTHING
                    ''', (
                        artist,
                        title,
                        row['emotion'],
                        valence,
                        genre,
                        year,
                        key,
                        tempo
                    ))
                except (ValueError, KeyError) as e:
                    print(f"Error processing row: {row}")
                    print(f"Error details: {e}")
                    continue
            conn.commit()
    except Exception as e:
        print(f"Error populating songs: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
    
