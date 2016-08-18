class InfluxDBClient():
    def __init__(self,host, port, user, passwd, database):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._database = database
    
    def create_database(self,database):
        pass
        
    def drop_database(self,database):
        pass
        
    def write_points(self,data):
        pass
