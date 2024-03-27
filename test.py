g = {
    1: [2,3,4],
    2: [1,5,6],
    3: [1,4,7],
    4: [1,3,8],
    5: [2],
    6: [2,9],
    7: [3,9],
    8: [4,9,10],
    9: [6,7,8],
    10: [8],            
    }

def bfs(g:dict, start:int, stop:int):
    # to avoid changing the actual source object I createa a copy here
    counter = 0
    if start == stop:
        print(f"start and stop are the same value: {start}.. No search needed..")
        return
    #
    # adding one to visited nodes and init the function
    visited = [start]
    next_to_visit = list(g.get(start,[]))
    #
    # looping
    while not next_to_visit==[]:
        counter = counter + 1
        print(f"Iteration: {counter} - nodes to visit: {next_to_visit} - visited nodes: {visited}")
        node = next_to_visit.pop(0)
        print(f"Checking node: {node}")
        if node not in visited:
            visited.append(node)
        #    
        if node == stop:
            print(f"Found node {stop } at iteration : {counter}")
            return
        #
        # adding he children of node, at the end of the list, unless they have been visited already
        next_to_visit.extend([x for x in g.get(node,[]) if x not in visited and x not in next_to_visit])
    #
    print(f"Search stopped at iteration: {counter}")









def bfs_recursive(g:dict, start:int, stop:int, visited:list = [], nodes_to_visit:list = [], counter:int = 0):
    if start == stop:
        print(f"Stop value: {stop} found at recursive level: {counter}")
        return
    #
    if start in visited:
        return
    #
    visited.append(start)
    next_nodes = [ x for x in g.get(start,[]) if x not in visited and x not in nodes_to_visit]
    nodes_to_visit.extend(next_nodes) 
    print(f"Visiting node {start} - level {counter} - visited: {str(visited):20} - nodes_to_visit: {nodes_to_visit}")       
    if nodes_to_visit == []:
        print("completed search.. level: {counter}")
    new_node = nodes_to_visit.pop(0)
    bfs_recursive(g, new_node, stop, visited, nodes_to_visit, counter+1)

    

def dfs(g:dict,start:int,stop:int):
    visited = []
    next_nodes = []
    counter = 0
    if start == stop:
        print(f"Start and Stop values are the same: {start} Stopping..")
        return
    #
    next_nodes = list(g.get(start,[]))
    if start not in visited:
        visited.append(start)
    counter = counter + 1    
    while next_nodes != []:
        print(f"Starting cycle: {counter}.. nodes visited: {str(visited):>20} - nodes to visit {next_nodes}")
        next_node = next_nodes.pop(0)
        if next_node == stop:
            print(f"Found final node: {stop} at iteration: {counter}")
            break
        #
        visited.append(next_node)
        node_children = g.get(next_node,[])
        next_nodes = [x for x in node_children if x not in visited ] + [x for x in next_nodes if x not in visited and x not in node_children]
        counter += 1
    #    
    print("Completed the graph search..")    


def dfs_recursive(g:dict,start:int,stop:int,visited:list=[], depth:int=1)-> bool:
    #
    found = False
    if start == stop:
        print(f"Stop value {stop} found at level: {depth}..")
        return True    
    #
    print(f"Level: {depth} - checking node: {start}")
    next_nodes = list(g.get(start,[]))
    if start not in visited:
        visited.append(start)
    #   
    for node in next_nodes:
        if node in visited:
            continue
        found = dfs_recursive(g,node,stop,visited,depth+1)
        if found: break
    #
    return found  
 