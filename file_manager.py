import os
import sys
import vlc
import time
import subprocess


# Global state
player = None
playlist = []
current_index = -1


def is_media_file(filepath):
    """Check if file is audio/video supported by VLC."""
    media_exts = (".mp4", ".mkv", ".avi", ".mp3", ".wav", ".mov", ".flac")
    return filepath.lower().endswith(media_exts)


def open_file(path):
    """Open file or folder at the given path.
    - Media files → play with VLC (so pause/play/etc. work)
    - Docs/PDFs → open with system default app
    - Folders → open in file manager
    """
    global player, playlist, current_index

    if not os.path.exists(path):
        print(f"❌ Path '{path}' not found.")
        return

    # Reset old player if exists
    if player:
        player.stop()
        player = None

    if os.path.isfile(path):
        if is_media_file(path):
            # Open with VLC
            print(f"▶️ Opening media with VLC: {path}")
            player = vlc.MediaPlayer(path)
            player.play()

            # Build playlist from the folder
            folder = os.path.dirname(path)
            files = sorted(os.listdir(folder))
            playlist = [os.path.join(folder, f) for f in files if os.path.isfile(os.path.join(folder, f))]
            current_index = playlist.index(path)

        else:
            # Non-media file → system default app
            print(f"📄 Opening file with default app: {path}")
            if sys.platform.startswith("win"):
                os.startfile(path)
            elif sys.platform.startswith("darwin"):
                subprocess.run(["open", path])
            else:
                subprocess.run(["xdg-open", path])

    else:
        # It's a folder → open in file manager
        print(f"📂 Opening folder in file manager: {path}")
        if sys.platform.startswith("win"):
            os.startfile(path)
        elif sys.platform.startswith("darwin"):
            subprocess.run(["open", path])
        else:
            subprocess.run(["xdg-open", path])




def play():
    global player
    if player:
        player.play()
        print("▶️ Playing")
    else:
        print("⚠️ No media file opened (use play only for video/audio).")


def pause():
    global player
    if player:
        player.pause()
        print("⏸️ Paused")
    else:
        print("⚠️ No media file opened.")


def stop():
    global player
    if player:
        player.stop()
        print("⏹️ Stopped")
    else:
        print("⚠️ No media file opened.")


def next_file():
    global current_index
    if playlist and current_index < len(playlist) - 1:
        current_index += 1
        open_file(playlist[current_index])
    else:
        print("⚠️ No next file available.")


def previous_file():
    global current_index
    if playlist and current_index > 0:
        current_index -= 1
        open_file(playlist[current_index])
    else:
        print("⚠️ No previous file available.")

def forward(seconds=10):
    if player:
        current_time = player.get_time()
        player.set_time(current_time + seconds * 1000)
        return f"⏩ Forward {seconds}s"
    return "⚠️ No media file opened."


import os


def list_files(path=".", filter_type="all", extension=None):
    """
    List contents of a directory with optional filters.

    Args:
        path (str): Directory path to list.
        filter_type (str): "all", "files", or "folders".
        extension (str): Show only files with this extension (e.g., ".pdf").
    """
    if not os.path.exists(path):
        print(f"❌ Path '{path}' not found.")
        return

    if os.path.isfile(path):
        print(f"📄 {path} (file)")
        return

    print(f"\n📂 Listing contents of: {path}\n")
    for entry in os.listdir(path):
        full_path = os.path.join(path, entry)

        if os.path.isdir(full_path):
            if filter_type in ("all", "folders"):
                print(f"📁 {entry}/")

        elif os.path.isfile(full_path):
            if filter_type in ("all", "files"):
                if extension is None or entry.lower().endswith(extension.lower()):
                    print(f"📄 {entry}")



def backward(seconds=10):
    if player:
        current_time = player.get_time()
        player.set_time(max(0, current_time - seconds * 1000))
        return f"⏪ Backward {seconds}s"
    return "⚠️ No media file opened."


if __name__ == "__main__":
    def run():
        """Main interactive loop."""
        print("📂 File Assistant Ready! Commands: open <filepath>, play, pause, stop, next, previous, exit")
        while True:
            command = input(">> ").strip()

            if command.startswith("open "):
                filepath = command[5:].strip('" ')
                open_file(filepath)

            elif command == "play":
                play()
            elif command == "pause":
                pause()
            elif command == "stop":
                stop()
            elif command == "next":
                next_file()
            elif command == "previous":
                previous_file()
            elif command == "forward":
                forward() # forward 10 sec

            elif command == "backward":
                backward()
            elif command.startswith("list"):
                # If user writes "list" → list current folder
                # If user writes "list <path>" → list that folder
                parts = command.split(" ", 1)
                if len(parts) > 1:
                    list_files(parts[1].strip('" '),filter_type="files",extension='.jpg')
                else:
                    list_files(os.getcwd())

            elif command == "exit":
                print("👋 Exiting assistant...")
                break
            else:
                print("❓ Unknown command. Try: open <file>, play, pause, stop, next, previous, exit")


    run()
