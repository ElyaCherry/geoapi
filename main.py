import tkinter as tk
from PIL import ImageTk, Image
import requests

KEY = "175513c9-027e-4035-be37-e494d2b40a58"


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
        self.address.bind("<Return>", self.get_map_by_coords)

        self.json_url = "https://geocode-maps.yandex.ru/1.x/?format=json&apikey=" + KEY + \
                        "&geocode=" + str(self.address.get("0.0", 'end'))  # TODO: read 1 line only

        self.button_send_input = tk.Button(self.master, height=1, text="Show map", command=self.get_map_by_coords)
        self.button_send_input.pack()

        self.frame.pack()

    def get_map_by_coords(self):
        self.get_coords_by_address()
        self.map_url = "https://static-maps.yandex.ru/1.x/?ll=" + self.coords[0] + "," + self.coords[1] + \
                       "&size=450,450&z=16&l=map&pt=" + self.coords[0] + "," + self.coords[1] + "," + \
                       "pmwtm1"
        print(self.map_url)
        self.response = requests.get(self.map_url)
        self.map_data = self.response.content
        with open("index.jpeg", "wb") as map_file:
            map_file.write(self.map_data)
        self.map = ImageTk.PhotoImage(Image.open("index.jpeg").resize((450, 450), Image.ANTIALIAS))
        self.panel.config(image=self.map)
    # Москва, улица Новый Арбат, дом 24

    def get_coords_by_address(self):
        self.json_url = "https://geocode-maps.yandex.ru/1.x/?format=json&apikey=" + KEY + \
                        "&geocode=" + str(self.address.get("0.0", 'end'))
        self.json_data = requests.get(self.json_url).json()
        self.coords = self.json_data["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]["Point"]["pos"]
        self.coords = self.coords.split()  # [0], [1]


def main():
    root = tk.Tk()
    root.title("Geocoder")
    root.geometry("450x522")
    app = GeoWindow(root)
    root.mainloop()


if __name__ == '__main__':
    main()
