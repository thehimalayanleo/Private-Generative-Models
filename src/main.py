# -*- coding: utf-8 -*-
"""Private-EM-Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1AjZlnd3GQl4Iowqx5-abxWh2eq6462Su
"""

# Import Libraries
import numpy as np
import matplotlib.pyplot as plt
import csv
import random

import sklearn
from sklearn.cluster import KMeans
!pwd
!pip install hmmlearn

## PRIVATE
from copy import deepcopy
N_classes = 3

fpath = "/content/HMMdata.csv"

def file_reader(fpath):
  filep = open(fpath, 'rt')
  reader = csv.reader(filep, delimiter=',')
  return np.array(list(reader))

data = file_reader(fpath)
data = data.astype(np.float64)

colormap = np.array(['r', 'g', 'b'])
X = np.array(list(map(int, data[:, 0])))
Y = np.array(data[:, 1:])
print(Y.shape)
y1, y2 = np.array(data[:, 1]), np.array(data[:, 2])
plt.scatter(y1, y2, c=colormap[X])
plt.title('Data divided by classes')
plt.show()

from math import pow, sqrt, log
def add_noise_gaussian(eps, delta, sensitivity, size=1):
    # Add 1D noise to data
    # Need to precalculate per data epsilon value
    constant = np.sqrt(2*np.log(1.25/delta))
    sigma = (constant*sensitivity)/eps
    #print('std:', sigma, 'Noise:', np.random.normal(loc=0, scale=sigma))
    if size == 1:
        return np.random.normal(loc=0, scale=sigma, size=size)[0]
    #elif type(size) == int:
    return np.random.normal(loc=0, scale=sigma, size=size)
    #else:

    #elif len(size) > 1:
    #    return np.random.normal(loc=0, sigma=sigma, )

def add_noise(eps, delta, sensitivity, size=1):
    #constant = np.sqrt(2*np.log(1.25/delta))
    sigma = sensitivity/eps
    if size == 1:
        return np.random.laplace(loc=0, scale=sigma, size=size)[0]
    #elif type(size) == int:
    return np.random.laplace(loc=0, scale=sigma, size=size)
    #else:

# Test Noise
x = 1
print(x, x+add_noise(eps=1, delta=0.01, sensitivity=1))
y = np.array([1, 2])
print(y, y+add_noise(eps=1, delta=0.01, sensitivity=1, size=2))
z = np.array([[1, 2], [3, 4]])
print(z, add_noise(eps=1, delta=0.01, sensitivity=1, size=(2, 2)))

def clip(x, bound):
    den = max(1, np.linalg.norm(x, 1)/bound)
    output = x/den
    #print('Output Norm:', np.linalg.norm(output))
    return output

def clip_gaussian(x, bound):
    den = max(1, np.linalg.norm(x)/bound)
    output = x/den
    #print('Output Norm:', np.linalg.norm(output))
    return output

print(np.linalg.norm(clip(y, 1), 1))

from math import exp, log
def advanced_composition(eps, delta, iterations):
    delta_prime = delta
    term1=iterations*eps*(exp(eps)-1)
    term2=eps*sqrt(2*iterations*log(1/delta_prime))

    return term1+term2, iterations*delta+delta_prime # eps, delta

advanced_composition(0.1, 0.005, 24)

