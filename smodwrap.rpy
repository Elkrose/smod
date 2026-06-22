# Sound Mod

init python:

    def get_mp3_playlist(directory="audio/bgm"):
        # Scans a directory for MP3 files and returns a list of paths.
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

    if not hasattr(store, 'smod_last_hub_name'):
        store.smod_last_hub_name = None    
    if not hasattr(store, 'smod_last_room_name'):
        store.smod_last_room_name = None
    if not hasattr(store, 'smod_target_playlist'):
        store.smod_target_playlist = None
    if not hasattr(store, 'smod_last_song'):
        store.smod_last_song = None
    if not hasattr(store, 'smod_current_playlist'):
        store.smod_current_playlist = None
    if not hasattr(store, 'smod_playlist_index'):
        store.smod_playlist_index = 0

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

            # Determine target_playlist for this location
            target_playlist = get_playlist_for_location(current_room, current_hub)

            # If target_playlist is None, no music for this location
            if target_playlist is None:
                return

            # Only update and play music if playlist changed
            # Compare by content (list equality works for this)
            if store.smod_target_playlist != target_playlist:
                renpy.music.stop(channel='music', fadeout=1.0)
                store.smod_current_playlist = target_playlist
                store.smod_last_song = None
                store.smod_last_room_name = current_room
                store.smod_last_hub_name = current_hub
                store.smod_target_playlist = target_playlist
                play_location_music(target_playlist)
            else:
                store.smod_last_room_name = current_room
                store.smod_last_hub_name = current_hub

            # Call your player function
            #play_location_music(target_playlist)
        except:
            # If anything goes wrong (mod removed, error in logic), fail silently
            pass

    def get_playlist_for_location(room_name, hub_name):
        # Helper to determine which playlist a room belongs to
        
        # Specific to ROOM
        # if room_name == "mc_bedroom":
            # return home_playlist
        # elif room_name in ["office", "lobby", "main_office", "rd_div", "ceo_office", "market_div", "prod_div"]:
            # return lab_playlist
        # elif room_name in ["home_hall", "kitchen", "mom_bedroom", "lily_bedroom"]:
            # return home_playlist
        # elif room_name == "bar":
            # return bar_playlist
        # elif room_name == "stripclub":
            # return strip_playlist
        # elif room_name in ["university", "campus"]:
            # return uni_playlist
        # elif hub_name in ["uni_home", "industrial"]:
            # return uni_playlist
        # elif room_name in ["park_hub", "park"]:
            # return park_playlist
        # elif room_name in ["downtown", "coffee_shop", "hotel_lobby", "hospital"]:
            # return downtown_playlist

        # Specific to HUB
        if hub_name in ["home", "Home", "home_hall"]:
            if room_name == "dungeon":
                return strip_playlist
            elif room_name in ["bathroom", "home_shower", "laundry_room"]:
                return park_playlist
            else:
                return home_playlist
        elif hub_name == "aunt_home":
            return home_playlist
        elif hub_name == "office":
            if room_name == "break_room":
                return park_playlist
            elif room_name in ["work_bathroom", "storage_room"]:
                return strip_playlist
            else:
                return lab_playlist
        elif hub_name == "mall":
            if room_name in ["gaming_cafe_store_room", "mall_bathroom", "changing_room"]:
                return strip_playlist
            elif room_name == "gaming_cafe":
                return home_playlist
            else:
                return downtown_playlist
        elif hub_name == "sex_shop":
            return strip_playlist
        elif hub_name == "downtown":
            if room_name in ["bar", "coffee_shop", "bar_bathroom", "hotel_room"]:
                return bar_playlist
            elif room_name in ["hotel_lobby", "fancy_restaurant", "mom_office_lobby", "mom_office", "hospital", "hospital_room"]:
                return park_playlist
            else:
                return downtown_playlist
        elif hub_name == "plaza":
            return downtown_playlist
        elif hub_name == "gym":
            return park_playlist
        elif hub_name == "university":
            if room_name in ["study_room", "university_bathroom"]:
                return strip_playlist
            else:
                return uni_playlist
        elif hub_name == "mansion":
            return home_playlist            
        elif hub_name == "stripclub":
            return strip_playlist
        elif hub_name == "residential":
            return home_playlist
        elif hub_name == "industrial":
            return home_playlist
        elif hub_name == "downtown_home":
            return home_playlist
        elif hub_name == "uni_home":
            return home_playlist
        elif hub_name in ["park_hub", "park"]:
            return park_playlist          
        return None  # No playlist defined for this room

    def play_location_music(target_playlist):
        store.smod_current_playlist = target_playlist
        
        if not target_playlist or len(target_playlist) == 0:
            return

        current_track = renpy.music.get_playing(channel='music')
        if current_track and current_track not in target_playlist:
            renpy.music.stop(fadeout=1.0)
        
        # Pick random start
        store.smod_playlist_index = random.randint(0, len(target_playlist) - 1)
        
        # Play first track
        first_track = target_playlist[store.smod_playlist_index]
        renpy.music.play(first_track, channel='music', loop=False, fadein=1.0)
        
        # Queue up the next 10 tracks (they play automatically when each ends)
        for i in range(1, 11):
            idx = (store.smod_playlist_index + i) % len(target_playlist)
            renpy.music.queue(target_playlist[idx], channel='music')
        
        store.smod_last_song = first_track

init 101 python:
    # Hijack the start label to run our initialization code
    add_label_hijack("normal_start", "smod_hook")
    add_label_hijack("game_loop", "smod_change_location")

label smod_hook(stack):
    python:
        check_music()
        execute_hijack_call(stack)
    return

label smod_change_location(stack):
    python:
        check_music()
        execute_hijack_call(stack)
    return
