import datetime

import psycopg2
from clases.Vehicle import Vehicle

p1a = 0;
c1a = datetime.datetime.now();
while True:
    car = Vehicle();
    p1, c1,back = car.getAllplate(1)
    if (p1 != p1a or c1 != c1a):
        conexion = psycopg2.connect(
            "host=tgparkey.postgres.database.azure.com port=5432 dbname=postgres user=cdandrango password=Barcelona97. sslmode=require")
        conexion.set_session(autocommit=True)
        cur = conexion.cursor()
        cur.execute("select exists(SELECT * FROM parqueaderos_vehiculo WHERE placa='{0}')".format(p1))
        for curs in cur:
            v = curs[0]
        if not v:
            cur.execute("INSERT INTO parqueaderos_vehiculo(placa,color) VALUES(%s,%s) RETURNING id", (p1, "red"))
            res = cur.fetchone()
            last_inserted_id = res[0]
            cur.execute("INSERT INTO parqueaderos_registrobitacora(hora_entrada,id_vehiculo_id) VALUES(%s , %s)",
                    (c1, last_inserted_id))
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

