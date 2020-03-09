
from sklearn.cluster import AgglomerativeClustering, KMeans
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA

import pandas as pd
import plotly.express as px

algs = {
        0: AgglomerativeClustering,
        1: KMeans
        }

#Clustering

def cluster(algorithm, array, num_clusters, distance_type, linkage_type):
    #array = pd.get_dummies(array)
    if(algorithm):
        algorithm = algs[algorithm](n_clusters=num_clusters)
    else:
        algorithm = algs[algorithm](
                                        linkage=linkage_type,
                                        n_clusters=num_clusters,
                                        affinity=distance_type)
    algorithm.fit(array)
    validation = silhouette_score(array, algorithm.labels_, metric=distance_type)
    return (["Cluster "+str(label) for label in algorithm.labels_], validation)
    #return (algorithm.labels_, validation)


#plotting
def plotPCA(data, group_labels):
    pca = PCA(n_components=2)
    X_r = pca.fit(data).transform(data)
    pc1_values = [sample[0] for sample in X_r]
    pc2_values = [sample[1] for sample in X_r]
    print(len(pc1_values), len(pc2_values), len(group_labels))
    data = pd.DataFrame(data = {"PC1":pc1_values,
                                "PC2":pc2_values, 
                                "Group":["{lb}".format(lb=label) for label in group_labels]})

    fig = px.scatter(data, x = "PC1", y = "PC2", color = "Group")

    fig.update_layout(
        xaxis_title="PC1 (%.3f)"%(pca.explained_variance_ratio_[0]),
        yaxis_title="PC2 (%.3f)"%(pca.explained_variance_ratio_[1]),
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="#7f7f7f"
        )
    )

    return fig


#example
if __name__ == "__main__":
    print("Executing PCA example with 'iris' data.")
    from sklearn import datasets
    iris = datasets.load_iris()
    Z = pd.DataFrame(iris.data)

    a = cluster(algorithm=1, array = Z, num_clusters = 3, distance_type = "euclidean", linkage_type = "ward")
    b = twodimensions(Z,a[0])
    plotPCA(b, path='/home/fabian/image.png')
