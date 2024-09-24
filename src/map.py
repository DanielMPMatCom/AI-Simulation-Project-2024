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


map_2d = Map2D(
    no_circuits=50,
    no_thermoelectrics=8,
)

map_2d.visualize()