# Privatized K-Means with Gaussian Noise
from copy import deepcopy
class private_KMeans:
    def __init__(self, data, Y_main, X, N_classes, d, tol=0.01, private=False, clip_bound = 4, eps = 1, delta = 1./200, max_iters=10):
        self.N_classes = N_classes # no. of classes
        self.data = data # complete
        self.tol = tol # tolerance for convergence
        self.N = Y.shape[0] # No of samples
        self.Y = deepcopy(Y_main) # data
        self.X = X # labels
        self.clip_bound = clip_bound
        self.d = d # dimensions of the data
        self.private = private # do we want to privatize?
        self.prev_centroids = None
        self.max_iters = max_iters # maximum iterations until convergence
        self.privacy_cost = {'eps':0.0, 'delta':0.0}
        self.privacy_counts = 0
        self.eps = eps
        self.delta = delta
        self.Y_original = deepcopy(self.Y)
        self.priors = np.zeros(self.N_classes)

        # Randomly initialize centroids
        # TODO: Matters a lot
        self.centroids = np.array([np.random.uniform(-self.clip_bound/self.d, self.clip_bound/self.d, self.d) for _ in range(self.N_classes)])
        if self.private:
            for k in range(self.N_classes):
                self.centroids[k, :] = deepcopy(clip_gaussian(self.centroids[k, :], self.clip_bound))
        #self.centroids = Y[np.random.choice(range(X.shape[0]), replace = False, size = self.N_classes), :]
        print('Initialization')
        print(self.centroids)

    

    def run(self):

        if self.private: #PRIVATE
            for n in range(self.N):
                self.Y[n] = deepcopy(clip_gaussian(self.Y[n], self.clip_bound))

            plt.figure()
            plt.scatter(self.Y[:, 0], self.Y[:, 1])
            plt.title('Clipped with norm bound:'+str(self.clip_bound))
            plt.show()

        for iterations in range(self.max_iters):
            votes = []
            for n in range(self.N): # This can be done privately
                distances = []
                for k in range(self.N_classes):
                    distances.append(np.linalg.norm(self.Y[n]-self.centroids[k, :]))
                votes.append(distances.index(min(distances))) # vote on the centroid which data n chooses

            #print(votes)

            # Get new centroids
            self.prev_centroids = deepcopy(self.centroids)

            for k in range(self.N_classes): 
                num = 0.
                den = 0.
                for n in range(self.N):
                    if votes[n] == k:
                        num+=self.Y[n]
                        den+=1
                
                #sensitivity_num = np.sqrt(self.clip_bound)
                sensitivity_num = self.clip_bound
                sensitivity_den = 1
                if self.private: #PRIVATE
                    num += add_noise_gaussian(self.eps, self.delta, sensitivity=sensitivity_num, size=self.d)
                    den += add_noise_gaussian(self.eps, self.delta, sensitivity=sensitivity_den, size=1) # only add positive noise
                    self.privacy_counts+=(1+self.d)
                self.priors[k]=den/self.N
                #privacy_cost['eps']+=2*self.eps
                #privacy_cost['delta']+=2*self.delta
                #print('NUM/DEN', num, den)

                if den > 0:
                    #print('ZERO')
                    self.centroids[k, :] = num/den 
                else:
                    self.centroids[k, :] = num

                if self.private:
                    for k in range(self.N_classes):
                        self.centroids[k, :] = deepcopy(clip_gaussian(self.centroids[k, :], self.clip_bound))
                # else centroids do not change
            #print('Old', self.prev_centroids)
            #print('New', self.centroids)
            # Stopping Condition
            if iterations > 2 and np.linalg.norm(self.centroids-self.prev_centroids) < self.tol:
                print('Iterations Required:', iterations+1)
                print('KMeans Converged')
                break
        if iterations == self.max_iters-1:
            print('Maximum Iterations Done')
            print('Iterations Required:', iterations+1)

        kmeans = KMeans(N_classes).fit(self.Y_original)
        means = kmeans.cluster_centers_

        # Compute priors
        #self.priors = 

        #if self.private:

        #print(means)
        #print(self.centroids)

        if self.private:
            e, d = advanced_composition(self.eps, self.delta, self.privacy_counts)
            print('Total eps/delta', min(e, self.privacy_counts*self.eps), min(d, self.privacy_counts*d))
            print('Total privacy mechanisms', self.privacy_counts)

        plt.figure()
        y1, y2 = np.array(self.data[:, 1]), np.array(self.data[:, 2])
        plt.scatter(y1, y2, c=colormap[X], alpha=0.2)
        plt.scatter(means[:, 0], means[:, 1], s=200, c='m', marker='X', label='In-Built Function')
        plt.scatter(self.centroids[:, 0], self.centroids[:, 1], s=200, c='c', marker='^', label='Simulation')
        plt.title('KMeans: Data divided by classes')
        plt.legend()
        plt.show()

kmeans = private_KMeans(data, Y, X, N_classes=3, d=2, tol=0.00001, private=False, max_iters=20)
kmeans.run()

