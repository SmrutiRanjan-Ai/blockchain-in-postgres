class Event:
    def __init__(self, timestamp, args):
        self.timestamp = timestamp
        self.args = args

    def __str__(self):
        print(self.timestamp, *self.args)
        return str()

    def __le__(self, other):
        if self.timestamp <= other.timestamp:
            return True
        else:
            return False

    def __lt__(self, other):
        if self.timestamp < other.timestamp:
            return True
        else:
            return False

    def __ge__(self, other):
        if self.timestamp >= other.timestamp:
            return True
        else:
            return False

    def __gt__(self, other):
        if self.timestamp > other.timestamp:
            return True
        else:
            return False