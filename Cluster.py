#!/usr/bin/python3
import time, sys
from helpers import import_data_from_file
import numpy as np
import concurrent.futures
from sgd import compute_local_theta

class Cluster:
    MAX_ID = 0

    def __init__(self, machine_speed):
        ## Create a new Cluster instance.
        # :param machine_speed [float] the speed of the machine, proportional to ops / sec
        # :param data_set [array<array<int>>] rows of a dataset where the first element contains the class of the row
        # :return [Cluster] a new Cluster instance
        self.machine_speed = machine_speed
        self.X = 0
        self.y = 0 
        self.latency_table = {}
        self.cluster_table = {}
        self.id = Cluster.MAX_ID + 1
        Cluster.MAX_ID += 1
    
    def get_id(self):
        ## Get the ID for this cluster.
        # return [int] the ID
        return self.id

    def set_data_set(self, X, y):
        ## Set the data set on which this cluster will train.
        # :param data_set [array<array<int>>] rowws of a dataset where the first element of each,
        #  row indicates the class of the row.
        self.X = np.c_[np.ones((len(X),1)),X]
        self.y = y

    def set_latency_to(self, cluster, latency):
        ## Set the latency this cluster has when sendin messages to another cluster.
        # This latency is artificial and trggers a sleep for the amount of time specified.
        # If there is *real* latency between clusters, the artificial latency should be 
        # set to zero.
        # :param cluster [Cluster] the cluster to which the latency is set
        # :param latency [float] the latency betwween clusters in seconds
        self.latency_table[cluster.get_id()] = latency
        self.cluster_table[cluster.get_id()] = cluster

    def go(self):
        # If I want to send a message to another cluster: 
        # time.sleep(self.latency_table[j])
        # self.cluster_table[j].some_func()
        '''
        X    = Matrix of X with added bias units
        y    = Vector of Y
        theta=Vector of thetas np.random.randn(j,1)
        learning_rate 
        iterations = no of iterations
        
        Returns the final theta vector and array of cost history over no of iterations
        '''
        iterations = 50
        theta = np.random.randn(2,1)

        m = len(self.y)
        cost_history = np.zeros(iterations)

        for it in range(iterations):
            cost = 0.0
            for i in range(m):
                ## Compute update
                theta, cost = compute_local_theta(m, self.X, self.y, theta, cost)
                ## Global aggregation
        cost_history[it]  = cost
        print('Theta0:          {:0.3f},\nTheta1:          {:0.3f}\nFinal cost/MSE:  {:0.3f}\n\n'.format(theta[0][0],theta[1][0],cost_history[-1]))
        return theta, cost_history

def launch_cluster(cluster):
    return cluster.go()
        
def main():
    ## TODO: Use real data  
    # all_data = import_data_from_file(sys.argv[1])

    # Generate Data 
    X = 2 * np.random.rand(1000,1)
    y = 4 +3 * X + np.random.randn(1000,1)

    max_machine_speed = 3
    max_server_latency = 5
    ## TODO: Figure out a way to have clusters dies and come back.
    clusters = [Cluster(k % max_machine_speed) for k in range(100)]
    ## TODO: Refactor and design a better assignment schema.
    size_of_data_partition = len(X) // len(clusters)
    for k in range(len(clusters)):
        low = k * size_of_data_partition
        hi = (k + 1) * size_of_data_partition
        clusters[k].set_data_set(X[low:hi], y[low:hi])
    for k in range(len(clusters)):
        for j in range(len(clusters)):
            if k != j:
                clusters[k].set_latency_to(clusters[j], (k + j) % max_server_latency)
    with concurrent.futures.ProcessPoolExecutor() as executor:
        result = executor.map(launch_cluster, clusters)

if __name__ == "__main__":
    main()