#print(Y.shape)
#plt.scatter(Y[:, 0], Y[:, 1])
#plt.show()

print('Epsilon: 1')
kmeans = private_KMeans(data, Y, X, N_classes=3, d=2, tol=0.00001, private=True, clip_bound = 3, eps = 1, delta = 1./200, max_iters=4)
kmeans.run()
print('Priors', kmeans.priors)
#plt.scatter(Y[:, 0], Y[:, 1])
#plt.show()

print('Epsilon: 0.5')
kmeans = private_KMeans(data, Y, X, N_classes=3, d=2, tol=0.00001, private=True, clip_bound = 3, eps = 0.5, delta = 1./200, max_iters=4)
kmeans.run()
print('Priors', kmeans.priors)

#plt.scatter(Y[:, 0], Y[:, 1])
#plt.show()

print('Epsilon: 0.2')
kmeans = private_KMeans(data, Y, X, N_classes=3, d=2, tol=0.00001, private=True, clip_bound = 3, eps = 0.2, delta = 1./200, max_iters=4)
kmeans.run()
print('Priors', kmeans.priors)

print('Epsilon: 0.1')
kmeans = private_KMeans(data, Y, X, N_classes=3, d=2, tol=0.00001, private=True, clip_bound = 3, eps = 0.1, delta = 1./200, max_iters=4)
kmeans.run()
print('Priors', kmeans.priors)

# Original GMM 


'''
Expectation Maximization for the Gaussian Mixture Models.

'''

