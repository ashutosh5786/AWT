import os
import pygame
from tkinter import Tk, Label, Button, Listbox, filedialog, PhotoImage, ttk
from ttkthemes import ThemedTk
import requests
from io import BytesIO
from PIL import Image, ImageTk
import eyed3
import datetime
# Create the music player


class MusicPlayer:
    def __init__(self, master):
        self.master = master
        master.title("Music Player")
        master.geometry("800x600")
        master.option_add("*Font", "SegoeUI 16")

        self.song_paused = False

        # Set the default theme
        self.style = ttk.Style()
        self.style.theme_use('ubuntu')

        # Set the theme
        available_themes = ['aquativo', 'arc', 'black', 'blue', 'breeze', 'clearlooks', 'elegance', 'equilux',
                            'itft1', 'keramik', 'kroc', 'plastik', 'radiance', 'scidblue', 'smog', 'ubuntu', 'winxpblue', 'yaru']
        self.theme_var = ttk.Combobox(master, values=available_themes)
        self.theme_var.set('keramik')  # default value
        self.theme_var.bind('<<ComboboxSelected>>', self.change_theme)
        self.theme_var.grid(row=0, column=0, padx=10, pady=10)

        # Load the default album art
        img = Image.open("default_album_art.png")
        img = img.resize((100, 100))
        self.album_art = ImageTk.PhotoImage(img)

        # self.album_art = PhotoImage(file="default_album_art.png")
        self.album_art_label = ttk.Label(master, image=self.album_art)
        self.album_art_label.grid(row=2, column=0, padx=0, pady=0)

        # # Create a Label widget to display song name of album art
        # self.song_label = Label(master)
        # self.song_label.grid(row=0, column=0, padx=10, pady=10)

        # Library Configuration
        self.song_library = []
        self.song_details = []
        # This needs to be "None" need to fix this its connected to progress bar
        self.current_song_index = 0
        self.playing = False

        # Playlist Configuration
        self.playlist_listbox = Listbox(master, selectmode="MULTIPLE")
        self.playlist_listbox.grid(row=2, column=1, padx=10, pady=10)
        self.playlist_listbox.bind(
            '<<ListboxSelect>>', self.play_selected_song)

        self.label = Label(master, text="Music Player", font=("Segoe UI", 16))
        self.label.grid(row=1, column=0, padx=10, pady=10)

        # Adding the URL box for the S3 and Google Drive
        # self.url_box = ttk.Entry(master, width=40)
        # self.url_box.pack(pady=10)

        # Create the Entry widget
        # self.url_entry = ttk.Entry(master, width=40)

        # # Place the Entry widget
        # self.url_entry.grid(row=0, column=0, padx=5, pady=5)

        # # Create the Button
        # self.add_url_button = Button(
        #     master, text="Add URL", command=self.add_url_library)

        # # Place the Button
        # self.add_url_button.grid(row=1, column=1, padx=5, pady=5)

        # Add the songs to the library
        self.add_button = Button(
            master, text="Select Folder", command=self.add_to_library)
        self.add_button.grid(row=3, column=1, pady=10)

        # Create the buttons
        button_frame = ttk.Frame(master)
        button_frame.grid(row=7, column=0)

        # Resize factor for the icons
        resize_factor = 0.5
        # Load the icons
        self.play_icon = PhotoImage(file="play.png")
        self.play_icon = self.play_icon.subsample(int(resize_factor * 100))
        self.play_button = ttk.Button(
            button_frame, image=self.play_icon, command=self.play)
        self.play_button.grid(row=0, column=2, padx=5)

        self.pause_icon = PhotoImage(file="pause.png")
        self.pause_icon = self.pause_icon.subsample(int(resize_factor * 100))
        self.pause_button = ttk.Button(
            button_frame, image=self.pause_icon, command=self.pause)
        self.pause_button.grid(row=0, column=1, padx=5)
        self.pause_button.grid_remove()  # Hide the pause button by default

        self.forward_icon = PhotoImage(file="forward.png")
        self.forward_icon = self.forward_icon.subsample(
            int(resize_factor * 100))
        self.forward_button = ttk.Button(
            button_frame, image=self.forward_icon, command=self.forward)
        self.forward_button.grid(row=0, column=4, padx=5)

        self.backward_icon = PhotoImage(file="backward.png")
        self.backward_icon = self.backward_icon.subsample(
            int(resize_factor * 100))
        self.backward_button = ttk.Button(
            button_frame, image=self.backward_icon, command=self.backward)
        self.backward_button.grid(row=0, column=0, padx=5)

        # Create the progress bar
        self.progress_bar = ttk.Progressbar(
            master, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.grid(row=4, column=0, pady=10, padx=50)
        self.progress_bar.bind("<Button-1>", self.set_progress_start)
        self.progress_bar.bind("<B1-Motion>", self.set_progress_update)
        self.update_progress_bar()

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

    # Change theme
    def change_theme(self, event):
        selected_theme = self.theme_var.get()
        self.master.set_theme(selected_theme)

    # Add Songs from the URL
    # def add_url_library(self):
    #     url = self.url_entry.get()
    #     if url:
    #         response = requests.get(url)
    #         if response.status_code == 200:
    #             song_data = BytesIO(response.content)
    #             self.song_library.append(song_data)
    #             # self.song_listbox.insert("end", os.path.basename(url))
    #             self.url_entry.delete(0, "end")
    #             # Add the song to the playlist_listbox widget
    #             self.playlist_listbox.insert(
    #                 "end", os.path.basename(file_path))
    #         else:
    #             print("Invalid URL")

    # Add songs to the library
    def add_to_library(self):
        # from local directory
        Tk().withdraw()
        directory_path = filedialog.askdirectory(title="Select Music Folder")
        for file_name in os.listdir(directory_path):
            if file_name.endswith('.mp3') or file_name.endswith('.wav'):
                file_path = os.path.join(directory_path, file_name)

                # created to sort the songs by date added
                date_added = datetime.datetime.fromtimestamp(
                    os.path.getctime(file_path))
                self.song_details.append((file_path, date_added))

        # Sorting the songs by date added
        self.song_details.sort(key=lambda x: x[1], reverse=True)

        # Removing the date added from the list and populating the song_library list
        self.song_library = [song[0] for song in self.song_details]

        for song in self.song_library:
            self.playlist_listbox.insert("end", os.path.basename(song))

    # Get the album art from the song
    # Need to call this function before playing the songs with current index of that song

    def get_album_art(self, file_path):
        audio_file = eyed3.load(file_path)
        if audio_file.tag:
            if audio_file.tag.images:
                image_data = audio_file.tag.images[0].image_data
                img = Image.open(BytesIO(image_data))
                img = img.resize((350, 250))
                self.album_art = ImageTk.PhotoImage(img)
                self.album_art_label.configure(image=self.album_art)
            else:
                img = Image.open("default_album_art.png")
                img = img.resize((100, 100))
                self.album_art = ImageTk.PhotoImage(img)
                self.album_art_label.configure(image=self.album_art)
        else:
            img = Image.open("default_album_art.png")
            img = img.resize((100, 100))
            self.album_art = ImageTk.PhotoImage(img)
            self.album_art_label.configure(image=self.album_art)

    # Playing Selected Song from the List
    def play_selected_song(self, event):
        self.current_song_index = self.playlist_listbox.curselection()[0]
        song_data = self.song_library[self.current_song_index]

        self.play(song_data)


# Stop the music


    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.progress_bar.stop()

    # Play the music

    def play(self, song_data=None):  # The play function is playing from the start of the list and we cant play from the list due to this as the play function is not taking any index value from where tho play from the list I think we need to add the index value or pass it in function
        self.get_album_art(song_data)
        if self.song_paused:
            pygame.mixer.music.unpause()
            self.song_paused = False
            # self.update_progress_bar()
            self.play_button.grid_remove()  # Hide the play button when playing the song
            self.pause_button.grid()  # Show the pause button when playing the song
            self.playing = True

        else:
            self.stop()
            song_data = self.song_library[self.current_song_index]
            pygame.mixer.music.load(song_data)
            pygame.mixer.music.play()
            self.play_button.grid_remove()  # Hide the play button when playing the song
            self.pause_button.grid()  # Show the pause button when playing the song
            self.playing = True
            self.update_progress_bar()

        # # Calling the get_album_art function to get the album art
        # album_art = self.get_album_art()

        # song_name = song_names[self.current_song_index]
        # album_art = self.song_library[self.current_song_index].album_art
        # pygame.mixer.music.load(self.song_library[self.current_song_index])

# Pause the music

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False
            self.song_paused = True
            self.play_button.grid()  # Show the play button
            self.pause_button.grid_remove()  # Hide the pause button

    # Go to the next song
    def forward(self):
        self.stop()
        if self.current_song_index < len(self.song_library) - 1:
            self.current_song_index += 1
            song_data = self.song_library[self.current_song_index]
            self.play(song_data)

    # Go back to the previous song
    def backward(self):
        self.stop()
        if self.current_song_index > 0:
            self.current_song_index -= 1
            song_data = self.song_library[self.current_song_index]
            self.play(song_data)

    # Update the progress bar as the song plays
    def update_progress_bar(self):
        if 0 <= self.current_song_index < len(self.song_library):
            total_time = pygame.mixer.Sound(
                self.song_library[self.current_song_index]).get_length() * 1000
            self.progress_bar["maximum"] = total_time

            def update():
                if self.playing:
                    current_time = pygame.mixer.music.get_pos()
                    self.progress_bar["value"] = current_time
                    self.master.after(100, update)

            update()

    # Set the progress bar to the clicked position
    def set_progress_start(self, event):
        if self.playing:
            clicked_x = event.x
            total_width = self.progress_bar.winfo_width()
            total_time = pygame.mixer.Sound(
                self.song_library[self.current_song_index]).get_length() * 1000
            new_time = (clicked_x / total_width) * total_time
            # Set new position in seconds
            pygame.mixer.music.set_pos(new_time / 1000)
            self.progress_bar["value"] = new_time

    # Update the progress bar as the user drags the mouse
    def set_progress_update(self, event):
        if self.playing:
            clicked_x = event.x
            total_width = self.progress_bar.winfo_width()
            total_time = pygame.mixer.Sound(
                self.song_library[self.current_song_index]).get_length() * 1000
            new_time = (clicked_x / total_width) * total_time
            # Set new position in seconds
            pygame.mixer.music.set_pos(new_time / 1000)

    # Stop the music and close the window
    def on_closing(self):
        self.stop()
        self.master.destroy()
        os._exit(0)


# Run the program
if __name__ == "__main__":
    pygame.init()
    root = ThemedTk()
    player = MusicPlayer(root)
    root.mainloop()
    pygame.quit()


# @ TODO 1: Add the URL box for the S3 and Google Drive
# @ TODO 2: Add the album art to the player
# @ TODO 3: Add the progress bar to the player
# @ TODO 4: Add the volume control to the player
# @ TODO 5: Add the song duration to the player
# @ TODO 6: Add the song current time to the player
# @ TODO 7: Add the song name to the player
