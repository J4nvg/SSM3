import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import networkx as nx
import random
import collections
from collections import deque
from incidentandtruck import IncidentSolvers,TowTruck
from cars import Car
from events import Event
from sim_queue import Queue
from fes import FES
from constants import *

# INCIDENT_DURATION_PARAMS = ()

#Sampling arrival times of cars to network
def lambdat(lambda_t, t : np.array):
    lambdat = []
    for time in t:
        lambdat.append(lambda_t[int(np.floor(time))])
    return lambdat

def arrival_times(lam): #Taken from lecture notes
    max_T = 24
    arrival_times = collections.deque()
    exp_dist = stats.expon(scale = 1/lam)
    t = exp_dist.rvs()
    while t < max_T:
        arrival_times.append(t)
        t += exp_dist.rvs()
    
    return np.asarray(arrival_times)

#Using a thining approach to get arrival times
max_lambda = np.max(ARRIVAL_RATE) + 1
all_arrivals = arrival_times(max_lambda)

uniform_dist = stats.uniform(0,1)
u_rvs = uniform_dist.rvs(len(all_arrivals))
accept_filter = u_rvs * max_lambda < lambdat(ARRIVAL_RATE, all_arrivals)

accepted_arrivals = all_arrivals[accept_filter]

#Using a thining approach to get accident times
max_lambda = np.max(INCIDENT_RATE) + 1
all_accidents = arrival_times(max_lambda)

uniform_dist = stats.uniform(0,1)
u_rvs = uniform_dist.rvs(len(all_accidents))
accept_filter = u_rvs * max_lambda < lambdat(INCIDENT_RATE, all_accidents)

accepted_accidents = all_accidents[accept_filter]

incident_solvers = IncidentSolvers(2)

#Simulation (can be turned into an object later)
LIST_CARS = []
fes = FES()
# for arrival in accepted_arrivals:
#     #Two events associated with each arrival
#     arrival_event = Event(0, arrival)
#     fes.add(arrival_event)

for accident in accepted_accidents:
    affected_road = list(Graph.edges)[np.random.choice(len(Graph.edges))]
    if DIC_ACCIDENTS[affected_road] < accident:
        duration = incident_duration_dist.rvs()/60
        time_end = accident + duration
        accident_event = Event(2, accident, road=affected_road, duration=duration)
        end_accident = Event(3, time_end, road=affected_road)

        fes.add(accident_event)
        fes.add(end_accident)
        DIC_ACCIDENTS[affected_road] = time_end

#Queue for accidents setup
Queues = {}
for edge in DIC_EDGES.keys():
    Queues[edge] = Queue(edge)

# road = list(DIC_EDGES.keys())[0]
# accident = Event(2, 0.5, road=road)
# end_accident = Event(3, 0.6, road =road)
# fes.add(accident)
# fes.add(end_accident)
# road = road[::-1]
# accident = Event(2, 0.5, road=road)
# end_accident = Event(3, 0.6, road =road)
# fes.add(accident)
# fes.add(end_accident)

t = 0 #current time
while t < 24.0:
    event = fes.next()
    t = event.time

    #Car joins network
    if event.type == 0:
        car_travel_event = event.car.next_event
        fes.add(car_travel_event)
        LIST_CARS.append(event.car)

    #Car leaves road
    if event.type == 1:
        next_travel_event_car = event.car.schedule_event_exit()
        if type(next_travel_event_car) == Event: #If the car has arrived to its destination it wont return an event object
            fes.add(next_travel_event_car)

        #when a tow truck arrives to the accident it wants to solve, it will return two events
        if type(next_travel_event_car) == list:
            #Event for fixing the accident
            fes.add(next_travel_event_car[1])
            # print(f'Tow truck solved accident {t} truck time:{event.car.time}')

            # print(next_travel_event_car)
            #Event for heading back
            if type(next_travel_event_car[0]) == Event:
                fes.add(next_travel_event_car[0])
            #it may alr be at home
            elif next_travel_event_car[0] == 'Truck back':
                incident_solvers.truck_returned(event.car)
                # print(f'Tow truck back {t} truck time:{event.car.time}')

        if next_travel_event_car == 'Truck back':
            incident_solvers.truck_returned(event.car)
#             print(f'Tow truck back {t} truck time:{event.car.time}')
         # else:
            # print(event.car)

    #Start accident
    if event.type == 2:
        road = event.road
        #choose random cars affected:
            #List comprehension is inefficient af here
            # cars_not_in_queue = [car for car in DIC_EDGES[road] if car not in Queues[road].cars]
        cars_not_in_queue = list(set(DIC_EDGES[road]) - set(Queues[road].cars))
        if len(cars_not_in_queue) != 0:


            amount_cars_affected = np.random.randint(len(cars_not_in_queue))
            cars_affected = np.random.choice(cars_not_in_queue, amount_cars_affected, replace=False)


            #####Consider sorting list of cars before chooisng which ones are affected


            Queues[road].add_list(cars_affected, event.time)
        Graph.edges[road]['accident'] = True
        #Send tow truck
        # print("This road:",road)

        # Location on the road
        # Trying to keep it simple for debug purpose
        # Loc * Length / velocity will be the additional time it takes
        loc = stats.uniform(0, 1).rvs()

        first_event_truck = incident_solvers.send_truck(road, event.duration, event.time,location=loc)
        #If no trucks are available first_event_truck will be empty
        if type(first_event_truck) == Event:
            fes.add(first_event_truck)
            # print(f'Tow truck on its way {t}')
            pass
        elif type(first_event_truck) == list:
            fes.add(first_event_truck[1])
#             print(f'Tow truck on its way {t}')
            pass
        else:
#             print(f'Tow trucks all busy  {t}')
            pass

    #End accident
    if event.type == 3:
        road = event.road
        #A tow truck may have ended he accident before so there could be two events for ending it, hence only do it if there is still an accident
        if Graph.edges[road]['accident']:
            #1 minute until first car leaves the queue 
            if not(Queues[road].isEmpty()) and not(Graph.edges[road]['queue']):
                # print(f'First event departure {Queues[road].isEmpty()}', road)
                first_departure_event = Event(4, event.time + 1/60, road=road)
                # print(first_departure_event)
                fes.add(first_departure_event)
                Graph.edges[road]['queue'] = True
            Graph.edges[road]['accident'] = False   
        # print(t)
        else:
            print(f'Accident already solved {t}')
    
    #Departure from road
    if event.type == 4:
        # print(event)
        road = event.road
        time = event.time
        #Remove car from queue
        # print(len(Queues[road].cars), event.road)
        car = Queues[road].next()

        #Modify time to arrival of next node in path
        car.exit_queue(time)

        if not(Queues[road].isEmpty()):
            #Next departure event
            next_event_time = time + Graph.edges[road]['DepDist'].rvs()
            
            next_event = Event(4, next_event_time, road=road)
            # print(next_event)
            fes.add(next_event)
        else:
            Graph.edges[road]['queue'] = False