class GMM_EM:
    def __init__(self, N_classes, data, Y_main, X, d=2, max_iters = 5, private=False, clip_bound = 4, eps = 1, delta = 0.01, tol=0.01):
        # K-Means clustering to get centers for mean estimation
        kmeans = KMeans(N_classes).fit(Y)
        labels = kmeans.labels_
        data0 = Y[np.where(labels==0), :][0]
        data1 = Y[np.where(labels==1), :][0]
        data2 = Y[np.where(labels==2), :][0]
        self.max_iters = max_iters
        self.Y = np.array(deepcopy(Y_main), dtype=np.float128)
        self.d = d
        self.tol = tol
        self.N_classes = N_classes
        self.N = Y.shape[0]

        # ----------------------------------------
        # PRIVACY PARAMETERS
        # ----------------------------------------

        self.private = private
        self.privacy_counts = 0
        self.eps = eps
        self.delta = delta
        self.clip_bound = clip_bound

        # ----------------------------------------
        # CLIP DATA
        # ----------------------------------------

        if self.private: # CLIP DATA TO REDUCE SENSITIVITY
            for n in range(self.N):
                self.Y[n] = deepcopy(clip(self.Y[n], self.clip_bound))

        # ----------------------------------------
        # Initialize parameters
        # ----------------------------------------

        if self.private == False: # NON-PRIVATE PERFECT K-Means Initializatino
            self.means = np.array(kmeans.cluster_centers_, dtype=np.float128)
            self.covs = np.array([np.cov(data0.T), np.cov(data1.T), np.cov(data2.T)], dtype=np.float64)
            self.priors = np.array([list(labels).count(label)/len(labels) for label in range(N_classes)],dtype=np.float128)
        else: # Initialize privately
            print('Epsilon: 0.2')
            kmeans_private = private_KMeans(data, Y, X, N_classes=self.N_classes, d=self.d, tol=self.tol, 
                                            private=self.private, clip_bound = self.clip_bound, 
                                            eps = self.eps, delta = self.delta, max_iters=self.max_iters)
            kmeans_private.run()
            #print('Priors', kmeans.priors)
            print('Private KMeans DONE!')
            self.means = np.array(kmeans_private.centroids, dtype=np.float128)
            self.priors = np.array(kmeans_private.priors, dtype=np.float128)
            self.privacy_counts+=kmeans_private.privacy_counts # Add KMeans previous counts

        
            self.covs = np.array([np.eye(self.d)*np.random.random(self.d) for _ in range(self.N_classes)])
            for k in range(self.N_classes):
                diff_k = self.Y-self.means[k, :] 
                self.privacy_counts+=self.d
                samples_k = self.priors[k]*self.N #PRIVATE

                num_cov=(diff_k.T.dot(diff_k))
                if self.private:
                    num_cov+=add_noise(self.eps, self.delta, sensitivity=self.clip_bound**2, size=(self.d, self.d))
                    num_cov=np.abs(num_cov)
                    self.privacy_counts+=(self.d*(self.d+1))/2.

                #self.covs[]
                self.covs[k, :] = num_cov/samples_k # COMPUTE INITIAL COVARIANCE MATRIX


        
    # COMPUTE LOG LIKELIHOOD LOSS
    def log_likelihood_loss(self): # TODO: ASSUMED PRIVATE
        ll = 0.
        for n in range(self.N):
            ll_n = 0.
            for k in range(self.N_classes):
                pi_k, mu_k, sigma_k = self.priors[k], self.means[k, :], self.covs[k, :]
                ll_n += pi_k*self.normal_pdf(self.Y[n], k)*self.priors[k]
            ll+=np.log(ll_n)
        return ll

    def normal_pdf(self, x, k): # done on device so ignore
        mu_k, sigma_k = self.means[k, :], self.covs[k, :]
        try:
            sigma_k_inv = np.float128(np.linalg.inv(sigma_k))
            if np.linalg.det(sigma_k) <= 0:
                print('Problem with determinant')
                self.covs[k, :] = np.eye(self.d)*np.random.random(self.d)
                sigma_k = self.covs[k, :]
                print('Sigma:', sigma_k)
                print('Determinant:', np.linalg.det(sigma_k))
            constant = 1/np.sqrt(((2*np.pi)**len(x))*np.linalg.det(sigma_k))
        except np.linalg.LinAlgError:
            print('Singular Value Error')
            self.covs[k, :] = np.eye(self.d)*np.random.random(self.d)
            sigma_k = self.covs[k, :]
            if np.linalg.det(sigma_k) <= 0:
                print('Problem with determinant')
                self.covs[k, :] = np.eye(self.d)*np.random.random(self.d)
                sigma_k = self.covs[k, :]
                print('Sigma:', sigma_k)
                print('Determinant:', np.linalg.det(sigma_k))
            sigma_k_inv = np.float128(np.linalg.inv(sigma_k)) 
            print('Inv Sigma:', sigma_k_inv)
            constant = np.float128(1/np.sqrt(((2*np.pi)**len(x))*np.linalg.det(sigma_k)))
        #print(np.float128(-0.5*np.dot(np.dot((x-mu_k).T, sigma_k_inv), (x-mu_k))))
        return constant*np.exp(np.float128(-0.5*np.dot(np.dot((x-mu_k).T, sigma_k_inv), (x-mu_k))))

    def compute_gamma(self, n, k): #r_nk value
        # done on device
        num = self.normal_pdf(self.Y[n], k)*self.priors[k]
        den = sum([self.normal_pdf(self.Y[n], k)*self.priors[k] for k in range(self.N_classes)])
        return num/den

    def E_step(self):
        # Calculate gammas
        # can be done on device
        proba = []
        for n in range(self.N):
            proba_k = []
            for k in range(self.N_classes):
                proba_k.append(self.compute_gamma(n, k))
            proba.append(proba_k)

        return np.array(proba, dtype=np.float64)

    def M_step(self, proba):
        samples = np.sum(proba, axis=0)
        if self.private:
            for k in range(N_classes):
                samples[k]+=add_noise(self.eps, self.delta, sensitivity=1, size=1)
                samples[k]=np.abs(samples[k])
                self.privacy_counts+=1

        for k in range(N_classes):
            data = self.Y 
            gammas = np.squeeze(proba[:, k])
            num_mean = (gammas.T.dot(data).flatten())

            if self.private:
                num_mean+=add_noise(self.eps, self.delta, sensitivity=self.clip_bound, size=self.d)
                self.privacy_counts+=self.d

            self.means[k, :] = num_mean/samples[k] 
            mu_k = self.means[k, :]

            diff_k = np.subtract(data, mu_k) 

            num_cov=(diff_k.T.dot(diff_k*gammas[..., np.newaxis]))
            if self.private:
                num_cov+=add_noise(self.eps, self.delta, sensitivity=self.clip_bound**2, size=(self.d, self.d))
                self.privacy_counts+=(self.d*(self.d+1))/2.
                
            self.covs[k, :] = num_cov/samples[k]
            self.priors[k] = samples[k]/np.sum(samples)

    def run_EM(self):

        

        lls = []
        for iterations in range(self.max_iters):
            proba = self.E_step() 
            self.M_step(proba)
            ll = self.log_likelihood_loss()
            print('LL', ll)
            lls.append(ll)

            if len(lls) > 2 and np.abs(lls[-1]-lls[-2]) < self.tol:
                print('GMM Converged!')
                break

        if self.private:
            e, d = advanced_composition(self.eps, self.delta, self.privacy_counts)
            print('Total eps/delta', min(e, self.privacy_counts*self.eps), min(d, self.privacy_counts*d))
        print('No. of Iterations required:', iterations+1)
        plt.figure()
        plt.title('Log Likelihood Loss over iterations')
        plt.xlabel('Iterations')
        plt.ylabel('Log Likehood Loss')
        plt.plot(range(len(lls)), lls)
        plt.show()

