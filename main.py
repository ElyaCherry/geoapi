import tkinter as tk
from tkinter import ttk, StringVar
from PIL import ImageTk, Image
import requests
import sys

KEY1 = "175513c9-027e-4035-be37-e494d2b40a58"
KEY2 = "bbd7606b-2ca1-466b-94f9-9170f634c9fa"
LANGUAGES = {"en, US, miles": "en_US",
             "ru, RU, km": "ru_RU",
             "ru, UA, km": "ru_UA",
             "uk, UA, km": "uk_UA",
             "en, RU, km": "en_RU",
             "tr, TR, km": "tr_TR"}
TYPES = {"Map": "map", "Satellite": "sat", "Mixed": "sat,skl"}


class GeoWindow:
    def __init__(self, master):
        self.master = master
        self.frame = tk.Frame(self.master)

        self.map_url: str = ""
        self.weather_url: str = ""
        self.coords: tuple = ()
        self.map_zoom: str = "16"
        self.weather_condition: dict = {}
        self.json_data: dict = {}
        self.response = None
        self.json_weather = None
        self.map_data = None
        self.map = ImageTk.PhotoImage(Image.open("welcome.jpeg").resize((450, 450), Image.ANTIALIAS))
        self.panel = tk.Label(self.master, image=self.map)
        self.panel.pack(side="top", fill="x")

        self.address = tk.Text(self.master, height=2)
        self.address.get("0.0", 'end')  # the address
        self.address.bind("<Return>", self.get_coords_by_address)
        self.address.pack()

        self.weather_label = tk.Label(self.master, text="Weather: ")
        self.weather_label.pack(side="bottom", fill="x", anchor="nw")

        self.json_url = "https://geocode-maps.yandex.ru/1.x/?format=json&apikey=" + KEY1 + \
                        "&geocode=" + str(self.address.get("0.0", 'end'))

        self.button_send_input = tk.Button(self.master, height=1, width=8, text="Show map", bg="#55EE44",
                                           command=self.get_coords_by_address)
        self.button_send_input.pack(side="left", fill="y")

        self.frame_zoom = tk.LabelFrame(self.master, text="Zoom")
        self.button_zoom_out = tk.Button(self.frame_zoom, height=1, text="-", command=self.zoom_out, width=1)
        self.button_zoom_out.pack(side="left")
        self.button_zoom_in = tk.Button(self.frame_zoom, height=1, text="+", command=self.zoom_in, width=1)
        self.button_zoom_in.pack(side="left")
        self.frame_zoom.pack(side="left")

        self.frame_language = tk.LabelFrame(self.master, text="Localization")
        self.language_name = StringVar()
        self.language = StringVar()
        self.language_choice = ttk.Combobox(self.frame_language, values=list(LANGUAGES.keys()),
                                            textvariable=self.language_name, width=12, state="readonly")
        self.language_choice.current(0)
        self.language.set(LANGUAGES[self.language_name.get()])
        self.language_choice.bind("<<ComboboxSelected>>", self.change_language)
        self.language_choice.pack(side="left")
        self.frame_language.pack(side="left")

        self.frame_type = tk.LabelFrame(self.master, text="Type")
        self.map_type_name = StringVar()
        self.map_type = StringVar()
        self.type_choice = ttk.Combobox(self.frame_type, values=list(TYPES.keys()), textvariable=self.map_type_name,
                                        width=9, state="readonly")
        self.type_choice.current(0)
        self.map_type.set(TYPES[self.map_type_name.get()])
        self.type_choice.bind("<<ComboboxSelected>>", self.change_type)
        self.type_choice.pack(side="left")
        self.frame_type.pack(side="left")

        self.frame_weather = tk.LabelFrame(self.master, text="Weather")
        self.button_weather = tk.Button(self.frame_weather, text="Show", bg="#55EE44", command=self.get_weather)
        self.button_weather.pack()
        self.frame_weather.pack(side="left")

        self.frame.pack()

    def get_coords_by_address(self, *args):
        self.json_url = "https://geocode-maps.yandex.ru/1.x/?format=json&apikey=" + KEY1 + \
                        "&geocode=" + str(self.address.get("0.0", 'end'))
        try:
            self.json_data = requests.get(self.json_url).json()
            self.coords = self.json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"][
                                         "Point"]["pos"]
            self.coords = self.coords.split()  # (str, str)
            self.get_map_url()
            self.get_map_by_coords()
        except IndexError:
            pass
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                requests.exceptions.TooManyRedirects, requests.exceptions.Timeout):
            self.map = ImageTk.PhotoImage(Image.open("no_connection.jpeg").resize((450, 450), Image.ANTIALIAS))
            self.panel.config(image=self.map)

    def get_map_url(self):
        try:
            self.map_url = "https://static-maps.yandex.ru/1.x/?ll=" + self.coords[0] + "," + self.coords[1] + \
                           "&size=450,450&pt=" + self.coords[0] + "," + self.coords[1] + "," + "pmwtm" + \
                           "&z=" + self.map_zoom + "&l=" + self.map_type.get() + "&lang=" + self.language.get()
        except IndexError:
            pass
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                requests.exceptions.TooManyRedirects, requests.exceptions.Timeout):
            self.map = ImageTk.PhotoImage(Image.open("no_connection.jpeg").resize((450, 450), Image.ANTIALIAS))
            self.panel.config(image=self.map)

    def get_map_by_coords(self):
        try:
            self.response = requests.get(self.map_url)  # retries=10?
            self.map_data = self.response.content
            with open("index.jpeg", "wb") as map_file:
                map_file.write(self.map_data)
            self.map = ImageTk.PhotoImage(Image.open("index.jpeg").resize((450, 450), Image.ANTIALIAS))
            self.panel.config(image=self.map)
        except IndexError:
            pass
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                requests.exceptions.TooManyRedirects, requests.exceptions.Timeout):
            self.map = ImageTk.PhotoImage(Image.open("no_connection.jpeg").resize((450, 450), Image.ANTIALIAS))
            self.panel.config(image=self.map)

    def get_weather(self):
        self.weather_url = "https://api.weather.yandex.ru/v2/forecast?lat" + self.coords[0] + "&lon=" + self.coords[1] \
                           + "&lang=" + self.language.get()
        self.json_weather = requests.get(self.weather_url, headers={"X-Yandex-API-Key": KEY2}).json()
        try:
            self.weather_condition["temp"] = self.json_weather["fact"]["temp"]
            self.weather_condition["icon"] = self.json_weather["fact"]["icon"]
            self.weather_condition["condition"] = self.json_weather["fact"]["condition"]
            self.weather_label.config(text="Weather: " + str(self.weather_condition["temp"]) + "°С")
        except IndexError:
            pass
        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                requests.exceptions.TooManyRedirects, requests.exceptions.Timeout):
            self.map = ImageTk.PhotoImage(Image.open("no_connection.jpeg").resize((450, 450), Image.ANTIALIAS))
            self.panel.config(image=self.map)

    def zoom_in(self):
        self.map_zoom = str(min(17, int(self.map_zoom) + 1))
        self.get_map_url()
        self.get_map_by_coords()

    def zoom_out(self):
        self.map_zoom = str(max(0, int(self.map_zoom) - 1))
        self.get_map_url()
        self.get_map_by_coords()

    def change_language(self, *args):
        self.language.set(LANGUAGES[self.language_name.get()])
        self.language_choice.selection_clear()
        self.get_map_url()
        self.get_map_by_coords()

    def change_type(self, *args):
        self.map_type.set(TYPES[self.map_type_name.get()])
        self.type_choice.selection_clear()
        self.get_map_url()
        self.get_map_by_coords()


def main():
    root = tk.Tk()
    root.title("Geocoder")
    root.geometry("450x555")
    app = GeoWindow(root)
    root.mainloop()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
