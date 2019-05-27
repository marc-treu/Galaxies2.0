import numpy as np
import sqlite3
import shelve

from sklearn.manifold import TSNE
import matplotlib.pyplot as plt


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
    dirNode = shelve.open(project_path + '/BDs/listeNodes')

    for id_galaxie in list_galaxie:
        for node in dirGalaxies[id_galaxie]:
            dirNode[str(node)] = id_galaxie

    dirGalaxies.close()
    dirNode.close()

if __name__ == '__main__':
    path = "/home/marc/Desktop/PLDAC/Galaxies/projects/Balzac"

    # liste_galaxie = get_list_galaxie(path)
    # print([liste_galaxie])
    # inverse_bd(path,liste_galaxie)

    t = get_books(path)
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

    X = np.matrix([[5, 0, 0], [4, 0, 0], [3, 0, 0], [2, 0, 0]])
    X = np.matrix([[0, 1, 0],
                   [1, 0, 0],
                   [0, 1, 0],
                   [1, 0, 1],
                   [0, 1, 0],
                   [1,0,0],
                   [0,2,0],
                   [2,0,1],
                   [0,1,0],
                   [0,1,0]])

    Y = np.array(([1,2,1,2,3,2,1,2,1,3]))
    tsne = TSNE(n_components=2, verbose=1)
    res = tsne.fit_transform(X)
    print(res)
    plt.scatter([res[i]], Y)
    plt.show()
    plt.close()