# Sound Mod

init python:
    
    def get_mp3_playlist(directory="audio/bgm"):
        """Scans a directory for MP3 files and returns a list of paths."""
        playlist = []
        # renpy.list_files() lists files in the game directory and archives
        for filename in renpy.list_files(common=False):
            if directory in filename and filename.endswith(".mp3"):
                playlist.append(filename)
        return playlist
    
    
    # Define a variable holding the list of all found music files
    bar_playlist = get_mp3_playlist(directory="mods/smod/music/bar_music")
    downtown_playlist = get_mp3_playlist(directory="mods/smod/music/downtown_music")
    home_playlist = get_mp3_playlist(directory="mods/smod/music/home_music")
    lab_playlist = get_mp3_playlist(directory="mods/smod/music/lab_music")
    park_playlist = get_mp3_playlist(directory="mods/smod/music/park_music")
    strip_playlist = get_mp3_playlist(directory="mods/smod/music/strip_music")
    uni_playlist = get_mp3_playlist(directory="mods/smod/music/university_music")
    
    if not hasattr(store, 'smod_last_room_name'):
            store.smod_last_room_name = None
            
    def smod_notify(message, duration=3.0):
        """Custom VT notification with styled popup"""
        # First hide any existing VT notification        
        renpy.hide_screen("smod_notification")
        # Show our styled notification
        renpy.show_screen("smod_notification", message=message, duration=duration)  

    # 2. Define the check function
    # We use try/except to ensure that if the mod is removed, the game doesn't crash.
    # It will just stop playing dynamic music.
    def check_music():
        try:
            # If mc or location doesn't exist (e.g. main menu), stop
            if not mc or not hasattr(mc, 'location') or mc.location is None:
                return

            current_room = mc.location.name
            current_hub = ""
            if hasattr(mc, 'current_location_hub') and mc.current_location_hub:
                current_hub = mc.current_location_hub.name

            location_id = current_room

            # If we are already in this room, do nothing
            if store.smod_last_room_name == location_id:
                return

            # Room changed, update tracker and play music
            store.smod_last_room_name = location_id
            
            # Call your player function
            play_location_music(current_room)
        except:
            # If anything goes wrong (mod removed, error in logic), fail silently
            pass


screen smod_notification(message, duration=3.0):
    modal False
    zorder 100
    
    frame:
        style "smod_frame"
        xalign 0.5
        yalign 0.15
        padding (20, 15)
        
        text message:
            style "smod_notify_text"
            text_align 0.5
    
    timer duration action Hide("smod_notification")

style smod_frame:
    background "#3c0606"  # Dark purple-black background
    size 28

style smod_notify_text:
    color "#ffccff"       # Pinkish-white text
    size 24
    slow_cps 0

init python:
    # Hijack the start label to run our initialization code
    add_label_hijack("normal_start", "smod_hook")
    add_label_hijack("change_location", "smod_hook")

label smod_hook(*args, **kwargs):
    python:

        check_music()

    return

# 4. Define your music logic using the playlists defined earlier
init python:
    def play_location_music(room_name):
        # room_name is now just a string (e.g. "lobby")
        dest_name = room_name
        hub_name = ""

        # We need to find the Hub Name manually since we only have the room name string
        # We have to look it up from mc
        try:
            if mc and hasattr(mc, 'current_location_hub') and mc.current_location_hub:
                hub_name = mc.current_location_hub.name
        except:
            pass
        # 2. Logic to map locations to your playlists
        # We determine which playlist to use based on the room name
        target_playlist = []
        
        if dest_name == "mc_bedroom":
            target_playlist = home_playlist
        elif dest_name in ["office", "lobby", "main_office", "rd_div", "ceo_office", "market_div", "prod_div"]:
            target_playlist = lab_playlist
        elif dest_name in ["home_hall", "kitchen", "mom_bedroom", "lily_bedroom"]:
            target_playlist = home_playlist
        elif dest_name == "bar":
            target_playlist = bar_playlist
        elif dest_name == "stripclub":
            target_playlist = strip_playlist
        elif dest_name in ["university", "campus"]:
            target_playlist = uni_playlist
        elif hub_name in ["uni_home", "industrial"]:
            target_playlist = uni_playlist
        elif dest_name in ["park_hub", "park"]:
            target_playlist = park_playlist
        elif dest_name in ["downtown", "coffee_shop", "hotel_lobby", "hospital"]:
            target_playlist = downtown_playlist

        # 3. Check if we found a valid playlist and if it has songs
        if not target_playlist:
            return

        # 4. Check if we need to stop the current music
        # We check if the currently playing track is in the NEW playlist.
        # If not (e.g., we are leaving the Lab to go Home), we stop the music first.
        current_track = renpy.music.get_playing(channel='music')
        should_stop = False
        
        if current_track and current_track not in target_playlist:
            should_stop = True

        # 5. Play the music
        try:
            if should_stop:
                renpy.music.stop(fadeout=1.0)
            
            # Pick a random track from the playlist
            # Using the standard 'random' module
            next_track = random.choice(target_playlist)
            
            # Extract the song name from the full path
            # Example: "mods/smod/music/bar_music/song.mp3" -> "song.mp3"
            song_name = next_track.split("/")[-1].replace(".mp3", "")
            # Remove the .mp3 extension and escape special characters
            song_name_escaped = song_name.replace("{", "{{").replace("}", "}}")
            
            # Play the chosen track
            renpy.music.play(next_track, loop=True, fadein=1.0)

            # Debugging (Optional: comment this out later)
            #smod_notify("Now Playing: " + dest_name, duration=2.0)
            smod_notify("{q}Now Playing: {}{/q}".format(song_name_escaped), duration=2.0)

        except Exception as e:
            print(f"SMod Music Error: {e}")
    