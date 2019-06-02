#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib.pyplot as plt
import numpy as np
import scipy.spatial.distance


class Kmeans():
    
    def __init__(self, nombre_cluster,nb_it,eps):
        """
            eps : petit nombre critère de convergence 
            nb_it : nombre d'itérations max
            
        """
        self.nb_cluster = nombre_cluster
        self.eps = eps
        self.nb_it = nb_it
        self.which_cluster = None
        self.cluster = None
        

    def calcul_baricentre(self,data):
        for i in range (self.nb_cluster):
            points_cluster = data[self.which_cluster == i]
            if len(points_cluster)!=0:
                self.cluster[i]=np.mean(points_cluster,axis=0) 


                
    def fit(self, data):
        self.cluster =np.random.rand(self.nb_cluster,data.shape[1])
        self.which_cluster = np.zeros((len(data),))
        for i in range(self.nb_it):
            d = scipy.spatial.distance.cdist(data,self.cluster,metric='euclidean')
            ind_clust = np.argmin(d,axis=1)
            self.which_cluster = ind_clust
           
            tmp = self.cluster.copy()
            self.calcul_baricentre(data)
            
            if np.absolute(np.sum(tmp-self.cluster)) < self.eps:
                break

            
    def predict(self,data):
        """
            À voir s'il y a besoin.
        """
        which_cluster = []
        
        
        d = scipy.spatial.distance.cdist(data,self.cluster,metric='euclidean')
        ind_clust = np.argmin(d,axis=1)
        for i in ind_clust:
            which_cluster.append(self.cluster[i])
        return np.array(which_cluster)
            
        


if __name__ == '__main__':
    x = np.array([[1,1,0,0,0,0],
                  [0.9,0.9,0,0,0,0],
                  [0.6,0.7,0,0,0,0],
                  [0.5,0.5,0,0,0,0],
                  [0.5,0.5,0.5,0,0,0],
                  [0,0,0,0,0.5,0.5],
                  [0,0,0,0,0,1],
                  [0,0,0,0,1,1],
                  [0,0,0,0,0.5,1],
                  [1,0,0,0,0,0]])
     
    kmeans = Kmeans(2,200,0.1)
    kmeans.fit(x)
    print(kmeans.which_cluster)
    
