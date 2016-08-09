from influxdb import InfluxDBClient

class influxwrapper:
    def __init__(self, influxcli=None):
        if (influxcli != None):
            self.influxcli = influxcli
        else:
            self.influxcli = InfluxDBClient('localhost', 8086, 'root', 'root', 'NSF')
            self.influxcli.create_database('NSF')
            
    def clear():
        influxcli.drop_database('NSF')
        client.create_database('NSF')
    
    def log_host(self,host,ip,event):
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
