import numpy as np
import matplotlib.pyplot as plt

def gradient(textdata):

    #make the dataset to suit with the formulas
    #take the first 3 number
    dataset_1 = np.delete(textdata, [0,1,2]) 

    #take the first and the last 2 number
    dataset_2 = np.delete(textdata, [0, len(textdata)-1, len(textdata)-2]) 

    #take the last 3 number
    dataset_3 = np.delete(textdata, [len(textdata)-1, len(textdata)-2, len(textdata)-3])

    
    
    #setting up variables
    a2 = 0
    a3 = 0

    #max number of interations
    max_no_of_iter = 50
    aa = 0.05

    #Take out the first 3 number and align the dataset
    x = len(textdata) - 3
    
    
    #data list
    costlist = [] 
    iterationslist = []
    
    
    
    for i in range(max_no_of_iter):

        #Gradient Descent Methods
        predict = a2 * dataset_2 + a3 * dataset_3

        #dy/dk1
        dyda2 =-(2/x)*sum(dataset_2 *(dataset_1 -predict))

        #dy/dk2
        dyda3 =-(2/x)*sum(dataset_3 *(dataset_1 -predict))

        a2 -= aa * dyda2
        a3 -= aa * dyda3
        cost = sum([error ** 2 for error in (dataset_1 - predict)])
        
        #Save the results in the list for plotting graph
        costlist.append(cost)
        iterationslist.append(i)
    
    
    #Plot out the graph
    fig, ax = plt.subplots()
    ax.plot(iterationslist, costlist, color = 'magenta', linewidth = 5, label = 'cost J')
    ax.set_title('linear prediction error')
    ax.set_xlabel('iter')
    ax.set_ylabel('cost J')
    ax.grid(axis = 'x')
    ax.ticklabel_format(axis="y", style="scientific", scilimits=(2,2), useMathText = True)
    ax.legend()
    fig
    
    #check the best of  a2,a3, cost
    print("a2 is {}\na3 is {}".format(a2,a3))
    print("cost is {}".format(cost))


#take the data from the txt(1-5) file
data = np.array([])

with open('eie2108-lab-2021-datafile-05.txt', 'r') as txt:
    for line in txt.readlines():
        data = np.append(data, float(line.strip()))

#run the Gradient Descent Method
gradient(data)