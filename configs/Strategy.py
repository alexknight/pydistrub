

class TaskStrategy(object):
    priority = 0
    weight = 0
    allocate_to = []


class Addr(object):
    MasterServerAddress = "localhost:10021"
    WorkerAddress = ["192.168.1.1:10022", "192.168.1.1:10023"]

