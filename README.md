# Private Generative Models
Final Project for ECE695 (Generative Models) at Purdue. Scalable Implementations of Locally Differentially Private:
- KMeans
- Gaussian Mixture Model (GMM)

## Future Work:
- Hidden Markov Model
- Restricted Boltzmann Machines
- Scale to image datasets

We assume a basic understanding of Expectation-Maximization Algorithm and Differential Privacy (DP):
1. DP Reference (specifically Gaussian Mechanism on Pg. 261): https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf

## Implementation Details Building Blocks:
1. Local Differential Privacy: Each data-point belongs to a single user & we add noise to maintain privacy accordingly.
2. K-Means: We run experiments on GMM to test if it performs well with random initialization. Unfortunately, it does not. So, we implement private K-Means to find a good inital point (priors, means & covariance matrices) for our GMM.
3. Expectation Maximization (EM): EM depends on finding the optimal priors, means and covariances. This happens on every iteration. Therefore, unless we perturb our entire dataset, private EM depends on us adding noise to these parameters per iteration & thus privacy scales with iterations.
4. Composition Theorem for Differential Privacy: We measure privacy in the differential privacy domain with epsilon, delta. As we have multiple iterations & multiple mechanisms we compute the total privacy cost (to understand our privacy budget) using the regular composition theorem as well as the k-iterations adaptive composition theorem and take the minimum of both.
5. Hyperparameters: We control privacy using multiple tunable parameters: A. No. of iterations, B. Data clipping (norm-based) to control sensitivity, C. Epsilon, D. Delta (Fixed), E. Type of privacy (Local or Central)
6. Extra Points: 
  - A privacy budget of single digit is required for any meaningful privacy so anything beyond that will significantly destory user privacy. 
  - Furthermore, our data is only 2D and thus the dimensionality does not add a significant burden on our privacy costs
  - Data vizualization & ability to tune results helps us get better results than in practice
  - The dataset used is present in the data folder & the code is in Jupyter Notebook
  - Both the private/non-private and randomly initialized K-Means and GMM Models are available

## Results:

NOTE: We use the sklearn implementations as our baselines along with our own implementations.

- Initial Data with given labels:
![Initial Available Data](https://github.com/thehimalayanleo/Private-Generative-Models/blob/main/results/initial-data.png)

1. K-Means:

To reduce the privacy cost (by reducing the sensitvity) we clip the data to a sphere of radius 3 shown next.

![Clipped Data](https://github.com/thehimalayanleo/Private-Generative-Models/blob/main/results/clipped-data-norm-3.png)

Next we show all the non-private/private KMeans superimposed on the accurate sklearn KMeans.

![KMeans](https://github.com/thehimalayanleo/Private-Generative-Models/blob/main/results/KMeans.png)


2. GMM:

NOTE: Here, we combine the privacy costs of the K-Means with our GMM implementation & we only report the best fit. Depending on randomness & certain hyperparameters the results may vary, but the results presented are true on an average.

![GMM](https://github.com/thehimalayanleo/Private-Generative-Models/blob/main/results/GMM.png)

## Contributions:
This repository is currently closed for contributions. Feel free to tune the models with your own hyperparameters.

## Major References:
- Park, Mijung, et al. "DP-EM: Differentially private expectation maximization." Artificial Intelligence and Statistics. PMLR, 2017.
- Kairouz, Peter, Sewoong Oh, and Pramod Viswanath. "The composition theorem for differential privacy." International conference on machine learning. PMLR, 2015.

