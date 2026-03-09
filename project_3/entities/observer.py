class Observer:
    def update(self, value):
        pass

class ScoreSubject:
    def __init__(self):
        self.observers = []
        self.score = 0

    def attach(self, observer):
        self.observers.append(observer)

    def add_score(self, value):
        self.score += value
        for obs in self.observers:
            obs.update(self.score)
