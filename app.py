import streamlit as st
import osmnx as ox
import networkx as nx
import folium
import random
from streamlit_folium import st_folium

st.set_page_config(page_title="Google Maps Mini — Бишкек", page_icon="🗺️", layout="wide")
st.title("🗺️ Google Maps Mini — Бишкек")


@st.cache_resource(show_spinner="Загружаю карту Бишкека...")
def load_graph():
    place = "Bishkek, Kyrgyzstan"
    G = ox.graph_from_place(place, network_type="drive")
    G = ox.distance.add_edge_lengths(G)
    for u, v, k, data in G.edges(keys=True, data=True):
        speed = 50 * random.uniform(0.3, 1.0)
        length_km = data["length"] / 1000
        data["time"] = length_km / speed
    return G


G = load_graph()

col1, col2 = st.columns(2)
with col1:
    start = st.text_input("Откуда:", placeholder="например: Бишкек, ул. Киевская 100")
with col2:
    end = st.text_input("Куда:", placeholder="например: Бишкек, ул. Абдрахманова 150")


def add_fake_buses(m, coords):
    bus_colors = [
        "purple", "orange", "darkred", "cadetblue", "pink",
        "darkgreen", "black", "lightblue", "gray", "beige",
    ]
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
            tooltip=f"Автобус №{i + 1}",
        ).add_to(m)


if st.button("🚗 Построить маршрут", type="primary"):
    if not start or not end:
        st.warning("Введите оба адреса.")
    else:
        with st.spinner("Строю маршрут..."):
            try:
                orig_point = ox.geocode(start)
                dest_point = ox.geocode(end)

                orig = ox.distance.nearest_nodes(G, orig_point[1], orig_point[0])
                dest = ox.distance.nearest_nodes(G, dest_point[1], dest_point[0])

                route = nx.astar_path(G, orig, dest, weight="time")
                coords = [(G.nodes[n]["y"], G.nodes[n]["x"]) for n in route]

                m = folium.Map(location=coords[0], zoom_start=13)
                folium.Marker(coords[0], tooltip="Старт", icon=folium.Icon(color="green")).add_to(m)
                folium.Marker(coords[-1], tooltip="Финиш", icon=folium.Icon(color="red")).add_to(m)
                folium.PolyLine(coords, color="blue", weight=5).add_to(m)
                add_fake_buses(m, coords)

                st.success("Маршрут построен!")
                st_folium(m, width=None, height=500, use_container_width=True)

            except Exception as e:
                st.error(f"Ошибка: {e}")
