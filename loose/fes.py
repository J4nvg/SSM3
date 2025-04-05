import heapq
class FES:
    def __init__(self):
        self.events = []

    def add(self, event):
        heapq.heappush(self.events, event)
    
    def next(self):
        return heapq.heappop(self.events)
    
    def isEmpty(self):
        return len(self.events) == 0
    
    def __repr__(self):
        string = ''
        sorted_events = sorted(self.events)
        for event in sorted_events:
            string += f'{event}\n'
        return string