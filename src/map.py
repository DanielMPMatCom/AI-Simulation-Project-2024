import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.interpolate import splprep, splev
from typing import Tuple, Literal
import networkx as nx
import plotly.graph_objects as go


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
        Visualizes the map with different components and their connections using Plotly.

        This method uses Plotly to create an interactive scatter plot of various components
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

        self.connections = [
            (self.towers_positions[i], self.towers_positions[i + 1])
            for i in range(len(self.towers_positions) - 1)
        ]

        y_means = self.kmeans.predict(self.circuits_positions)

        fig = go.Figure()

        # Add circuits
        fig.add_trace(
            go.Scatter(
                x=self.circuits_positions[:, 0],
                y=self.circuits_positions[:, 1],
                mode="markers",
                marker=dict(
                    size=10, color=y_means, colorscale="Viridis", showscale=True
                ),
                name="Circuits",
            )
        )

        # Add thermoelectrics
        fig.add_trace(
            go.Scatter(
                x=self.thermoelectrics_positions[:, 0],
                y=self.thermoelectrics_positions[:, 1],
                mode="markers",
                marker=dict(size=15, color="red", symbol="x"),
                name="Thermoelectrics",
            )
        )

        # Add tension towers
        fig.add_trace(
            go.Scatter(
                x=[t[0] for t in self.towers_positions],
                y=[t[1] for t in self.towers_positions],
                mode="markers",
                marker=dict(size=12, color="black", symbol="triangle-up"),
                name="Tension Towers",
            )
        )

        # Add connections
        for u, v in self.connections:
            fig.add_trace(
                go.Scatter(
                    x=[u[0], v[0]],
                    y=[u[1], v[1]],
                    mode="lines",
                    line=dict(color="black"),
                    showlegend=False,
                )
            )

        fig.update_layout(
            title="Map Visualization",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor="rgba(255, 255, 255, 0.5)",
                bordercolor="rgba(0, 0, 0, 0.5)",
            ),
            height=800,
            plot_bgcolor="lightgreen",
        )

        fig.show()


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


class ElectricObject(MapObject):
    """
    Represents an electric object on the map that can be connected to a wire.

    Attributes:
        id (str): The unique identifier of the electric object.
        position (Tuple): The position of the electric object on the map.
        wireConnection: The wire connection associated with the electric object.
        connection_point: The point at which the electric object is connected to the wire.
        distance (float): The distance from the electric object to the connection point.

    Methods:
        connect_to_wire(wireConnection, connection_point, distance):
            Connects the electric object to a wire with the specified connection point and distance.
    """

    def __init__(self, id: str, position: Tuple) -> None:
        """
        Initializes an ElectricObject with the given id and position.

        Args:
            id (str): The unique identifier of the electric object.
            position (Tuple): The position of the electric object on the map.
        """
        ...

        """
        Connects the electric object to a wire.

        Args:
            wireConnection: The wire connection to be associated with the electric object.
            connection_point: The point at which the electric object is connected to the wire.
            distance (float): The distance from the electric object to the connection point.
        """
        MapObject.__init__(self, id, position)
        self.wireConnection = None
        self.connection_point = None
        self.distance = float("inf")

    def connect_to_wire(self, wireConnection, connection_point, distance):
        """
        Establishes a connection to a wire.

        Args:
            wireConnection (Wire): The wire to connect to.
            connection_point (Point): The point at which the connection is made.
            distance (float): The distance from the current object to the connection point.

        Attributes:
            wireConnection (Wire): Stores the wire connection.
            connection_point (Point): Stores the connection point.
            distance (float): Stores the distance to the connection point.
        """
        self.wireConnection = wireConnection
        self.connection_point = connection_point
        self.distance = distance


