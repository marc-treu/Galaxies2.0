import numpy as np
import sqlite3
import shelve

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from yellowbrick.text import TSNEVisualizer
import sklearn.manifold as ts
from kmeans import Kmeans
from sklearn.decomposition import TruncatedSVD, PCA


def get_books(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute("""SELECT * FROM livres""")
    result = cursor.fetchall()
    connexion.close()
    return result


def get_id_nodes_book(project_path, id_book):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute("""SELECT idNoeud FROM texteNoeuds WHERE idRowLivre = (?) """, (id_book,))
    result = cursor.fetchall()
    connexion.close()
    return [i[0] for i in result]


def get_galaxie_from_id_node(project_path, id_node):

    # listeNodes n'existe plus

    dirNode = shelve.open(project_path + '/BDs/listeNodes')
    id_galaxie = dirNode[str(id_node)]
    dirNode.close()
    return id_galaxie


def get_list_galaxie(project_path):
    connexion = sqlite3.connect(project_path + '/BDs/galaxie.db', 1, 0, 'EXCLUSIVE')
    cursor = connexion.cursor()
    cursor.execute("""SELECT idGalaxie FROM degreGalaxies""")
    result = cursor.fetchall()
    connexion.close()
    return [i[0] for i in result]


def inverse_bd(project_path, list_galaxie):
    dirGalaxies = shelve.open(project_path + '/BDs/listeGalaxies')
    # listeNodes n'existe plus
    dirNode = shelve.open(project_path + '/BDs/listeNodes')

    for id_galaxie in list_galaxie:
        for node in dirGalaxies[id_galaxie]:
            dirNode[str(node)] = id_galaxie

    dirGalaxies.close()
    dirNode.close()


if __name__ == '__main__':
    path = "../projects/Balzac"

    t = get_books(path)
    result = []
    for i in range(1, len(t) + 1):
        result.append(get_id_nodes_book(path, i))

    index = dict()
    for i in range(len(result)):
        for j in range(len(result[i])):
            index[result[i][j]] = i

    liste_galaxies = get_list_galaxie(path)

    matrix = np.zeros([len(t), len(liste_galaxies)])

    dirGalaxies = shelve.open(path + '/BDs/listeGalaxies')

    for galaxie in range(len(liste_galaxies)):
        for node in dirGalaxies[str(liste_galaxies[galaxie])]:
            matrix[index[node]][galaxie] += 1
        
        matrix[:,galaxie] = matrix[:,galaxie] / len(dirGalaxies[str(liste_galaxies[galaxie])])

    dirGalaxies.close()
    
    label = np.array([i for i in range(len(t))])
    tsne = TSNEVisualizer(decompose='svd',decompose_by=15)
    tsne.fit(matrix, label)
    print(tsne.transformer_)
    tsne.poof()

    svd = TruncatedSVD(n_components=15)
    svd_matrix = svd.fit_transform(matrix)
    tsne = ts.TSNE()
    y = tsne.fit_transform(svd_matrix)
    kmeans = Kmeans(5,200,0.1)
    kmeans.fit(y)
    for i in range(kmeans.nb_cluster):
        print("Cluster ",i)
        print((np.where(kmeans.which_cluster == i))[0])
        print()
    plt.scatter(y[:, 0], y[:, 1], c=kmeans.which_cluster.reshape(-1,1), s=50, cmap='viridis')
    plt.title("Resultat du clustering")
    plt.savefig("clustering")
    plt.show()
