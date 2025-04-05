from cars import Car
class Event:
    TYPE = ['New car', 'Car departure', 'Accident', 'Accident end', 'left queue']
    def __init__(self, typ:int, time, car = None, road = None, duration = None):
        #types:
            #0 : Arrival of car to the network
            #1 : Car leaves current road and goes on to the next
            #2 : Accident in road
            #3 : End of accident
            #4 : Departure of car from queue of accident
        self.type = typ
        self.time = time
        self.road = road
        #Only for type 2 events bc needed for tow trucks
        self.duration = duration

        if typ == 0:
            car = Car(time_entrance = time)
    
        self.car = car
        
    def __str__(self):
        if self.type == 0:
            return f'{self.TYPE[self.type]} from {self.car.origin} to {self.car.destination} at {self.time}'
        if self.type == 1:
            return f'{self.TYPE[self.type]} of {self.car} at {self.time}h'
        if self.type == 2:
            return f'{self.TYPE[self.type]} at {self.road} at {self.time}h'
        if self.type == 3:
            return f'{self.TYPE[self.type]} at {self.road} at {self.time}h'
        if self.type == 4:
            return f'{self.car} {self.TYPE[self.type]} at {self.road} at {self.time}h'

    def __lt__(self, other):
        return self.time < other.time
    
    def new_time(self, new_time):
        self.time = new_time