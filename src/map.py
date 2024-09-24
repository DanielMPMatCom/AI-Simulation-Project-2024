import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.interpolate import splprep, splev
import networkx as nx
from typing import Tuple


# REFACTOR MAP
def distance(point_a, point_b):
    """
    Calculate the Euclidean distance between two points.

    Parameters:
    point_a (tuple or list): Coordinates of the first point (x, y).
    point_b (tuple or list): Coordinates of the second point (x, y).

    Returns:
    float: The Euclidean distance between point_a and point_b.
    """
    return np.linalg.norm(np.array(point_a) - np.array(point_b))


def is_isolate_point(point, point_references, max_distance):
    """
    Determines if a given point is isolated based on a list of reference points and a maximum distance.

    Args:
        point (tuple): The point to check, represented as a tuple of coordinates (e.g., (x, y)).
        point_references (list): A list of reference points, each represented as a tuple of coordinates.
        max_distance (float): The maximum distance to consider a point as isolated.

    Returns:
        bool: True if the point is isolated (i.e., all reference points are at least max_distance away), False otherwise.
    """
    for pr in point_references:
        if distance(pr, point) <= max_distance:
            return False
    return True


class MapObject:
    """
    A class to represent an object on a map.

    Attributes:
    -----------
    id : int
        The unique identifier of the map object.
    position : tuple
        The (x, y) coordinates of the map object on the map.
    connections : list
        A list of other MapObject instances that this object is connected to.

    Methods:
    --------
    add_connection(map_object):
        Adds a connection to another MapObject.

    __str__():
        Returns a string representation of the MapObject.
    """

    def __init__(self, id: str, position: Tuple[int, int]) -> None:
        """
        Initializes a new instance of the class.

        Args:
            id (str): The unique identifier for the instance.
            position (Tuple[int, int]): The position of the instance as a tuple of (x, y) coordinates.

        Attributes:
            id (str): The unique identifier for the instance.
            position (Tuple[int, int]): The position of the instance.
            connections (list): A list to store connections related to the instance.
        """
        self.id = id
        self.position = position
        self.connections = []

    def add_connection(self, map_object):
        """
        Adds a connection to the current map object.

        Parameters:
        map_object (MapObject): The map object to be added as a connection.

        Returns:
        None
        """
        self.connections.append(map_object)

    def __str__(self):
        """
        Returns a string representation of the Node object.

        The string includes the node's ID, position, and its connections.

        Returns:
            str: A string describing the node.
        """
        return f"Node {self.id} at {self.position} with connections {self.connections}"


def create_connection(map_object_1: MapObject, map_object_2: MapObject):
    """
    Establishes a bidirectional connection between two MapObject instances.

    This function ensures that both map_object_1 and map_object_2 are connected
    to each other. If a connection does not already exist, it adds the connection
    to both objects.

    Args:
        map_object_1 (MapObject): The first map object to connect.
        map_object_2 (MapObject): The second map object to connect.

    Returns:
        None
    """
    if map_object_1 not in map_object_2.connections:
        map_object_1.add_connection(map_object_2)

    if map_object_2 not in map_object_1.connections:
        map_object_2.add_connection(map_object_1)


