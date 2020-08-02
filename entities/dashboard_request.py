class DashboardRequest:
    def __init__(self, **kwargs):
        self.group = kwargs['group']
        self.genders = kwargs['genders'].split(",")
        self.years = kwargs['years'].split(",")
        self.values = kwargs['values'].split(",")
        self.indexes = kwargs['indexes'].split(",")
        self.__column = kwargs['columns'].split(",")
        self.__assign_columns()

    def __assign_columns(self):
        if self.__column[0] == "":
            self.columns = None
        else:
            self.columns = self.__column
