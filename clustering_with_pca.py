from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

algs = {
        0: KMeans,
        1: AgglomerativeClustering
        }
#IMPUTATION OF MISSING VALUES (missing values must be np.nan)
pandas.options.mode.use_inf_as_na = True #infinite values are considered missing

def impute_values(data):
    imp = SimpleImputer(strategy = most_frequent)
    imp.fit(data)
    return pd.DataFrame(imp.transform(data))

#Clustering

def cluster(algorithm, array, num_clusters, distance_type, linkage_type):
    array = pd.get_dummies(array)
    algorithm = algs[algorithm](
                                        linkage=linkage_type,
                                        n_clusters=num_clusters,
                                        affinity=distance_type)
    algorithm.fit(array)
    validation = silhouette_score(array, algorithm.labels_, metric=distance_type)
    return (["Cluster "+str(label) for label in algorithm.labels_], validation)

#pca
def twodimensions(data, group_labels):

    pca = PCA(n_components=2)
    X_r = pca.fit(data).transform(data)
    pc1_values = [sample[0] for sample in X_r]
    pc2_values = [sample[1] for sample in X_r]
    data = pd.DataFrame(data = {"PC1":pc1_values,"PC2":pc2_values, "Group":group_labels})
    return (data,pca.explained_variance_ratio_)
#plotting
def plotPCA(transformed_data):
    sns.set(style="whitegrid")
    sns.scatterplot(x="PC1", y="PC2", hue = "Group", data=transformed_data[0])
    plt.show()

#example
if __name__ == "__main__":
    print("Executing PCA example with 'iris' data.")
    from sklearn import datasets
    iris = datasets.load_iris()
    Z = pd.DataFrame(iris.data)

    a = cluster(array = Z, num_clusters = 3, distance_type = "euclidean", linkage_type = "ward")
    b = twodimensions(Z,a[0])
    plotPCA(b)