class Map2D:
    """
    A class to represent a 2D map for simulating circuits, thermoelectrics, and towers.

    Methods:
        __init__(no_circuits, no_thermoelectrics, scale=100, max_distance_from_tower=10, random_seed=4806545):
        generate_circuits_positions(no_circuits, scale):
            Generates random positions for circuits.
        generate_thermoelectrics_positions(no_thermoelectrics, circuits_positions, random_state):
            Generates positions for thermoelectrics using KMeans clustering.
        visualize():
            Visualizes the map with circuits, thermoelectrics, and towers.
    """

    def __init__(
        self,
        no_circuits: int,
        no_thermoelectrics: int,
        scale=100,
        max_distance_from_tower=10,
        random_seed: int = 4806545,
    ) -> None:
        """
        Initializes the map with circuits, thermoelectrics, and towers.

        Args:
            no_circuits (int): Number of circuits to generate.
            no_thermoelectrics (int): Number of thermoelectrics to generate.
            scale (int, optional): Scale factor for the map. Defaults to 100.
            max_distance_from_tower (int, optional): Maximum distance a tower can be from a thermoelectric. Defaults to 10.
            random_seed (int, optional): Seed for random number generation. Defaults to 4806545.

        Attributes:
            thermoelectrics_positions (list): List of positions for thermoelectrics.
            towers_positions (list): List of positions for towers.
            circuits_positions (list): List of positions for circuits.
            kmeans (KMeans): KMeans clustering object for thermoelectrics.
            connections (list): List of connections between towers.
        """

        self.thermoelectrics_positions = []
        self.towers_positions = []

        np.random.seed(random_seed)

        self.circuits_positions = self.generate_circuits_positions(
            no_circuits=no_circuits, scale=scale
        )

        state = np.random.RandomState(seed=random_seed)

        self.thermoelectrics_positions, self.kmeans = (
            self.generate_thermoelectrics_positions(
                no_thermoelectrics=no_thermoelectrics,
                circuits_positions=self.circuits_positions,
                random_state=state,
            )
        )

        self.towers_positions = []
        centroids = self.thermoelectrics_positions

        while True:
            insolate_centroids = []
            for c in centroids:
                if is_isolate_point(c, self.towers_positions, max_distance_from_tower):
                    insolate_centroids.append(c)

            insolate_centroids = np.array(insolate_centroids)

            if len(insolate_centroids) == 0:
                break

            if len(insolate_centroids) > 3:
                interpolation = splprep(
                    [insolate_centroids[:, 0], insolate_centroids[:, 1]], s=0
                )
                tck, u = interpolation
                x_fine, y_fine = splev(np.linspace(0, 1, no_thermoelectrics * 2), tck)
                interpolated_points = np.vstack((x_fine, y_fine)).T

                for p in interpolated_points:
                    self.towers_positions.append(p)
            else:
                break

        self.towers_positions = sorted(self.towers_positions, key=lambda x: x[0])
        self.connections = [
            (self.towers_positions[i], self.towers_positions[i + 1])
            for i in range(len(self.towers_positions) - 1)
        ]

    def generate_circuits_positions(self, no_circuits: int, scale: int) -> np.ndarray:
        """
        Generates random positions for circuits within the given scale.

        Args:
            no_circuits (int): The number of circuits to generate positions for.
            scale (int): The scale factor for the map dimensions.

        Returns:
            np.ndarray: An array of shape (no_circuits, 2) containing the generated positions.
        """

        return np.random.rand(no_circuits, 2) * scale

    def generate_thermoelectrics_positions(
        self,
        no_thermoelectrics: int,
        circuits_positions: list[tuple[int, int]],
        random_state: np.random.RandomState,
    ) -> Tuple[np.ndarray, KMeans]:
        """
        Generates positions for thermoelectrics using KMeans clustering.

        Args:
            no_thermoelectrics (int): The number of thermoelectrics to generate positions for.
            circuits_positions (list[tuple[int, int]]): The positions of the circuits.
            random_state (np.random.RandomState): The random state for reproducibility.

        Returns:
            Tuple[np.ndarray, KMeans]: A tuple containing the positions of the thermoelectrics and the KMeans object.
        """

        kmeans = KMeans(n_clusters=no_thermoelectrics, random_state=random_state)
        kmeans.fit(circuits_positions)
        centroids = kmeans.cluster_centers_
        return centroids, kmeans

    def visualize(self):
        """
        Visualizes the map with different components and their connections.

        This method uses matplotlib to create a scatter plot of various components
        on the map, including circuits, thermoelectrics, and tension towers. It also
        plots the connections between these components.

        The components are visualized as follows:
        - Circuits: Plotted as circles with colors determined by k-means clustering.
        - Thermoelectrics: Plotted as red X markers.
        - Tension Towers: Plotted as black triangle markers.

        The connections between components are plotted as black lines.

        The plot includes a legend and a light green background.

        Returns:
            None
        """
        y_means = self.kmeans.predict(self.circuits_positions)

        plt.scatter(
            self.circuits_positions[:, 0],
            self.circuits_positions[:, 1],
            label="Circuits",
            s=50,
            cmap="viridis",
            marker="o",
            c=y_means,
        )
        plt.scatter(
            self.thermoelectrics_positions[:, 0],
            self.thermoelectrics_positions[:, 1],
            c="red",
            label="Thermoelectrics",
            s=200,
            alpha=0.75,
            marker="X",
        )
        plt.scatter(
            [t[0] for t in self.towers_positions],
            [t[1] for t in self.towers_positions],
            c="black",
            label="Tension Towers",
            s=100,
            alpha=0.75,
            marker="^",
        )

        for u, v in self.connections:
            plt.plot([u[0], v[0]], [u[1], v[1]], c="black")

        plt.legend()
        plt.gca().set_facecolor("lightgreen")
        plt.show()


class GraphMap:
    def __init__(
        self,
        thermoelectric_labels: list[str],
        circuits_labels: list[str],
        thermoelectrics_positions: list[Tuple[int, int]],
        circuits_positions: list[Tuple[int, int]],
        towers_positions: list[Tuple[int, int]],
    ) -> None:
        # objetivo un grafo bidireccional con peso de aristas

        self.towers_nodes = [MapObject() for i in range(len(thermoelectric_labels))]
        self.thermoelectrics_nodes = []
        self.circuits_nodes = []


# OLD CLASS MAP


class Node:
    def __init__(self, id, position):
        self.id = id
        self.position = position
        self.connections = []

    def __str__(self):
        return f"Node {self.id} at {self.position} with connections {self.connections}"