from sklearn.preprocessing import Normalizer
transformer = Normalizer().fit(Y)
Y_scaled1 = transformer.transform(Y)

colormap = np.array(['r', 'g', 'b'])
y1, y2 = np.array(Y[:, 0]), np.array(Y[:, 1])
plt.scatter(y1, y2, c=colormap[X])
plt.title('Data divided by classes')
plt.show()

#for y in Y_scaled:
#    print(np.linalg.norm(y))

gmm_em_private = GMM_EM(N_classes, data, Y, X, d=2, max_iters = 7, private=True, clip_bound = 4, eps = 2, delta = 1./200, tol=0.0001)
gmm_em_private.run_EM()
print('Final Private Parameters')
print(gmm_em_private.means)
print(gmm_em_private.covs)
print(gmm_em_private.priors)
proba_sim_private = gmm_em_private.E_step()
proba_labels_sim_private = np.argmax(proba_sim_private, 1)
print('Accuracy:', np.mean(np.argmax(proba_sim_private, 1) ==  X))

# Private

#print(proba_sim_private)
print(np.argmax(proba_sim_private, 1))

print('Simualted with eps:', 0.2)
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim_private)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

gmm_em_private = GMM_EM(N_classes, data, Y, X, d=2, max_iters = 7, private=True, clip_bound = 4, eps = 1, delta = 1./200, tol=0.0001)
gmm_em_private.run_EM()
print('Final Private Parameters')
print(gmm_em_private.means)
print(gmm_em_private.covs)
print(gmm_em_private.priors)
proba_sim_private = gmm_em_private.E_step()
proba_labels_sim_private = np.argmax(proba_sim_private, 1)
print('Accuracy:', np.mean(np.argmax(proba_sim_private, 1) ==  X))

# Private

#print(proba_sim_private)
print(np.argmax(proba_sim_private, 1))

print('Simualted with eps:', 0.2)
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim_private)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

gmm_em_private = GMM_EM(N_classes, data, Y, X, d=2, max_iters = 7, private=True, clip_bound = 4, eps = 0.5, delta = 1./200, tol=0.0001)
gmm_em_private.run_EM()
print('Final Private Parameters')
print(gmm_em_private.means)
print(gmm_em_private.covs)
print(gmm_em_private.priors)
proba_sim_private = gmm_em_private.E_step()
proba_labels_sim_private = np.argmax(proba_sim_private, 1)
print('Accuracy:', np.mean(np.argmax(proba_sim_private, 1) ==  X))

# Private

#print(proba_sim_private)
print(np.argmax(proba_sim_private, 1))

print('Simualted with eps:', 0.2)
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim_private)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

