import numpy as np


class TSNE(object):
    """ perplexity : correspond au k-neighbors à considerer
        epsilon correspond à l'ecart type
    """ 
    
    def __init__(self, perplexite=20, sigma=1, learn_rate=200, iteration=5000, momuntum=0.99):
        self.perplexite = perplexite
        self.sigma = sigma
        self.learn_rate = learn_rate
        self.iteration = iteration
        self.momuntum = momuntum
        self.matrice = None
        self.matrice_reduite = None


    #fonction qui pour chaque point xi retourne ses k-voisin
    def k_neighbors(self, i, heigh_dim=True):
        distance = []
        if heigh_dim :
            xi = self.matrice[i]
            for j in range(self.matrice.shape[0]):
                if i != j :
                    xj = self.matrice[j]
                    d = np.exp(-np.linalg.norm(xi-xj)**2/(2*self.sigma**2))
                    distance.append(d)

        else :
            yi = self.matrice_reduite[i]
            for j in range(self.matrice_reduite.shape[0]):
                if i != j :
                    yj = self.matrice_reduite[j]
                    d = (1 + np.linalg.norm(yi-yj)**2)**(-1)
                    distance.append(d)

        distance = np.sort(distance)
        return distance[:self.perplexite]


    
    #fonction qui calcule la similarite entre xi et xj dans l'espace original
    def proba_pij(self,i,j):
        xi = self.matrice[i]
        xj = self.matrice[j]
        d = np.exp(-np.linalg.norm(xi-xj)**2)/(2*self.sigma**2)
        voisin_xi = self.k_neighbors(i)
        somme_d = np.sum(voisin_xi)
        return d/somme_d



    #fonction qui calcule la similarite entre xi et xj dans le nouvel espace original
    def proba_qij(self,i,j):
        yi = self.matrice_reduite[i]
        yj = self.matrice_reduite[j]
        d = (1 + np.linalg.norm(yi-yj)**2)**(-1)
        voisin_yi = self.k_neighbors(i,heigh_dim=False)
        somme_d = np.sum(voisin_yi)
        return d/somme_d


    #la matrice des p des xij dans l'espace original 
    def matrice_p(self):
        dim = self.matrice.shape[0]
        matrice = np.zeros((dim,dim))
        for i in range(dim):
            for j in range(dim):
                if i!=j:
                    pij = self.proba_pij(i,j)
                    pji = self.proba_pij(j,i)
                    matrice[i][j] = np.divide((pij+pji),2*dim)

        return matrice


    #la matrice des q des xij dans l'espace reduit 
    def matrice_q(self):
        dim = self.matrice.shape[0]
        matrice = np.zeros((dim,dim))
        for i in range(dim):
            for j in range(dim):
                if i!=j:
                    matrice[i][j] = self.proba_qij(i,j)

        return matrice
    
    
        
    def kl_divergence(self,p,q):
        with np.errstate(divide='ignore'):
            div = np.divide(p, q)
            div[q==0] = 0
        
        logarithm = np.ma.log(div)
        res = logarithm.filled(0)
        produit = p*res
        return np.sum(produit)


    """
    def descente_gradient(self,p):
        colonne = self.matrice_reduite.shape[1]
        ligne = self.matrice_reduite.shape[0]
        histo_y = np.zeros((ligne,2,colonne))
        for epoque in range(self.iteration):
            q = self.matrice_q()
            pq= p-q
            for i in range(ligne):
                gradient = 0
                temp = self.matrice_reduite[i] - self.matrice_reduite
                for j in range(ligne):
                    gradient += (self.matrice_reduite[i]-self.matrice_reduite[j]) * (pq[i][j]) * (1+np.linalg.norm(self.matrice_reduite[i]-self.matrice_reduite[j])**2)**(-1)
                self.matrice_reduite[i] = histo_y[i][1] - self.learn_rate * 4 * gradient + self.momuntum * (histo_y[i][1]-histo_y[i][0])
                histo_y[i][0] = histo_y[i][1]
                histo_y[i][1] = self.matrice_reduite[i]
            #if epoque%100==0:
            print(self.kl_divergence(p,q))"""

       

    
    def descente_gradient(self,p):
        colonne = self.matrice_reduite.shape[1]
        ligne = self.matrice_reduite.shape[0]
        histo_y = np.zeros((ligne,2,colonne))
        for epoque in range(self.iteration):
            q = self.matrice_q()
            pq= p-q
            for i in range(ligne):
                temp = self.matrice_reduite[i] - self.matrice_reduite
                gradient = np.sum(temp * pq[i].reshape(-1,1) * ((1+np.linalg.norm(temp,axis=1)**2)**(-1)).reshape(-1,1),axis=0)
                self.matrice_reduite[i] = histo_y[i][1] - self.learn_rate * 4 * gradient + self.momuntum * (histo_y[i][1]-histo_y[i][0])
                histo_y[i][0] = histo_y[i][1]
                histo_y[i][1] = self.matrice_reduite[i]
            #if epoque%100==0:
            #print(self.kl_divergence(p,q))

        self.matrice_reduite -= np.mean(self.matrice_reduite)
        self.matrice_reduite /= np.std(self.matrice_reduite)

    def fit_transform(self, x):
        self.matrice = x
        self.matrice_reduite = np.random.normal(0,0.001,(x.shape[0],2))
        p = self.matrice_p()
        self.descente_gradient(p)
        return self.matrice_reduite



    
if __name__ == '__main__':

    tsne = TSNE(perplexite=3,iteration=50)
    #x = np.random.rand(100,30)
    x = np.array([[1,1,0,0,0,0],
                  [0.9,0.9,0,0,0,0],
                  [0.6,0.7,0,0,0,0],
                  [0.5,0.5,0,0,0,0],
                  [0.5,0.5,0.5,0,0,0],
                  [0,0,0,0,0.5,0.5],
                  [0,0,0,0,0,1],
                  [0,0,0,0,1,1],
                  [0,0,0,0,0.5,1],
                  [0,0,0,0,0.2,1]])
    y = tsne.fit_transform(x)
    print(y)
