import os
import pygame
from tkinter import Tk, Label, Button, Listbox, filedialog, PhotoImage, ttk
from ttkthemes import ThemedTk


class MusicPlayer:
    def __init__(self, master):
        self.master = master
        master.title("Music Player")
        master.geometry("500x400")
        master.set_theme("breeze")

        self.song_library = []
        self.current_song_index = -1
        self.playing = False

        self.label = Label(master, text="Music Player", font=("Helvetica", 16))
        self.label.pack(pady=10)

        self.song_listbox = Listbox(master, selectmode="SINGLE", width=40)
        self.song_listbox.pack(pady=10)

        self.add_button = Button(
            master, text="Add to Library", command=self.add_to_library)
        self.add_button.pack()

        button_frame = ttk.Frame(master)
        button_frame.pack()

        # Resize factor for the icons
        resize_factor = 0.5

        self.play_icon = PhotoImage(file="play.png")
        self.play_icon = self.play_icon.subsample(int(resize_factor * 100))
        self.play_button = ttk.Button(
            button_frame, image=self.play_icon, command=self.play)
        self.play_button.grid(row=0, column=0, padx=5)

        self.pause_icon = PhotoImage(file="pause.png")
        self.pause_icon = self.pause_icon.subsample(int(resize_factor * 100))
        self.pause_button = ttk.Button(
            button_frame, image=self.pause_icon, command=self.pause)
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_icon = PhotoImage(file="stop.png")
        self.stop_icon = self.stop_icon.subsample(int(resize_factor * 100))
        self.stop_button = ttk.Button(
            button_frame, image=self.stop_icon, command=self.stop)
        self.stop_button.grid(row=0, column=2, padx=5)

        self.forward_icon = PhotoImage(file="forward.png")
        self.forward_icon = self.forward_icon.subsample(
            int(resize_factor * 100))
        self.forward_button = ttk.Button(
            button_frame, image=self.forward_icon, command=self.forward)
        self.forward_button.grid(row=0, column=3, padx=5)

        self.backward_icon = PhotoImage(file="backward.png")
        self.backward_icon = self.backward_icon.subsample(
            int(resize_factor * 100))
        self.backward_button = ttk.Button(
            button_frame, image=self.backward_icon, command=self.backward)
        self.backward_button.grid(row=0, column=4, padx=5)

        self.progress_bar = ttk.Progressbar(
            master, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=10)
        self.progress_bar.bind("<Button-1>", self.set_progress_start)
        self.progress_bar.bind("<B1-Motion>", self.set_progress_update)

        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.update_progress_bar()

    def add_to_library(self):
        Tk().withdraw()
        file_paths = filedialog.askopenfilenames(title="Select Audio Files", filetypes=[
                                                 ("Audio Files", "*.mp3;*.wav")])
        for file_path in file_paths:
            self.song_library.append(file_path)
            self.song_listbox.insert("end", os.path.basename(file_path))

    def play(self):
        if not self.playing and self.song_library and self.current_song_index < len(self.song_library) - 1:
            self.current_song_index += 1
            pygame.mixer.music.load(self.song_library[self.current_song_index])
            pygame.mixer.music.play()
            self.playing = True
            self.update_progress_bar()

    def pause(self):
        if self.playing:
            pygame.mixer.music.pause()
            self.playing = False

    def stop(self):
        pygame.mixer.music.stop()
        self.playing = False
        self.progress_bar.stop()

    def forward(self):
        self.stop()
        if self.current_song_index < len(self.song_library) - 1:
            self.current_song_index += 1
        self.play()

    def backward(self):
        self.stop()
        if self.current_song_index > 0:
            self.current_song_index -= 1
        self.play()

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

    def set_progress_update(self, event):
        if self.playing:
            clicked_x = event.x
            total_width = self.progress_bar.winfo_width()
            total_time = pygame.mixer.Sound(
                self.song_library[self.current_song_index]).get_length() * 1000
            new_time = (clicked_x / total_width) * total_time
            # Set new position in seconds
            pygame.mixer.music.set_pos(new_time / 1000)

    def on_closing(self):
        self.stop()
        self.master.destroy()


if __name__ == "__main__":
    pygame.init()
    root = ThemedTk()
    player = MusicPlayer(root)
    root.mainloop()
    pygame.quit()
