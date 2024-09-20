import numpy as np
from matplotlib import pyplot as plt
from sklearn.cluster import KMeans
from scipy.interpolate import splprep, splev


class Map:
    def __init__(
        self, circuits: list[str], thermoelectric: list[str], scale=100
    ) -> None:
        np.random.seed(4806545)
        map = np.random.rand(len(circuits), 2) * scale
        print("map", map)
        # cluster for thermoelectric location

        k = len(thermoelectric)
        kmeans = KMeans(n_clusters=k, random_state=1)
        kmeans.fit(map)
        labels = kmeans.labels_
        centroids = kmeans.cluster_centers_
        print("centroids", centroids)

        # tension towers location, interpolation
        centroids = np.sort(centroids, axis=0)
        tck, _ = splprep([centroids[:, 0], centroids[:, 1]], s=0)
        u_fine = np.linspace(0, 1, len(centroids))
        x_fine, y_fine = splev(u_fine, tck)

        torres = np.vstack((x_fine, y_fine)).T
        conexiones = [(torres[i], torres[i + 1]) for i in range(len(torres) - 1)]

        # plot

        plt.scatter(map[:, 0], map[:, 1], c="blue", label="Circuitos")
        plt.scatter(
            centroids[:, 0],
            centroids[:, 1],
            c="red",
            label="Termoeléctricas",
        )
        # plt.scatter(torres[:, 0], torres[:, 1], c="green", label="Torres")

        # for c in conexiones:
        #     plt.plot([c[0][0], c[1][0]], [c[0][1], c[1][1]], c="black")

        plt.legend()
        plt.show()


# Testing

map_2d = Map(circuits=["c1"] * 5, thermoelectric=["t1"] * 5, scale=10000)
