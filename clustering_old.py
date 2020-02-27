# -*- coding: utf-8 -*-

from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score

algs = {
        0: KMeans,
        1: AgglomerativeClustering
        }

def cluster(algorithm, array, num_clusters, distance_type, linkage_type):
    if algorithm == 0:
        algorithm = KMeans(n_clusters=num_clusters)
    elif algorithm == 1:
        algorithm = AgglomerativeClustering(
                                        linkage=linkage_type,
                                        n_clusters=num_clusters,
                                        affinity=distance_type)
    algorithm.fit(array)
    validation = silhouette_score(array, algorithm.labels_, metric=distance_type)
    return (algorithm.labels_, validation)
