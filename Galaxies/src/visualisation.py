import numpy as np
import sqlite3
import shelve

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
from yellowbrick.text import TSNEVisualizer


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

    # liste_galaxie = get_list_galaxie(path)
    # print([liste_galaxie])
    # inverse_bd(path,liste_galaxie)

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

    print("index =", index)
    print("matrix =", matrix)
    print("result =", result)
    print("liste_galaxies =", liste_galaxies)

    dirGalaxies = shelve.open(path + '/BDs/listeGalaxies')

    for galaxie in range(len(liste_galaxies)):
        for node in dirGalaxies[str(liste_galaxies[galaxie])]:
            matrix[index[node]][galaxie] = 1

    dirGalaxies.close()
    print("matrix =", matrix)

    label = np.array([i for i in range(len(t))])

    tsne = TSNEVisualizer(decompose_by=20)
    tsne.fit(matrix, label)
    tsne.poof()





    # print(t[0])
    # # print(sum([(len(get_id_nodes_book(path, i))) for i in range(len(t))])/len(t))
    # d =get_id_nodes_book(path, 36)
    # print(d)
    # print(t)
    # livre = dict()
    # for i in range(len(t)):
    #     print(i)
    #     res = []
    #     for j in get_id_nodes_book(path, i):
    #         # print(j)
    #         res.append(get_galaxie_from_id_node(path, j))
    #     livre[i] = set(res)
    # print(livre)
    #
    # X = np.matrix([[5, 0, 0], [4, 0, 0], [3, 0, 0], [2, 0, 0]])
    # X = np.matrix([[0, 1, 0],
    #                [1, 0, 0],
    #                [0, 1, 0],
    #                [1, 0, 1],
    #                [0, 1, 0],
    #                [1,0,0],
    #                [0,2,0],
    #                [2,0,1],
    #                [0,1,0],
    #                [0,1,0]])
    #
    # Y = np.array(([1,2,1,2,3,2,1,2,1,3]))
    # tsne = TSNE(n_components=2, verbose=1)
    # res = tsne.fit_transform(X)
    # print(res)
    # plt.scatter([res[i]], Y)
    # plt.show()
    # plt.close()
