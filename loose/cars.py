from constants import *
import numpy as np
import networkx as nx

class Car:
    VELOCITIES = [100, 80]
    VELOCITIES_P = [0.9, 0.1]
    def __init__(self, time_entrance, origin = None, destination = None):
        #Origin and destination
        origin, destination = np.random.choice(JUNCTIONS, 2, replace = False)
        
        self.origin = origin
        self.destination = destination

        #path to follow
        self.path = nx.shortest_path(Graph, self.origin, self.destination, weight = 'length')

        #Velocity
        self.velocity = np.random.choice(self.VELOCITIES, p=self.VELOCITIES_P)

        #Variable to keep track how far into the path we are (to simplify scheduling events)
        #Int between 0 and len(path) - 1 that indicates in which edge we are, starting at 0
        #Essentially, how many edges has it travelled so far
        self.progress = 0
        
        #Give it nav with 10% chance
        self.has_nav = np.random.choice([True, False], p=[0.1,0.9])
        self.changed_route = []

        #Time entrance
        self.time = time_entrance

        #Schedule next event and store it as attribute
        self.next_event = self.schedule_event_exit()


    def __str__(self):
        return f'Vehicle travelling from {self.origin} to {self.destination} at {self.velocity} km/h, atm at {self.path[self.progress]}'
    

    def custom_weight(self,u,v,data):
        """
        :param u: std for accepting function as weight, node 1
        :param v:  std for accepting function as weight, node 2
        :param data: std for accepting function as weight, edge
        :return: time_to_travel + delay
        """
        length = data['length']
        time_to_travel = (length / (self.velocity /3.6)) / 3600 #Mean of normal dist
        if Graph.edges[(u,v)]['accident']:   
            delay = MEAN_ACCIDENT_DURATION
        else:
            delay = 0
        return time_to_travel + delay
    
    def calc_time_to_travel(self,length):
        """
        :param length: edge length
        :return: returns time to traverse length based on normal speed
        """
        mean = length / (self.velocity /3.6) #seconds
        std = mean / 20
        time_to_travel = np.random.normal(loc = mean, scale = std) / 3600 #back to hours
        return time_to_travel

    def schedule_event_exit(self):
        #Remove car from list of cars in previous edge
        if self.progress > 0:
            #Edges can be expressed in two directions, account for it
            edge = (self.path[self.progress - 1], self.path[self.progress])
            DIC_EDGES[edge].remove(self)


        if self.progress < len(self.path) - 1:
            # Get the current and next node on the original path
            current_node = self.path[self.progress]
            next_node = self.path[self.progress + 1]
            edge = Graph.edges[(current_node, next_node)]

            # Check for accident on the current edge and if nav is enabled
            # No need to check for accident, just check if navigation (there may be accidents later that makes us recompute)
            if self.has_nav:
                # print("Updating path")
                new_path = nx.shortest_path(Graph, current_node, self.destination, weight=self.custom_weight)

                if new_path != self.path[self.progress:]:
                    print("Found a quicker route")
                    # print(f"Prev path = {[Graph.nodes[node]['name'] for node in self.path]}")
                    # print(f"New path = {[Graph.nodes[node]['name'] for node in new_path]}")

                    #I commented this out bc append is not efficient
                    # self.changed_route.append((self.path, new_path))

                    # Preserve the already traversed portion
                    prefix = self.path[:self.progress]

                    updated_path = prefix + new_path
                    self.path = updated_path
                    # print(f"Updated path: {[Graph.nodes[node]['name'] for node in self.path]}")

                    # Update next_node based on the new path
                    next_node = self.path[self.progress + 1]
                    edge = Graph.edges[(current_node, next_node)]
                    length = edge['length']
                    # Sample travel time along the new edge (including accident delay)
                    
                    #I think no need to add accident duration bc i account for this in my code alr and a accident can happen before scheduling this
                    # time_to_travel = self.calc_time_to_travel(length) + edge['accident_duration']
                    time_to_travel = self.calc_time_to_travel(length)
                else:
                    # No change in path (fallback scenario)
                    length = edge['length']
                    time_to_travel = self.calc_time_to_travel(length)
            else:
                # Normal travel (no accident on the edge)
                length = edge['length']
                time_to_travel = self.calc_time_to_travel(length)

            new_time = self.time + time_to_travel
            # Schedule next event and update car's progress and time
            self.next_event = Event(1, new_time, car=self)
            self.increase_progress()
            self.increase_time(new_time)

            #Add car to list of cars in the new edge
            edge = (self.path[self.progress - 1], self.path[self.progress])
            DIC_EDGES[edge].append(self)

            return self.next_event
    
    def increase_progress(self):
        self.progress += 1

    def increase_time(self, new_time):
        self.time = new_time

    def __lt__(self, other):
        return self.time < other.time
    
    def enter_queue(self, time):
        #store time at which the car entered the queue
        self.time_enter = time

    def exit_queue(self, time_exit):
        #Update time of car when it left the queue
        self.time += time_exit - self.time_enter

        #Update time of event leaving road
        self.next_event.new_time(self.time)


