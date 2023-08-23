from flask import render_template, url_for, flash, redirect, request, abort
from music import app, db, bcrypt
from music.forms import RegistrationForm, LoginForm, PlaylistForm, SongForm
from music.models import User, Playlist, Song
from flask_login import login_user, current_user, logout_user, login_required


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = User(name=form.name.data, email=form.email.data, password_hash=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You can now log in.", "success")
        return redirect(url_for("login"))
    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))
        else:
            flash("Login unsuccessful. Please check email and password.", "danger")
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


@app.route("/all_songs")
@login_required
def all_songs():
    user_playlists = Playlist.query.filter_by(user=current_user).all()
    all_songs = []

    for playlist in user_playlists:
        all_songs.extend(playlist.songs)

    return render_template("all_songs.html", songs=all_songs)


@app.route("/playlists")
@login_required
def playlists():
    user_playlists = Playlist.query.filter_by(user=current_user).all()
    return render_template("playlists.html", playlists=user_playlists)



@app.route("/playlist/<int:playlist_id>")
@login_required
def playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    songs = Song.query.filter_by(playlist=playlist).all()
    return render_template("playlist.html", playlist=playlist, songs=songs)


@app.route("/create_playlist", methods=["GET", "POST"])
@login_required
def create_playlist():
    form = PlaylistForm()
    if form.validate_on_submit():
        new_playlist = Playlist(name=form.name.data, band=form.band.data, genre=form.genre.data, user=current_user)
        db.session.add(new_playlist)
        db.session.commit()
        flash("Playlist created successfully!", "success")
        return redirect(url_for("playlists"))
    return render_template("create_playlist.html", form=form)


# ... (Other routes and views)

@app.route("/edit_playlist/<int:playlist_id>", methods=["GET", "POST"])
@login_required
def edit_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    form = PlaylistForm()
    if form.validate_on_submit():
        playlist.name = form.name.data
        playlist.band = form.band.data
        playlist.genre = form.genre.data
        db.session.commit()
        flash("Playlist updated successfully!", "success")
        return redirect(url_for("playlists"))
    elif request.method == "GET":
        form.name.data = playlist.name
        form.band.data = playlist.band
        form.genre.data = playlist.genre
    return render_template("edit_playlist.html", form=form, playlist=playlist)


@app.route("/delete_playlist/<int:playlist_id>", methods=["POST"])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)

    if playlist.user != current_user:
        abort(403)  # User doesn't have permission to delete this playlist

    # Delete the associated songs
    for song in playlist.songs:
        db.session.delete(song)

    # Delete the playlist
    db.session.delete(playlist)
    db.session.commit()

    flash("Playlist and its songs deleted successfully!", "success")
    return redirect(url_for("playlists"))




@app.route("/add_song/<int:playlist_id>", methods=["GET", "POST"])
@login_required
def add_song(playlist_id):
    playlist = Playlist.query.get_or_404(playlist_id)
    form = SongForm()
    if form.validate_on_submit():
        new_song = Song(name=form.name.data, scale=form.scale.data, tempo=form.tempo.data,
                        original_artist=form.original_artist.data, genre=form.genre.data, playlist=playlist,
                        user=current_user)
        db.session.add(new_song)
        db.session.commit()
        flash("Song added successfully!", "success")
        return redirect(url_for("playlist", playlist_id=playlist.id))
    return render_template("add_song.html", form=form, playlist=playlist)


@app.route("/delete_song/<int:song_id>", methods=["GET", "POST"])
@login_required
def delete_song(song_id):
    song = Song.query.get_or_404(song_id)
    if song.playlist.user != current_user:
        abort(403)  # User doesn't have permission to delete this song
    db.session.delete(song)
    db.session.commit()
    flash("Song deleted successfully!", "success")
    return redirect(url_for("playlist", playlist_id=song.playlist.id))


from flask import render_template



@app.route("/edit_song/<int:song_id>", methods=["GET", "POST"])
@login_required
def edit_song(song_id):
    song = Song.query.get_or_404(song_id)
    form = SongForm()
    if form.validate_on_submit():
        song.name = form.name.data
        song.scale = form.scale.data
        song.tempo = form.tempo.data
        song.original_artist = form.original_artist.data
        song.genre = form.genre.data
        db.session.commit()
        flash("Song updated successfully!", "success")
        return redirect(url_for("playlist", playlist_id=song.playlist.id))
    elif request.method == "GET":
        form.name.data = song.name
        form.scale.data = song.scale
        form.tempo.data = song.tempo
        form.original_artist.data = song.original_artist
        form.genre.data = song.genre
    return render_template("edit_song.html", form=form)

# More routes for song creation, editing, and deletion can be added here