class TowerObject(MapObject):
    """
    TowerObject represents a tower in the map that can connect to wires.

    Attributes:
        id (str): The unique identifier for the tower.
        position (Tuple): The position of the tower on the map.
        wireConnection (list): A list of wire connections associated with the tower.

    Methods:
        connect_to_wire(wireConnection):
            Connects a wire to the tower.

        wires(remove_any=None):
            Returns a list of wire connections, optionally excluding a specified wire.
    """

    def __init__(self, id: str, position: Tuple) -> None:
        MapObject.__init__(self, id, position)
        self.wireConnection = []

    def connect_to_wire(self, wireConnection):
        self.wireConnection.append(wireConnection)

    def wires(self, remove_any=None):
        return [w for w in self.wireConnection if w != remove_any]


class WireConnection:
    def __init__(self, head: TowerObject, tail: TowerObject) -> None:
        """
        Initializes a new map with the given head and tail TowerObjects.

        Args:
            head (TowerObject): The head tower object.
            tail (TowerObject): The tail tower object.

        Attributes:
            id (str): A unique identifier for the map, created by concatenating the IDs of the head and tail TowerObjects.
            towers (list): A list containing the head and tail TowerObjects.
            circuits_connections (list[Tuple[MapObject, Tuple[int, int], float]]): A list to store circuit connections,
                where each connection is represented as a tuple containing a MapObject, a tuple of two integers, and a float.
            thermoelectrics_connections (list[Tuple[MapObject, Tuple[int, int], float]]): A list to store thermoelectric connections,
                where each connection is represented as a tuple containing a MapObject, a tuple of two integers, and a float.
        """
        self.id = head.id + "&" + tail.id
        self.towers = [head, tail]
        self.circuits_connections: list[Tuple[MapObject, Tuple[int, int], float]] = []
        self.thermoelectrics_connections: list[
            Tuple[MapObject, Tuple[int, int], float]
        ] = []

    def connect_map_object(
        self,
        mapObject: MapObject,
        interception_point: Tuple[int, int],
        distance: float,
        type: Literal["Thermoelectric", "Circuit"],
    ):
        """
        Connects a map object (either a thermoelectric or a circuit) to the wire connection.

        Args:
            mapObject (MapObject): The map object to connect.
            interception_point (Tuple[int, int]): The point at which the connection is made.
            distance (float): The distance from the map object to the interception point.
            type (Literal["Thermoelectric", "Circuit"]): The type of the map object being connected.

        Raises:
            Exception: If the type is not "Thermoelectric" or "Circuit".
        """
        if type == "Thermoelectric":
            self.thermoelectrics_connections.append(
                (mapObject, interception_point, distance)
            )

        elif type == "Circuit":
            self.circuits_connections.append((mapObject, interception_point, distance))
        else:
            raise Exception(f"{type} is not defined for connect to a wireConnection")

    def get_all_circuits_connected(self):
        """
        Retrieve all circuits that are connected.

        Returns:
            list: A list of circuits that are connected.
        """
        return self.circuits_connections


def find_nearest_line_to_a_point(
    point: Tuple[int, int], lines: list[Tuple[Tuple[int, int], Tuple[int, int]]]
):
    """
    Finds the nearest line segment to a given point from a list of line segments.

    Args:
        point (Tuple[int, int]): The point (x, y) to which the nearest line segment is to be found.
        lines (list[Tuple[Tuple[int, int], Tuple[int, int]]]): A list of line segments,
            where each line segment is represented as a tuple of two points (start, end),
            and each point is a tuple (x, y).

    Returns:
        Tuple[int, Tuple[float, float], float]: A tuple containing:
            - The index of the nearest line segment in the list.
            - The coordinates of the interception point on the nearest line segment.
            - The minimum distance from the point to the nearest line segment.
    """

    best_line_index = -1
    min_distance = float("inf")
    interception = (-1, -1)

    for i, (start, end) in enumerate(lines):
        x1, y1 = start
        x2, y2 = end

        px, py = point
        norm = np.linalg.norm([x2 - x1, y2 - y1])
        u = ((px - x1) * (x2 - x1) + (py - y1) * (y2 - y1)) / (norm**2)
        u = max(min(u, 1), 0)
        ix = x1 + u * (x2 - x1)
        iy = y1 + u * (y2 - y1)
        dist = np.linalg.norm([px - ix, py - iy])

        if dist < min_distance:
            min_distance = dist
            best_line_index = i
            interception = (ix, iy)

    return best_line_index, interception, min_distance


