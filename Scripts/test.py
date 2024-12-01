from flask import Flask
from flask import request
from flask import json
import sqlite3
import requests as rq
import datetime
from markupsafe import escape

app = Flask(__name__)

# Database is named songs. (Housed in songData.db) 

def songDataCreator(jsonSongData):
    timeOfSubmission = datetime.datetime.today().strftime('%a %d %b %Y')
    cover = jsonSongData['tracks']['items'][0]['album']['images'][0]['url'] # Album Cover
    artistName = jsonSongData['tracks']['items'][0]['artists'][0]['name'] # Artist Name
    songName = jsonSongData['tracks']['items'][0]['name'] # Song Name
    
    # Columns respectively are date, cover, artist, song
    songInfo = [(timeOfSubmission, cover, artistName, songName)]

    songDatabase = sqlite3.connect('../Database/songData.db')
    songDatabaseCursor = songDatabase.cursor()
        
    # Checks if song data already exists for current day. If it does it replaces data, if not, new data is pushed.    
    if songDatabaseCursor.execute('SELECT date FROM songs WHERE date=?', (timeOfSubmission, )).fetchone()[0] == ():
        songDatabaseCursor.executemany("INSERT INTO songs VALUES(?, ?, ?, ?)", songInfo)
    else: 
        songDatabaseCursor.executemany("UPDATE songs SET date=?, cover=?, artist=?, song=?", songInfo)

    songDatabase.commit()
    songDatabase.close()


@app.route("/")
def homePage():
    currentDate = datetime.datetime.today().strftime('%a %d %b %Y')
    songDatabaseConnection = sqlite3.connect('../Database/songData.db')
    databaseCursur = songDatabaseConnection.cursor()
    coverArt = databaseCursur.execute("SELECT cover FROM songs WHERE date=?", (currentDate, )).fetchone()[0]
    songName = databaseCursur.execute("SELECT song FROM songs WHERE date=?", (currentDate, )).fetchone()[0]
    artistName = databaseCursur.execute("SELECT artist FROM songs WHERE date=?", (currentDate, )).fetchone()[0]
    songDatabaseConnection.close()
    return f'''
<!DOCTYPE html>
<html>
    <head>
        <link href={app.url_for('static', filename='style.css')} rel="stylesheet" type="text/css">
        <script src={app.url_for('static', filename='listener.js')} rel="script" defer></script>
    </head>
    <body>
        <div class="topRow">
            <div id="Logo"><img src={app.url_for('static', filename='LSTNLogo.png')}></div>
            <div class="buttonAbout"><h2>About</h2></div>
        </div>
        <div class="albumCover">
            <img src={coverArt}>
        </div>
        <div class="songName">
            <h1>{songName}</h1>
        </div>
        <div class="artistName">
            <h1>{artistName}</h1>
        </div>
    </body>
</html>'''


@app.route("/about")
def aboutPage():
    return f'''
<!DOCTYPE html>
<html>
    <head>
        <link href={app.url_for('static', filename='style.css')} rel='stylesheet' type='text/css'>
        <script src={app.url_for('static', filename='returnHome.js')} rel="script" defer></script>
    </head>
    <body>
        <div class="topRow">
            <div id="Logo"><img src={app.url_for('static', filename='LSTNLogo.png')}></div>
            <div class="buttonHome"><h2>Home</h2></div>
        </div>
        <div class='info'>
            <h1>Welcome to LSTN 365!</h1>
            <h3>This website is still in heavy development, and it will be a long while before it is finished.</h3>
            <p>For now you can check back daily to see the song of the day.</p>
        </div>
    </body>
</html>'''

@app.route("/submit", methods=['GET', 'POST'])
def submitSongPage():
    if request.method == 'GET':
        return '''<!DOCTYPE html>
    <html>
        <body>
            <div>
                <h1>Submit A Song!</h1>
                <h3>Type in song info to disply on the main page.</h3>
                <br>
                <form id="formBox" method="POST" action="/submit">
                    <input type="text" name="songName">
                    <input type="submit">
                </form>
            </div>
        </body>
    </html>'''
    if request.method == 'POST':
        formSongName = request.form['songName']
        spotifyTknResponse = rq.request('POST', "https://accounts.spotify.com/api/token", headers={'Content-Type': 'application/x-www-form-urlencoded'}, data={'grant_type': 'client_credentials', 'client_id': 'c7d9495ec7594f308487294cffd68249', 'client_secret': '6bb70d812e204fdd996cd894969e0da8'})
        token = spotifyTknResponse.json()['access_token']
        songResponse = rq.request('GET', 'https://api.spotify.com/v1/search', params={'q' : formSongName, 'type': 'track'}, headers={'Authorization': f'Bearer {token}'})
        songResponseJson = songResponse.json()
        songDataCreator(songResponseJson)
        return app.redirect('/')

