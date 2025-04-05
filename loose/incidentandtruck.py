import random
from collections import deque
import networkx as nx
from constants import *
from events import Event
import numpy as np


class IncidentSolvers:

    def __init__(self,K_trucks, origin ='2752332143'):
        self.origin = origin
        self.K_trucks = K_trucks
        self.trucks = []
        self.available = deque()
        self.unavailable = deque()
        for i in range(K_trucks):
            truck = TowTruck(origin=origin)
            truck.name = f"Truck {i}"

            self.trucks.append(truck)
            self.available.append(truck)

    def truck_returned(self, truck):
        if truck in self.unavailable:
            self.unavailable.remove(truck)

        self.available.append(truck)
        truck.progress = 0
        truck.isHome = True
        truck.going_home = False
        truck.path = None
        # print(f"Truck {truck.name} returned to base at time {truck.time}")
        # print("Trucks available after return:",len(self.available),'\n')


    def send_truck(self, destination_road, incident_duration, current_time,location):
        # print(f"trying to send a truck, \n \
        # amount trucks available: {len(self.available)} \n trucks available: {[truck.name for truck in self.available]}\n")
        if len(self.available) > 0:
            truck = self.available.pop()
            # Check if truck can reach in time
            destination = destination_road[0]
            path = nx.shortest_path(Graph, self.origin, destination, weight='length')
            length = nx.path_weight(Graph, path,weight='length')
            length_additional = location * nx.path_weight(Graph, destination_road,weight='length')
            time_to_travel = truck.calc_time_to_travel(length + length_additional)


            if time_to_travel> incident_duration:
                # print("Takes too long to reach incident location\n")
                self.available.append(truck)
                return
            else:
                # Send the truck to the incident.
                # print(f"sending truck {truck.name} to {Graph.nodes[destination]['name']} at time {current_time}\n")
                # print(f"location {location*100}% from {Graph.nodes[destination_road[0]]['name']} to {Graph.nodes[destination_road[1]]['name']} ")
                # print(f"Incident at {length_additional} from {Graph.nodes[destination]['name']}, total_length = {nx.path_weight(Graph, destination_road,weight='length')}")
                # print(f"Reaching {Graph.nodes[destination]['name']} at {current_time+ truck.calc_time_to_travel(length)} ")
                reaching_time = current_time + time_to_travel
                # print(f"Reaching incident at {reaching_time} incident should be solved atmost {current_time + incident_duration}\n")
                event_truck = truck.new_destination(destination_road,destination, current_time, distance_from_junction=length_additional)
                self.unavailable.append(truck)
                return event_truck

        else:
            # print('No trucks available sry')
            pass

    
