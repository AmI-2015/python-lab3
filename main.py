from flask import Flask
from flask import render_template, request, url_for
from werkzeug import redirect

from yamp import TrackList, Track, Player


app = Flask(__name__)
# the folder that stores the music files
folder = '/home/derussis/Music'
# create a track list
track_list = TrackList()
# create a player
player = Player()

@app.route('/')
def index():
    return render_template('index.html', tracks=track_list.tracks)

@app.route('/tracks/<int:id>')
def show(id):
    # get the track
    track = track_list.tracks[id]
    return render_template('show.html', track=track)

@app.route('/tracks/<int:id>/play', methods=['POST'])
def play(id):
    # get the path of the desired track
    path = track_list.tracks[id].path
    # play the song
    player.play(path)
    return redirect(url_for('show', id=id))

@app.route('/tracks/<id>/stop', methods=['POST'])
def stop(id):
    # stop the player
    player.stop()
    return redirect(url_for('show', id=id))

if __name__ == '__main__':
    # get the list of tracks from the given folder
    track_list.addTracks(track_list.scan(folder))
    app.run(debug=True)
