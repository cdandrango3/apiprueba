import datetime
import json
import time
from random import random
from time import sleep

import psycopg2 as psycopg2
import requests
import xmltodict
import asyncio
from multiprocessing import Process, Queue
from hikvisionapi.hikvisionapi import response_parser
from httpcore.backends import asyncio
from requests.auth import HTTPDigestAuth
url_cam_plate = 'http://186.69.152.58:81/ISAPI/Traffic/channels/1/vehicleDetect/plates'
class Vehicle():

    def __init__(self):
        self.url_cam_plate = 'http://localhost:3000/Plates'
        self.response = requests.get(
            url=self.url_cam_plate,
            stream=True,
        )


    def reader(q: Queue):
        while True:
            job = {'date': datetime.now().isoformat(), 'number': random()}
            q.put(job)
            print('Enqueued new job', job)
            sleep(5)

    def getlastplate(self):

        plate = self.response_parser(self.response)[-1]['plateNumber']
        return self.response_parser(self.response)['plateNumber']

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



p1a = 0;
c1a = datetime.datetime.now();

while True:
    car = Vehicle();
    p1, c1,back = car.getAllplate(1)
    print(p1,c1,back)
    if (p1 != p1a or c1 != c1a):
        conexion = psycopg2.connect(
            "host=tgparkey.postgres.database.azure.com port=5432 dbname=postgres user=cdandrango password=Barcelona97. sslmode=require")
        conexion.set_session(autocommit=True)
        cur = conexion.cursor()
        cur.execute("select exists(SELECT * FROM parqueaderos_vehiculo WHERE placa='{0}')".format(p1))
        print(cur)
        for curs in cur:
            v = curs[0]
        if not v:
            cur.execute("INSERT INTO parqueaderos_vehiculo(placa,color) VALUES(%s,%s) RETURNING id", (p1, "red"))
            res = cur.fetchone()
            last_inserted_id = res[0]
            print(last_inserted_id)
            cur.execute("INSERT INTO parqueaderos_registrobitacora(hora_entrada,id_vehiculo_id) VALUES(%s , %s)",
                    (c1, last_inserted_id))
            print(cur)
        else:
            cur.execute("SELECT id FROM parqueaderos_vehiculo WHERE placa='{0}'".format(p1))
            for curs in cur:
                id=curs[0]
            cur.execute("select exists(SELECT * FROM parqueaderos_registrobitacora WHERE id_vehiculo_id={0} and hora_salida IS NULL)".format(id))
            for curs in cur:
                ex= curs[0]
            if not ex:
              cur.execute("INSERT INTO parqueaderos_registrobitacora(hora_entrada,id_vehiculo_id) VALUES(%s , %s)",
                        (c1, id))
            else:

                cur.execute("SELECT id,hora_entrada FROM parqueaderos_registrobitacora WHERE id_vehiculo_id={0} ORDER BY id Desc LIMIT 1".format(id))
                for curs in cur:
                    ex=curs[0]
                print(ex)
                date=str(curs[1].date())
                da=str(c1).split()

                if da[0] == date:
                    cur.execute("UPDATE parqueaderos_registrobitacora SET hora_salida='{0}' WHERE id={1}".format(c1,ex))
                else:
                    cur.execute("UPDATE parqueaderos_registrobitacora SET hora_salida='{0}' WHERE id={1}".format(da[0] + " " + "23:59:00", ex))
                    cur.execute(
                        "INSERT INTO parqueaderos_registrobitacora(hora_entrada,hora_salida,id_vehiculo_id) VALUES(%s ,%s,%s)",
                        (da[0] + " " + "00:00:00", c1, id))

        cur.close()
        conexion.close()
    p1a = p1
    c1a = c1

