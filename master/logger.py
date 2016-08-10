from influxdb import InfluxDBClient

class influxwrapper:
    """
    @class influxwrapper

    This class provides methods for logging all events to influxDB.
    """
    
    def __init__(self, influxcli=None):
    
        """
        @brief Instantiate the wrapper class
        """
        if (influxcli != None):
            self.influxcli = influxcli
        else:
            self.influxcli = InfluxDBClient('localhost', 8086, 'root', 'root', 'NSF')
        self.influxcli.create_database('NSF')
            
    def clear(self):
        """
        @beief clear the log by re-create the database

        """
        self.influxcli.drop_database('NSF')
        self.influxcli.create_database('NSF')
    
    def log_host(self,host,ip,event):
        """
        @beief This method logs host related events

        @param host hostname of the node
        @param ip ip address of the node
        @param event Type of event
        """
    
        json_body = [
        {
            "measurement": "Hosts",
            "tags": {
                "Hostname": host,
                "IP": ip
            },
            "fields": {
                "Event": event
            }
        }
        ]
        self.influxcli.write_points(json_body)
        
    def log_vnf(self,vnf_id,vnf_type,host,event):
        """
        @beief This method logs VNF related events

        @param vnf_id id of container
        @param vnf_type type of the container
        @param host hostname of the node which container lives
        @param event Type of event
        """
        json_body = [
        {
            "measurement": "VNF",
            "tags": {
                "Con_id": vnf_id,
                "VNF_type": vnf_type,
                "Host": host
            },
            "fields": {
                "Event": event
            }
        }
        ]
        self.influxcli.write_points(json_body)
        











    
