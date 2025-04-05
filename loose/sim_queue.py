import heapq
class Queue:
    def __init__(self, road):
        self.road = road
        self.cars = []

    def add(self, car, time):
        heapq.heappush(self.cars, car)
        car.enter_queue(time)

    def add_list(self, list, time):
        for car in list:
            heapq.heappush(self.cars, car)
            car.enter_queue(time)   

    def next(self):
        return heapq.heappop(self.cars)
    
    def first(self):
        return heapq.nsmallest(1, self.cars)
    
    def isEmpty(self):
        return len(self.cars) == 0
    
    def __repr__(self):
        string = ''
        sorted_cars = sorted(self.cars)
        for car in sorted_cars:
            string += f'{car}\n'
        return string