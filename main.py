import osmnx as ox
import networkx as nx
import folium
import webbrowser
import random
import tkinter as tk
from threading import Thread

place = "Bishkek, Kyrgyzstan"

G = ox.graph_from_place(place, network_type="drive")
G = ox.distance.add_edge_lengths(G)

def add_traffic(G):
    for u, v, k, data in G.edges(keys=True, data=True):
        speed = 50 * random.uniform(0.3, 1.0)
        length_km = data['length'] / 1000
        data['time'] = length_km / speed
    return G

G = add_traffic(G)

root = tk.Tk()
root.title("Google Maps Mini")
root.geometry("400x250")

tk.Label(root, text="Откуда:").pack()
start_entry = tk.Entry(root, width=40)
start_entry.pack()

tk.Label(root, text="Куда:").pack()
end_entry = tk.Entry(root, width=40)
end_entry.pack()

status = tk.Label(root, text="")
status.pack()


def add_fake_buses(m, coords):
    import random

    bus_colors = ["purple", "orange", "darkred", "cadetblue", "pink",
                  "darkgreen", "black", "lightblue", "gray", "beige"]

    if len(coords) < 2:
        return

    for i in range(10):
        start_index = random.randint(0, len(coords) - 2)
        end_index = min(start_index + random.randint(3, 10), len(coords))

        bus_route = coords[start_index:end_index]

        folium.PolyLine(
            bus_route,
            color=bus_colors[i],
            weight=3,
            dash_array="5,10",
            tooltip=f"Автобус №{i + 1}"
        ).add_to(m)

def build_map():
    try:
        start = start_entry.get()
        end = end_entry.get()

        status.config(text="Строю маршрут...")

        orig_point = ox.geocode(start)
        dest_point = ox.geocode(end)

        orig = ox.distance.nearest_nodes(G, orig_point[1], orig_point[0])
        dest = ox.distance.nearest_nodes(G, dest_point[1], dest_point[0])

        route = nx.astar_path(G, orig, dest, weight='time')

        coords = [(G.nodes[n]['y'], G.nodes[n]['x']) for n in route]

        m = folium.Map(location=coords[0], zoom_start=13)

        folium.Marker(coords[0], tooltip="Старт", icon=folium.Icon(color="green")).add_to(m)
        folium.Marker(coords[-1], tooltip="Финиш", icon=folium.Icon(color="red")).add_to(m)

        folium.PolyLine(coords, color="blue", weight=5).add_to(m)
        add_fake_buses(m, coords)

        file = "map.html"
        m.save(file)

        webbrowser.open(file)

        status.config(text="Готово")

    except Exception as e:
        status.config(text=f"Ошибка: {e}")


def run():
    Thread(target=build_map).start()




tk.Button(root, text="Построить маршрут", command=run).pack()

root.mainloop()