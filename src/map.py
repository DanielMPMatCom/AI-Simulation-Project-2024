import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.interpolate import splprep, splev


class Map:
    def __init__(
        self,
        circuits: list[str],
        thermoelectric: list[str],
        scale=100,
        maxDistancefromTower=100 / 20,
    ) -> None:
        np.random.seed(4806545)
        self.map = np.random.rand(len(circuits), 2) * scale

        # cluster for thermoelectric location
        self.kmeans = KMeans(n_clusters=len(thermoelectric), random_state=1)
        self.kmeans.fit(self.map)

        labels = self.kmeans.labels_
        centroids = self.kmeans.cluster_centers_

        # tension towers location, interpolation
        sorted_centroids = np.sort(centroids, axis=0)
        while True:
            tck, _ = splprep([sorted_centroids[:, 0], sorted_centroids[:, 1]], s=0)
            u_fine = np.linspace(0, 1, len(sorted_centroids) * 4)
            x_fine, y_fine = splev(u_fine, tck)
            self.torres = np.vstack((x_fine, y_fine)).T

            # find isolate points
            isolate_points = []
            all_distances = []
            for c in sorted_centroids:
                distances = []
                for t in self.torres:
                    d = self.distance(t, c)
                    if d >= maxDistancefromTower:
                        distances.append(d)
                if len(distances) == len(self.torres):
                    isolate_points.append(c)
                    all_distances.append(distances)
            sorted_centroids = is

        self.conexiones = [
            (self.torres[i], self.torres[i + 1]) for i in range(len(self.torres) - 1)
        ]

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
            centroids[:, 0],
            centroids[:, 1],
            c="red",
            label="Termoeléctricas",
            s=200,
            alpha=0.75,
            marker="X",
        )
        plt.scatter(
            self.torres[:, 0], self.torres[:, 1], c="#000", label="Torres", marker="s"
        )

        for c in self.conexiones:
            plt.plot(
                [c[0][0], c[1][0]],
                [c[0][1], c[1][1]],
                c="black",
            )

        plt.legend()
        plt.gca().set_facecolor("lightgreen")  # Cambiar el color de fondo de la figura
        plt.show()

    def get_thermoelectrics_positions(self):
        return self.kmeans.cluster_centers_

    def get_circuits_distribution_by_thermoelectric(self):
        return self.kmeans.labels_

    def get_towers_positions(self):
        return self.torres

    def distance(self, point_a, point_b):
        return np.linalg.norm(np.array(point_a) - np.array(point_b))


# Testing

map_2d = Map(
    circuits=["c1", "c2", "c3", "c4", "c5"] * 10, thermoelectric=["t1", "t2"] * 4
)
map_2d.visualice()


import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import splprep, splev
from sklearn.cluster import KMeans

class Map:
    def __init__(self, circuits: list[str], thermoelectric: list[str], scale=100) -> None:
        self.circuits = np.random.rand(len(circuits), 2) * scale
        self.thermoelectric = np.random.rand(len(thermoelectric), 2) * scale
        self.map = np.vstack((self.circuits, self.thermoelectric))
        self.scale = scale

        # Cluster for thermoelectric location
        self.kmeans = KMeans(n_clusters=len(thermoelectric), random_state=1)
        self.kmeans.fit(self.map)

        labels = self.kmeans.labels_
        centroids = self.kmeans.cluster_centers_

        # Tension towers location, interpolation
        sorted_centroids = np.sort(centroids, axis=0)
        while True:
            tck, _ = splprep([sorted_centroids[:, 0], sorted_centroids[:, 1]], s=0)
            u_fine = np.linspace(0, 1, len(sorted_centroids) * 4)
            x_fine, y_fine = splev(u_fine, tck)
            self.torres = np.vstack((x_fine, y_fine)).T

            # Find isolate points
            isolate_points = []
            for point in self.map:
                distances = np.sqrt((self.torres[:, 0] - point[0])**2 + (self.torres[:, 1] - point[1])**2)
                min_distance = np.min(distances)
                if min_distance > self.scale * 0.1:  # Umbral para puntos aislados
                    isolate_points.append(point)

            if not isolate_points:
                break

            # Crear ramificaciones para puntos aislados
            for isolate_point in isolate_points:
                closest_tower_idx = np.argmin(np.sqrt((self.torres[:, 0] - isolate_point[0])**2 + (self.torres[:, 1] - isolate_point[1])**2))
                closest_tower = self.torres[closest_tower_idx]
                new_points = np.linspace(closest_tower, isolate_point, num=5)
                self.torres = np.vstack((self.torres, new_points))

    def visualizar(self):
        plt.scatter(self.circuits[:, 0], self.circuits[:, 1], c='blue', label='Circuitos')
        plt.scatter(self.thermoelectric[:, 0], self.thermoelectric[:, 1], c='red', label='Termoelectricas')

        # Añadir emojis en lugar de marcadores
        for x, y in self.circuits:
            plt.text(x, y, '🔵', fontsize=12, ha='center', va='center')
        for x, y in self.thermoelectric:
            plt.text(x, y, '🔴', fontsize=12, ha='center', va='center')
        for x, y in self.torres:
            plt.text(x, y, '⚡', fontsize=12, ha='center', va='center')

        plt.plot(self.torres[:, 0], self.torres[:, 1], 'k-')

        plt.legend()
        plt.gcf().set_facecolor('lightgrey')  # Cambiar el color de fondo de la figura
        plt.show()

# Ejemplo de uso
mapa = Map(circuits=['c1', 'c2', 'c3', 'c4', 'c5'], thermoelectric=['t1', 't2'])
mapa.visualizar()