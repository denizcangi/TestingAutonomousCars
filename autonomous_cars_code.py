import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from random import*

#implementation of unweighted strongly connected directed graph
def generator(numStates, density, maxNumAction,numOfGoals):

    numPossibleEdges=numStates*(numStates-1)
    #the number of edges in the graph, that depends on density
    numOfEdges=int(numPossibleEdges*density)

    G=nx.cycle_graph(numStates, create_using=nx.DiGraph)

    pos = nx.spring_layout(G, scale = 100)
    nx.draw_networkx_nodes(G, pos)
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    plt.axis('off')
    plt.show()
    #initially number of edges is equal to the number of states
    #since we have created the cycle
    numEdges=numStates

    #filling the alphabet of FSM, the number of symbols in the alphabet
    #depends on the maximum number of actionas to take from each state
    alphabet=[i for i in range(0,maxNumAction)]

    #adding an edge between randomly picked two states
    while numEdges!=numOfEdges:
        firstNode=randint(0,numStates-1)
        while(True):
            secondNode=randint(0,numStates-1)
            if secondNode!=firstNode:
                break
        if G.has_edge(firstNode, secondNode)==False and G.out_degree(firstNode)< maxNumAction:
            G.add_edge(firstNode,secondNode)
            numEdges=numEdges+1

    #assigning random weight to each edge
    #in order to satisfy the deterministic propert of FSM
    for i in G.nodes():
        outedges=[]
        for j in G.neighbors(i):
            found=False
            while found==False:
                random=randint(0,len(alphabet)-1)
                if alphabet[random] not in outedges:
                    G[i][j]["weight"]= alphabet[random]
                    outedges.append(alphabet[random])
                    found=True


    pos = nx.spring_layout(G, scale = 100.)
    nx.draw_networkx_nodes(G, pos, nodelist=G.nodes(), node_color='b')
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.axis('off')
    plt.show()
    starts=[0]

    errors=[]
    for i in range(numOfGoals): #numOfGoals is the number of erroneous states
        #created a list of nodes which are not neighbors of start state
        notNeighbors=list(nx.non_neighbors(G,starts[i]))
        randomError = randint(0, len(notNeighbors)-1)
        errorState = notNeighbors[randomError]
        while errorState in errors:
          randomError = randint(0, len(notNeighbors)-1)
          errorState = notNeighbors[randomError]
        if errorState not in errors:
          errors.append(errorState)
        print()
        print("Error state is", errorState)
        print()
        starts.append(errorState)

    listOfNodes = list(G.nodes())
    updatedList = []
    for i in listOfNodes:
      if i not in errors:
        updatedList.append(i)

    pos = nx.spring_layout(G, scale = 100.)
    #nx.draw_networkx_nodes(G, pos, nodelist= [errorState], node_color= 'r')
    nx.draw_networkx_nodes(G, pos, nodelist= errors, node_color= 'r')
    nx.draw_networkx_nodes(G, pos, nodelist=updatedList, node_color='b')
    nx.draw_networkx_edges(G, pos)
    nx.draw_networkx_labels(G, pos)
    labels = nx.get_edge_attributes(G,'weight')
    nx.draw_networkx_edge_labels(G,pos,edge_labels=labels)
    plt.axis('off')
    plt.show()
    #longestPath = nx.dag_longest_path(G, weight='weight', default_weight=1, topo_order=None)
    #print(longestPath)
    #longestPathLen = nx.dag_longest_path_length(G, weight='weight', default_weight=1)
    return G, errors

number_states=10
density=0.3
number_actions=3
numofGoals=1
errors=[]
G,errors=generator(number_states,density,number_actions,numofGoals)

def findingThePath(G,number_states,goal,initial_state):

    #edges is defined as the all edges in the graph.
    edges=G.edges()
    #matrix size is equal to the number of states that we've initialized
    MATRIX_SIZE=number_states
    #created a matrix M which is all 1's with a size MATRIX_SIZE x MATRIX_SIZE
    M = np.matrix(np.ones(shape =(MATRIX_SIZE, MATRIX_SIZE))) 
    #multiply all the cells in the matrix with -1
    M *= -1
    #trace all the edges in the graph
    for point in edges:
        #if the second state is an error state then change the cell in matrix
        #to 100
        if point[1] == goal:
            M[point] = 100
        #if there is an edge between two states but the second state is not the 
        #error state then change the cell in matrix to 0.
        else:
            M[point] = 0

    print(M)

    #created the Q table which stores the reward of each action for
    #the corresponding states, it has size of MATRIX_SIZE x MATRIX_SIZE
    Q = np.matrix(np.zeros([MATRIX_SIZE, MATRIX_SIZE]))

    # Determines the available actions for a given state
    def available_actions(state):
        #get the row of the state from the matrix M
        current_state_row = M[state]
        #create a list available_action, it gets the cells which are greater
        #than or equal to zero and get the successive state from it
        #and create a list of available states for the given state
        available_action = np.where(current_state_row >= 0)[1]
        return available_action
        
    # Chooses one of the available actions at random
    def sample_next_action(available_actions_range):
        next_action = int(np.random.choice(available_action, 1))
        return next_action

    #get the available actions from the initial state
    available_action = available_actions(initial_state)
    #find a random state from the available_action list.
    action = sample_next_action(available_action)

    #discount factor
    gamma = 0.75
    
    # Updates the Q-Matrix according to the path chosen
    def update(current_state, action, gamma):

        max_index = np.where(Q[action] == np.max(Q[action]))[1]
        if max_index.shape[0] > 1:
                max_index = int(np.random.choice(max_index, size = 1))
        else:
                max_index = int(max_index)
        max_value = Q[action, max_index]
        Q[current_state, action] = M[current_state, action] + gamma * max_value
        #if chosen states have edges inbetween them, then it updates it with 
        #reward, if it's not it updates the Q table with 0.
        if (np.max(Q) > 0):
                return(np.sum(Q / np.max(Q)*100))
        else:
                return (0)
    

    update(initial_state, action, gamma)

    #scores list 
    scores = []
    for i in range(number_states*100):
        current_state = np.random.randint(0, int(Q.shape[0]))
        available_action = available_actions(current_state)
        action = sample_next_action(available_action)
        score = update(current_state, action, gamma)
        scores.append(score)

    print("Trained Q matrix:")
    print(Q / np.max(Q)*100)

    # Testing part of the Q-learning
    current_state = initial_state
    #keep track of steps
    steps = [current_state]

    while current_state != goal:

        next_step_index = np.where(Q[current_state] == np.max(Q[current_state]))[1]
        if next_step_index.shape[0] > 1:
                next_step_index = int(np.random.choice(next_step_index, size = 1))
        else:
                next_step_index = int(next_step_index)
        steps.append(next_step_index)
        current_state = next_step_index

    print("Most efficient path:")
    print(steps)

    print("Language:")
    Language=[]

    for i in range(len(steps)-1):
        Language.append(G[steps[i]][steps[i+1]]['weight'])
    print(Language)

    plt.plot(scores)
    plt.xlabel('No of iterations')
    plt.ylabel('Reward gained')
    plt.show()
    return steps,Language

joinedList=[0]
joined_language=[]
initials=[0]
for i in range(numofGoals):

    first_steps, first_language=findingThePath(G,number_states,errors[i],initials[i])
    initials.append(errors[i])
#second_steps, second_language=findingThePath(G,number_states,secondGoal,goal)
    joinedList=joinedList+first_steps[1:]
    joined_language=joined_language+first_language

print()
print(joinedList)
print()
print(joined_language)
