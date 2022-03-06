import datetime
import json
from time import sleep
import requests
import xmltodict
url_cam_plate = 'http://186.69.152.58:81/ISAPI/Traffic/channels/1/vehicleDetect/plates'
class Vehicle():
    def __init__(self):
        self.url_cam_plate = 'http://localhost:3000/Plates'
        self.response = requests.get(
            url=self.url_cam_plate,
            stream=True,
        )

    def getAllplate(self, n):
        h= json.loads(self.response.text)
        plate=h[-1]['plateNumber']
        """plate = self.response_parser(self.response)['Plates']['Plate'][-n]['plateNumber']
        captureTime = self.response_parser(self.response)['Plates']['Plate'][-n]['captureTime']
        back = self.response_parser(self.response)['Plates']['Plate'][-n]['direction']
        """
        captureTime=h[-1]['captureTime']
        back = h[0]['direction']
        sleep(5)
        time=self.convertime(captureTime)
        return plate, time,back
    def convertime(self,t):
        dt_string = t.split("-")[0]
        formato = "%Y%m%dT%H%M%S"
        dt_object = datetime.datetime.strptime(dt_string, formato)
        return dt_object
    def response_parser(self, response, present='dict'):
        if isinstance(response, (list,)):
            result = "".join(response)
        else:
            result = response.text

        if present == 'dict':
            if isinstance(response, (list,)):
                events = []
                for event in response:
                    e = json.loads(json.dumps(xmltodict.parse(event)))
                    events.append(e)
                return events
            return json.loads(json.dumps(xmltodict.parse(result)))
        else:
            return result