class GraphMap:
    def __init__(
        self,
        thermoelectric_labels: list[str],
        circuits_labels: list[str],
        towers_labels: list[str],
        thermoelectrics_positions: list[Tuple[int, int]],
        circuits_positions: list[Tuple[int, int]],
        towers_positions: list[Tuple[int, int]],
    ) -> None:
        """
        Initializes the Map object with thermoelectric, circuit, and tower nodes, and establishes wire connections between them.

        Args:
            thermoelectric_labels (list[str]): Labels for thermoelectric nodes.
            circuits_labels (list[str]): Labels for circuit nodes.
            towers_labels (list[str]): Labels for tower nodes.
            thermoelectrics_positions (list[Tuple[int, int]]): Positions of thermoelectric nodes.
            circuits_positions (list[Tuple[int, int]]): Positions of circuit nodes.
            towers_positions (list[Tuple[int, int]]): Positions of tower nodes.

        Attributes:
            towers_nodes (list[TowerObject]): List of tower nodes.
            thermoelectrics_nodes (list[ElectricObject]): List of thermoelectric nodes.
            circuits_nodes (list[ElectricObject]): List of circuit nodes.
            wireConnections (list[WireConnection]): List of wire connections between nodes.
            thermoelectric_generation_cost (list[Tuple[ElectricObject, ElectricObject, float, list[str]]]):
                List of tuples containing thermoelectric generation cost details.
        """

        self.towers_nodes = [
            TowerObject(towers_labels[i], towers_positions[i])
            for i in range(len(towers_labels))
        ]

        self.thermoelectrics_nodes = [
            ElectricObject(thermoelectric_labels[i], thermoelectrics_positions[i])
            for i in range(len(thermoelectric_labels))
        ]
        self.circuits_nodes = [
            ElectricObject(circuits_labels[i], circuits_positions[i])
            for i in range(len(circuits_labels))
        ]

        self.wireConnections: list[WireConnection] = []

        for i in range(len(self.towers_nodes) - 1):
            wire_connection = WireConnection(
                self.towers_nodes[i], self.towers_nodes[i + 1]
            )
            self.towers_nodes[i].connect_to_wire(wire_connection)
            self.towers_nodes[i + 1].connect_to_wire(wire_connection)

            self.wireConnections.append(wire_connection)

        for circuit in self.circuits_nodes:
            nearest_wire_index, interception, distance = find_nearest_line_to_a_point(
                circuit.position,
                [
                    (wire.towers[0].position, wire.towers[1].position)
                    for wire in self.wireConnections
                ],
            )

            circuit.connect_to_wire(
                self.wireConnections[nearest_wire_index], interception, distance
            )

            self.wireConnections[nearest_wire_index].connect_map_object(
                circuit, interception, distance=distance, type="Circuit"
            )

        for thermoelectric in self.thermoelectrics_nodes:
            nearest_wire_index, interception, distance = find_nearest_line_to_a_point(
                thermoelectric.position,
                [
                    (wire.towers[0].position, wire.towers[1].position)
                    for wire in self.wireConnections
                ],
            )

            thermoelectric.connect_to_wire(
                self.wireConnections[nearest_wire_index], interception, distance
            )

            self.wireConnections[nearest_wire_index].connect_map_object(
                thermoelectric, interception, distance=distance, type="Thermoelectric"
            )

        self.thermoelectric_generation_cost: list[Tuple[str, str, float, list[str]]] = (
            []
        )  # thermoelectric id , circuit id, cost, dependence towers

        for thermoelectric in self.thermoelectrics_nodes:
            self.dfs(
                last_point=thermoelectric.connection_point,
                wire=thermoelectric.wireConnection,
                accumulative_cost=thermoelectric.distance,
                thermoelectric=thermoelectric,
                mk={},
                towers_dependence=[],
            )

    def dfs(
        self,
        last_point: Tuple[int, int],
        wire: WireConnection,
        accumulative_cost: float,
        thermoelectric: ElectricObject,
        mk: dict,
        towers_dependence: list[str],
    ):
        """
        Depth-First Search (DFS) to calculate the cost and dependencies for thermoelectric generation.

        This method traverses the wire connections to calculate the accumulative cost of connecting
        thermoelectrics to circuits and records the dependencies on towers.

        Args:
            last_point (Tuple[int, int]): The last point in the traversal.
            wire (WireConnection): The current wire connection being traversed.
            accumulative_cost (float): The accumulative cost of the connection so far.
            thermoelectric (ElectricObject): The thermoelectric object being connected.
            mk (dict): A dictionary to keep track of visited towers.
            towers_dependence (list[str]): A list to store the IDs of towers that the connection depends on.

        Returns:
            None
        """

        connected_circuits = wire.get_all_circuits_connected()

        for circuit, interception, dist in connected_circuits:

            cost = accumulative_cost + distance(last_point, interception) + dist

            self.thermoelectric_generation_cost.append(
                (thermoelectric.id, circuit.id, cost, towers_dependence)
            )

        towers = wire.towers

        for t in towers:
            if t.id not in mk:

                mk[t.id] = True

                towers_dependence.append(t.id)
                for w in t.wires(wire):
                    self.dfs(
                        t.position,
                        w,
                        (
                            accumulative_cost + distance(last_point, t.position)
                            if tuple(last_point)
                            else 0
                        ),
                        thermoelectric,
                        mk,
                        towers_dependence,
                    )

                towers_dependence.pop()

    def visualize_thermoelectric_generation_cost(
        self, filter_thermoelectrics: list[str] = []
    ):
        """
        Visualizes the thermoelectric generation cost.

        This method creates a graph where each edge represents the cost of generating electricity
        from a thermoelectric to a circuit. The nodes represent thermoelectrics, circuits, and towers.
        The edge weights represent the cost of the connections.

        Args:
            filter_thermoelectrics (list[str]): A list of thermoelectric IDs to filter the visualization.
                Only the connections involving these thermoelectrics will be visualized.

        Returns:
            None
        """
        G = nx.Graph()

        filtered = [
            x
            for x in self.thermoelectric_generation_cost
            if x[0] in filter_thermoelectrics
        ]

        for (
            thermoelectric,
            circuit,
            cost,
            _,
        ) in filtered:
            G.add_edge(thermoelectric, circuit, weight=cost)

        pos = {
            node.id: node.position
            for node in self.thermoelectrics_nodes
            + self.circuits_nodes
            + self.towers_nodes
        }
        labels = nx.get_edge_attributes(G, "weight")

        plt.figure(figsize=(10, 10))
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_color="lightblue",
            node_size=1000,
            font_size=10,
            font_weight="bold",
            edge_color="gray",
            width=2,
        )
        nx.draw_networkx_edge_labels(G, pos, edge_labels=labels, font_size=8)
        plt.title("Thermoelectric Generation Cost Graph")
        plt.show()

    def visualize(self):
        """
        Visualizes the map with thermoelectrics, circuits, towers, and their connections.

        This method creates an interactive plot using Plotly to visualize the nodes and connections
        in the map. It includes the following elements:

        - Thermoelectrics nodes: Plotted as red 'X' markers with labels.
        - Circuits nodes: Plotted as blue 'o' markers with labels.
        - Towers nodes: Plotted as green '^' markers with labels.
        - Wire connections between towers: Plotted as solid black lines.
        - Circuit connections: Plotted as dashed black lines with distance labels.
        - Thermoelectric connections: Plotted as dashed black lines with distance labels.

        The plot also includes a legend and a light green background color.

        Note:
            This method requires Plotly to be installed and imported as go.
        """
        fig = go.Figure()

        # Add thermoelectrics nodes
        fig.add_trace(
            go.Scatter(
                x=[node.position[0] for node in self.thermoelectrics_nodes],
                y=[node.position[1] for node in self.thermoelectrics_nodes],
                mode="markers+text",
                marker=dict(size=12, color="red", symbol="x"),
                text=[node.id for node in self.thermoelectrics_nodes],
                textposition="top center",
                name="Thermoelectrics",
            )
        )

        # Add circuits nodes
        fig.add_trace(
            go.Scatter(
                x=[node.position[0] for node in self.circuits_nodes],
                y=[node.position[1] for node in self.circuits_nodes],
                mode="markers+text",
                marker=dict(size=10, color="blue", symbol="circle"),
                text=[node.id for node in self.circuits_nodes],
                textposition="top center",
                name="Circuits",
            )
        )

        # Add towers nodes
        fig.add_trace(
            go.Scatter(
                x=[node.position[0] for node in self.towers_nodes],
                y=[node.position[1] for node in self.towers_nodes],
                mode="markers+text",
                marker=dict(size=14, color="green", symbol="triangle-up"),
                text=[node.id for node in self.towers_nodes],
                textposition="top center",
                name="Towers",
            )
        )

        # Add wire connections between towers
        for wire in self.wireConnections:
            start_pos = wire.towers[0].position
            end_pos = wire.towers[1].position
            fig.add_trace(
                go.Scatter(
                    x=[start_pos[0], end_pos[0]],
                    y=[start_pos[1], end_pos[1]],
                    mode="lines",
                    line=dict(color="black"),
                    name="Wire Connection",
                    showlegend=False,
                )
            )

        # Add circuit connections
        for c in self.circuits_nodes:
            start_pos = c.position
            end_pos = c.connection_point
            fig.add_trace(
                go.Scatter(
                    x=[start_pos[0], end_pos[0]],
                    y=[start_pos[1], end_pos[1]],
                    mode="lines",
                    line=dict(color="black", dash="dash"),
                    name="Circuit Connection",
                    showlegend=False,
                )
            )
            mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
            fig.add_trace(
                go.Scatter(
                    x=[mid_pos[0]],
                    y=[mid_pos[1]],
                    mode="text",
                    text=[f"{c.distance:.2f}"],
                    textposition="middle center",
                    showlegend=False,
                )
            )

        # Add thermoelectric connections
        for t in self.thermoelectrics_nodes:
            start_pos = t.position
            end_pos = t.connection_point
            fig.add_trace(
                go.Scatter(
                    x=[start_pos[0], end_pos[0]],
                    y=[start_pos[1], end_pos[1]],
                    mode="lines",
                    line=dict(color="black", dash="dash"),
                    name="Thermoelectric Connection",
                    showlegend=False,
                )
            )
            mid_pos = ((start_pos[0] + end_pos[0]) / 2, (start_pos[1] + end_pos[1]) / 2)
            fig.add_trace(
                go.Scatter(
                    x=[mid_pos[0]],
                    y=[mid_pos[1]],
                    mode="text",
                    text=[f"{t.distance:.2f}"],
                    textposition="middle center",
                    showlegend=False,
                )
            )

        fig.update_layout(
            title="Map Visualization",
            xaxis_title="X Coordinate",
            yaxis_title="Y Coordinate",
            legend=dict(
                x=0.01,
                y=0.99,
                bgcolor="rgba(255, 255, 255, 0.5)",
                bordercolor="rgba(0, 0, 0, 0.5)",
            ),
            plot_bgcolor="lightgreen",
            height=800,
        )

        fig.show()


"""
# # Example

# no_circuits = 50
# no_thermoelectrics = 8

# map_2d = Map2D(
#     no_circuits=no_circuits,
#     no_thermoelectrics=no_thermoelectrics,
# )

# # map_2d.visualize()


# graphMap = GraphMap(
#     thermoelectric_labels=[f"Th{i}" for i in range(no_thermoelectrics)],
#     circuits_labels=[f"C{i}" for i in range(no_circuits)],
#     towers_labels=[f"Tw{i}" for i in range(len(map_2d.towers_positions))],
#     thermoelectrics_positions=map_2d.thermoelectrics_positions,
#     circuits_positions=map_2d.circuits_positions,
#     towers_positions=map_2d.towers_positions,
# )

# graphMap.visualize()"""
