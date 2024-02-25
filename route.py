import osmnx as ox
import time
from shapely.geometry import Point, LineString
import os


def main():
    # Configure osmnx to use footprints
    ox.config(use_cache=True, log_console=True)

    # Define start and end points
    start_point = (51.5074, -0.1278)  # London
    end_point = (53.483959, -2.244644)  # Manchester

    # Check if the graph file exists
    graph_file_path = "great_britain_graph.graphml"
    if not os.path.isfile(graph_file_path):
        # Download the road network data for Great Britain
        G = ox.graph_from_place("Great Britain", network_type="drive")
        # Save the graph for future use
        ox.save_graphml(G, filepath=graph_file_path)
    else:
        # Load the graph if it already exists
        G = ox.load_graphml(graph_file_path)

    # Find the nearest nodes to the start and end points
    start_node = ox.distance.nearest_nodes(G, X=start_point[1], Y=start_point[0])
    end_node = ox.distance.nearest_nodes(G, X=end_point[1], Y=end_point[0])

    start_time = time.time()

    # Find the shortest path
    for i in range(18000):
        shortest_path = ox.shortest_path(G, start_node, end_node, weight="length")
        path_line = LineString(
            [Point((G.nodes[node]["x"], G.nodes[node]["y"])) for node in shortest_path]
        )

    end_time = time.time()

    print(f"Time taken: {end_time - start_time} seconds")
    print(f"Shortest path as line: {path_line}")


if __name__ == "__main__":
    main()
