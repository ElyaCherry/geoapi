import tkinter as tk
from tkinter import ttk, StringVar
from PIL import ImageTk, Image
import requests

KEY = "175513c9-027e-4035-be37-e494d2b40a58"
LANGUAGES = ["ru_RU", "ru_UA", "uk_UA", "en_US", "en_RU", "tr_TR"]
TYPES = {"Карта": "map", "Спутник": "sat", "Смешанный": "sat,skl"}


class GeoWindow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.map_url: str = ""
        self.coords: tuple = ()
        self.json_data: dict = {}
        self.response = None
        self.map_data = None
        self.map = ImageTk.PhotoImage(Image.open("9d4dccf7ffabe0c4c8025991.jpeg").resize((450, 450), Image.ANTIALIAS))
        self.panel = tk.Label(self.master, image=self.map)
        self.panel.pack(side="top", fill="x")

        self.address = tk.Text(self.master, height=2)
        self.address.pack()
        self.address.get("0.0", 'end')  # the address
        self.address.bind("<Return>", self.get_coords_by_address)

        self.json_url = "https://geocode-maps.yandex.ru/1.x/?format=json&apikey=" + KEY + \
                        "&geocode=" + str(self.address.get("0.0", 'end'))  # TODO: read 1 line only

        self.button_send_input = tk.Button(self.master, height=1, text="Show map", bg="#55EE44",
                                           command=self.get_coords_by_address)
        self.button_send_input.pack(side="left", fill="y")

        self.frame_zoom = tk.LabelFrame(self.master, text="Zoom")
        self.button_zoom_out = tk.Button(self.frame_zoom, height=1, text="-", command=self.zoom_out)
        self.button_zoom_out.pack(side="left")
        self.button_zoom_in = tk.Button(self.frame_zoom, height=1, text="+", command=self.zoom_in)
        self.button_zoom_in.pack(side="left")
        self.frame_zoom.pack(side="left")

        # self.languages = {"Русский, Россия": "ru_RU", "Украинский, Украина": "uk_UA", "Русский, Украина": "ru_UA",
        #                   "Английский"}
        self.frame_language = tk.LabelFrame(self.master, text="Language select")
        self.language = StringVar()
        self.language_choice = ttk.Combobox(self.frame_language, values=LANGUAGES, textvariable=self.language)
        self.language_choice.current(0)
        self.language_choice.bind("<<ComboboxSelected>>", self.get_coords_by_address)
        self.language_choice.pack(side="left")
        self.frame_language.pack(side="left")

        self.frame_type = tk.LabelFrame(self.master, text="Type select")
        self.map_type_name = StringVar()
        self.map_type = StringVar()
        self.type_choice = ttk.Combobox(self.frame_type, values=list(TYPES.keys()), textvariable=self.map_type_name)
        self.type_choice.current(0)
        self.map_type.set(TYPES[self.map_type_name.get()])
        self.type_choice.bind("<<ComboboxSelected>>", self.change_type)
        self.type_choice.pack(side="left")
        self.frame_type.pack(side="left")

        self.frame.pack()

        # map args:
        self.map_zoom = "16"  # 0-17

    def get_coords_by_address(self, *args):
        self.json_url = "https://geocode-maps.yandex.ru/1.x/?format=json&apikey=" + KEY + \
                        "&geocode=" + str(self.address.get("0.0", 'end'))
        self.json_data = requests.get(self.json_url).json()
        try:
            self.coords = self.json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                                         "Point"]["pos"]
            self.coords = self.coords.split()  # [str, str]
            self.get_map_by_coords()
        except IndexError:
            pass

    def get_map_by_coords(self):
        try:
            self.map_url = "https://static-maps.yandex.ru/1.x/?ll=" + self.coords[0] + "," + self.coords[1] + \
                           "&size=450,450&pt=" + self.coords[0] + "," + self.coords[1] + "," + "pmwtm1" + \
                           "&z=" + self.map_zoom + "&l=" + self.map_type.get() + "&lang=" + self.language.get()

            self.response = requests.get(self.map_url)
            self.map_data = self.response.content
            with open("index.jpeg", "wb") as map_file:
                map_file.write(self.map_data)
            self.map = ImageTk.PhotoImage(Image.open("index.jpeg").resize((450, 450), Image.ANTIALIAS))
            self.panel.config(image=self.map)
        except IndexError:
            pass
    # Москва, улица Новый Арбат, дом 24

    def zoom_in(self):
        self.map_zoom = str(min(17, int(self.map_zoom) + 1))
        self.get_map_by_coords()

    def zoom_out(self):
        self.map_zoom = str(max(0, int(self.map_zoom) - 1))
        self.get_map_by_coords()

    def change_type(self, *args):
        self.map_type.set(TYPES[self.map_type_name.get()])
        self.get_map_by_coords()


def main():
    root = tk.Tk()
    root.title("Geocoder")
    root.geometry("450x535")
    app = GeoWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