class TowTruck:
    def __init__(self, origin, name=f"Truck {random.randint(0,100)}"):
        self.origin = origin
        self.isHome = True
        self.velocity = 80
        self.progress = 0
        self.time = 0
        self.going_home = False
        self.name = name
        self.next_event = None
    def __str__(self):
        at = self.path[self.progress]
        return f"Tow Truck travelling from {Graph.nodes[self.origin]['name']} to {Graph.edges[self.destination_road]} at {self.velocity} km/h, atm at {Graph.nodes[at]['name']}"

    def calc_time_to_travel(self,length):
        """
        :param length: edge length
        :return: returns time to traverse length based on normal speed
        """
        mean = length / (self.velocity /3.6) #seconds
        std = mean / 20
        time_to_travel = np.random.normal(loc = mean, scale = std) / 3600 #back to hours
        return time_to_travel

    def new_destination(self, destination_road, destination, current_time, distance_from_junction):
        if self.isHome:
            #Lets make destination = first item in destination road
            if self.origin == destination:
                self.destination = destination_road[1]
            else:
                 self.destination = destination
            self.destination_road = destination_road
            self.add_d = distance_from_junction
            self.path = nx.shortest_path(Graph, self.origin, self.destination, weight = 'length')
            self.isHome = False
            self.going_home = False
            self.time = current_time
            new_event = self.schedule_event_exit()
            
            return new_event
        else:
            print("Not able to set new destination, vehicle still on the road.")

    def schedule_event_exit(self):
        #Car is travelling and did not reach destination yet

        if  self.progress < len(self.path) - 1:
            # Can go on emergency lane so doesn't care for traffic jam
            current_node = self.path[self.progress]
            next_node = self.path[self.progress + 1]
            # print(f"{self.name} Now going from {Graph.nodes[current_node]['name']} to {Graph.nodes[next_node]['name']} at time {self.time}\n")

            length = Graph.edges[(current_node,next_node)]['length']
            time_to_travel = self.calc_time_to_travel(length)

            new_time = self.time + time_to_travel
            # print(f"{self.name} reaching {Graph.nodes[next_node]['name']} at time {new_time}\n")
            #Store event and increase progress
            self.next_event = Event(1 , new_time, car=self)
            self.increase_progress()
            self.increase_time(new_time)
            
            if self.going_home:
                # print('On its way home')
                pass

            return self.next_event

        # Car reached destination, and is not going home
        elif (not(self.going_home)) and (self.progress == len(self.path) - 1):
            if self.origin == self.destination:
                print("Ohoh this shouldnt happend anymore....")
                # self.progress =0
                # # reached destination, Drive additional length to incident:
                # self.time +=  self.calc_time_to_travel(self.add_d)
                # print(f"Increased time {self.name} time to {self.time}")
                # solving_event = Event(3, self.time, road = self.destination_road)
                # print(f" {self.name} Solved event time {self.time}")
                # # Calculate how long it takes to get to the other side of the road, i.e. next junction
                # tot_road_length = nx.path_weight(Graph, self.destination_road,weight='length')
                # # 'Drive' to other side
                # self.time += self.calc_time_to_travel(tot_road_length-self.add_d)
                # print(f" Arrived at opposite side of the road {self.time}")
                # # Calculate new path from other side of the road
                # self.path = [self.destination_road[1],self.destination_road[0]]
                # print(f" Path to get back:{Graph.nodes[self.destination_road[1]]['name']} -> {Graph.nodes[self.destination_road[0]]['name']} {self.time}")
                # length = Graph.edges[tuple(self.path)]['length']
                # time_to_travel = self.calc_time_to_travel(length)
                # new_time = self.time + time_to_travel
                # print(f" Arrived back at origin base {new_time}")
                # self.progress = len(self.path)-1
                # self.increase_time(new_time)
                # print(f" updated time to {self.time}")
                # self.isHome = True
                # self.going_home = False
                # print(f"Now sending event back to event handler")
                # return ['Truck back', solving_event]


            # reached destination, Drive additional length to incident:
            self.time +=  self.calc_time_to_travel(self.add_d)
            solving_event = Event(3, self.time, road = self.destination_road)
            # Calculate how long it takes to get to the other side of the road, i.e. next junction
            tot_road_length = nx.path_weight(Graph, self.destination_road,weight='length')
            # 'Drive' to other side
            self.time += self.calc_time_to_travel(tot_road_length-self.add_d)
            # Calculate new path from other side of the road

            self.path = nx.shortest_path(Graph, self.destination_road[1], self.origin, weight = 'length')

            # Reset progress
            # print(f"New path {[Graph.nodes[nodes]['name'] for nodes in self.path]}")
            self.progress = 0

            # edge = Graph.edges[(self.destination, self.path[1])]
            # print('Heading home')
            if len(self.path) > 1:
                # print("##### Flag 0 #####")
                length = Graph.edges[(self.destination_road[1], self.path[1])]['length']

                time_to_travel = self.calc_time_to_travel(length)
                new_time = self.time + time_to_travel

                self.increase_progress()
                self.increase_time(new_time)
                self.next_event = Event(1, new_time, car=self)
                self.going_home = True
                
                return [self.next_event, solving_event]
            else:
                #Never triggered, Alr at home
                # print("##### Flag 1 #####")
                self.isHome = True
                self.going_home = False
                return ['Truck back', solving_event]
        # Car is going home, and reached destination, thus reached home
        elif (self.going_home) and (self.progress == len(self.path) - 1):
            self.isHome = True
            self.going_home = False
            return 'Truck back'

    def increase_progress(self):
        self.progress += 1

    def increase_time(self, new_time):
        self.time = new_time
