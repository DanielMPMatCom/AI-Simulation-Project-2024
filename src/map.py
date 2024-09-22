import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.interpolate import splprep, splev
import networkx as nx


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

    # def visualice(self):
    #     y_means = self.kmeans.predict(self.map)
    #     centroids = self.kmeans.cluster_centers_

    #     plt.scatter(
    #         self.map[:, 0],
    #         self.map[:, 1],
    #         label="Circuitos",
    #         s=50,
    #         cmap="viridis",
    #         marker="o",
    #         c=y_means,
    #     )
    #     plt.scatter(
    #         self.thermoelectrics[:, 0],
    #         self.thermoelectrics[:, 1],
    #         c="red",
    #         label="Termoeléctricas",
    #         s=200,
    #         alpha=0.75,
    #         marker="X",
    #     )
    #     plt.scatter(
    #         [t[0] for t in self.towers],
    #         [t[1] for t in self.towers],
    #         c="black",
    #         label="Torres de tensión",
    #         s=100,
    #         alpha=0.75,
    #         marker="^",
    #     )

    #     for u, v in self.connections:
    #         plt.plot([u[0], v[0]], [u[1], v[1]], c="black")

    #     plt.legend()
    #     plt.gca().set_facecolor("lightgreen")  # Cambiar el color de fondo de la figura
    #     plt.show()

    def distance(self, point_a, point_b):
        return np.linalg.norm(np.array(point_a) - np.array(point_b))


# Testing

map_2d = Map(
    circuits_labels=["c1", "c2", "c3", "c4", "c5"] * 10,
    thermoelectric_labels=["G1", "G2"] * 4,
)
map_2d.visualice_as_graph()