gmm_em_private = GMM_EM(N_classes, data, Y, X, d=2, max_iters = 7, private=True, clip_bound = 4, eps = 0.2, delta = 1./200, tol=0.0001)
gmm_em_private.run_EM()
print('Final Private Parameters')
print(gmm_em_private.means)
print(gmm_em_private.covs)
print(gmm_em_private.priors)
proba_sim_private = gmm_em_private.E_step()
proba_labels_sim_private = np.argmax(proba_sim_private, 1)
print('Accuracy:', np.mean(np.argmax(proba_sim_private, 1) ==  X))

# Private

#print(proba_sim_private)
print(np.argmax(proba_sim_private, 1))

print('Simualted with eps:', 0.2)
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim_private)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

# Try with a random initialization, Gives poor results & takes way longer
N_classes = 3
gmm_em = GMM_EM(N_classes, data, Y, X, d=2, max_iters=100, tol=0.0001)
n_classes, d = 3, 2
P = np.random.random(n_classes)
gmm_em.priors = P/np.sum(P)
#gmm_em.priors = np.array([1./n_classes for _ in range(n_classes)])
print(gmm_em.priors)
gmm_em.means = np.random.uniform(-20, 20, n_classes*d).reshape(n_classes, d)
gmm_em.covs = np.array([np.eye(d)*np.random.random(d) for _ in range(n_classes)])
#print(np.eye(d)*np.random.uniform(1, 10, 2))
gmm_em.run_EM()
print('Final Parameters')
print(gmm_em.means)
print(gmm_em.covs)
print(gmm_em.priors)
proba_sim = gmm_em.E_step()
proba_labels_sim = np.argmax(proba_sim, 1)
print('Accuracy:', np.mean(np.argmax(proba_sim, 1) ==  X))

colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

N_classes = 3
gmm_em = GMM_EM(N_classes, data, Y, X, d=2, max_iters=7)
gmm_em.run_EM()
print('Final Parameters')
print(gmm_em.means)
print(gmm_em.covs)
print(gmm_em.priors)
proba_sim = gmm_em.E_step()
proba_labels_sim = np.argmax(proba_sim, 1)
print(np.mean(np.argmax(proba_sim, 1) ==  X))



print('True Parameters')
from sklearn.mixture import GaussianMixture
gm = GaussianMixture(n_components=3)
gm = gm.fit(Y)
print(gm.means_)         
print(gm.covariances_)
print(gm.weights_)
print(gm.converged_)
print('Iters Required', gm.n_iter_)
proba_sklearn = gm.predict_proba(Y)
proba_labels_sklearn = np.argmax(proba_sklearn, 1)
print(np.mean(np.argmax(proba_sklearn, 1) ==  X))

# In-Built
print('In-Built')
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sklearn)))

plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (sklearn)')
plt.show()

# True simulation
print('Simulation')
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

eps_model = 4.5
# Private Last Model
counts = 0
b = 3
for k in range(3):
    gmm_em.means[k, :] = clip_gaussian(gmm_em.means[k, :], b)
    gmm_em.covs[k, :] = clip_gaussian(gmm_em.covs[k, :], b**2)
    gmm_em.means[k, :]+=add_noise(eps_model, 1./200, sensitivity=b, size=2)
    gmm_em.priors[k]+=(add_noise(eps_model, 1./200, sensitivity=1, size=1))
    gmm_em.covs[k, :]+=(add_noise(eps_model, 1./200, sensitivity=b**2, size=(2, 2)))
    counts+=6
gmm_em.priors = np.abs(gmm_em.priors)
#gmm_em.covs = np.abs(gmm_em.covs)
gmm_em.priors/=np.sum(gmm_em.priors)
print(counts)
eps1, delta1 = advanced_composition(eps_model, 1./200, counts)
print('Privacy Budget:', min(counts*eps_model, eps1), min(1./200*counts, delta1))

proba_sim_private = gmm_em.E_step()
proba_labels_sim_private = np.argmax(proba_sim_private, 1)
print(np.mean(np.argmax(proba_sim_private, 1) ==  X))

# True simulation
print('Simulation Private')
colormap = np.array(['r', 'g', 'b'])
lab = np.array(list(map(int, proba_labels_sim_private)))
plt.scatter(y1, y2, c=colormap[lab])
plt.title('Data divided by classes (simulation)')
plt.show()

