class DashboardRequest:
    def __init__(self, **kwargs):
        self.group = kwargs['group']
        self.genders = kwargs['genders'].split(",")
        self.years = kwargs['years'].split(",")
        self.values = kwargs['values'].split(",")
        self.indexes = kwargs['indexes'].split(",")