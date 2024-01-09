import pymysql


def db_con():
    return pymysql.connect(
        host="localhost",
        db="sportiton",
        user="root",
        password="",
    )