class Map:
    def __init__(
        self,
        circuits_labels: list[str],
        thermoelectric_labels: list[str],
        scale=100,
        max_distance_from_tower=10,
    ) -> None:
        np.random.seed(4806545)
        self.map = np.random.rand(len(circuits_labels), 2) * scale

        # cluster for thermoelectric location
        self.kmeans = KMeans(n_clusters=len(thermoelectric_labels), random_state=1)
        self.kmeans.fit(self.map)

        centroids = self.kmeans.cluster_centers_

        # tension towers location, interpolation
        def isIsolateCentroid(centroid, towers, maxDistance):
            for tower in towers:

                if self.distance(centroid[1:], tower) < maxDistance:
                    return False
            return True

        self.towers = []
        self.connections = []

        while True:
            insolate_centroids = []
            for i, c in enumerate(centroids):
                if isIsolateCentroid(c, self.towers, max_distance_from_tower):
                    insolate_centroids.append(c)

            insolate_centroids = np.array(insolate_centroids)
            if len(insolate_centroids) == 0:
                break

            if len(insolate_centroids) > 3:
                interpolation = splprep(
                    [insolate_centroids[:, 0], insolate_centroids[:, 1]], s=0
                )
                tck, u = interpolation
                x_fine, y_fine = splev(np.linspace(0, 1, 10), tck)
                interpolated_points = np.vstack((x_fine, y_fine)).T

                for p in interpolated_points:
                    self.towers.append(p)

            else:
                break

        # connections

        self.towers = sorted(self.towers, key=lambda x: x[0])

        for i in range(len(self.towers) - 1):
            self.connections.append((self.towers[i], self.towers[i + 1]))

        # resume data
        self.thermoelectrics = [
            (thermoelectric_labels[i], c) for i, c in enumerate(centroids)
        ]

        self.circuits = [(circuits_labels[i], c) for i, c in enumerate(self.map)]
        self.generate_graph()

    def generate_graph(self):

        self.thermoelectrics_nodes = []
        self.circuits_nodes = []
        self.towers_nodes = [Node(f"T{i}", t) for i, t in enumerate(self.towers)]

        for t in range(len(self.towers_nodes) - 1):
            self.towers_nodes[t].connections.append(self.towers_nodes[t + 1])
            self.towers_nodes[t + 1].connections.append(self.towers_nodes[t])

        def find_nearest_tower(node: Node):
            nearest_tower = None
            min_distance = float("inf")

            for t in self.towers_nodes:
                distance = self.distance(node.position, t.position)
                if distance < min_distance:
                    min_distance = distance
                    nearest_tower = t

            return nearest_tower

        for c in self.circuits:
            c_node = Node(c[0], c[1])
            nearest_tower = find_nearest_tower(c_node)
            c_node.connections.append(nearest_tower)
            nearest_tower.connections.append(c_node)
            self.circuits_nodes.append(c_node)

        for t in self.thermoelectrics:
            t_node = Node(t[0], t[1])
            nearest_tower = find_nearest_tower(t_node)
            t_node.connections.append(nearest_tower)
            nearest_tower.connections.append(t_node)
            self.thermoelectrics_nodes.append(t_node)

        return

    def visualice_as_graph(self):
        all_nodes = self.circuits_nodes + self.thermoelectrics_nodes + self.towers_nodes
        G = nx.Graph()
        for n in all_nodes:
            G.add_node(n.id, pos=(n.position[0], n.position[1]))

        for n in all_nodes:
            for c in n.connections:
                G.add_edge(n.id, c.id)

        pos = nx.get_node_attributes(G, "pos")
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=500,
            node_color="skyblue",
            edge_color="gray",
        )

        plt.gcf().set_facecolor("lightgrey")  # Cambiar el color de fondo de la figura
        plt.show()

    def visualice(self):
        y_means = self.kmeans.predict(self.map)
        centroids = self.kmeans.cluster_centers_

        plt.scatter(
            self.map[:, 0],
            self.map[:, 1],
            label="Circuitos",
            s=50,
            cmap="viridis",
            marker="o",
            c=y_means,
        )
        plt.scatter(
            self.thermoelectrics[:, 0],
            self.thermoelectrics[:, 1],
            c="red",
            label="Termoeléctricas",
            s=200,
            alpha=0.75,
            marker="X",
        )
        plt.scatter(
            [t[0] for t in self.towers],
            [t[1] for t in self.towers],
            c="black",
            label="Torres de tensión",
            s=100,
            alpha=0.75,
            marker="^",
        )

        for u, v in self.connections:
            plt.plot([u[0], v[0]], [u[1], v[1]], c="black")

        plt.legend()
        plt.gca().set_facecolor("lightgreen")  # Cambiar el color de fondo de la figura
        plt.show()

    def distance(self, point_a, point_b):
        return np.linalg.norm(np.array(point_a) - np.array(point_b))


# Testing

# map_2d = Map(
#     circuits_labels=["c1", "c2", "c3", "c4", "c5"] * 10,
#     thermoelectric_labels=["G1", "G2"] * 4,
# )
# map_2d.visualice_as_graph()


map_2d = Map2D(
    no_circuits=50,
    no_thermoelectrics=8,
)

map_2d.visualize()


node_map = ObjectMap(
    thermoelectric_labels=[f"G{i}" for i in range(4)],
    circuits_labels=[f"G{i}" for i in range(50)],
    thermoelectrics_positions=map_2d.thermoelectrics_positions,
    circuits_positions=map_2d.circuits_positions,
    towers_positions=map_2d.towers_positions,
)
