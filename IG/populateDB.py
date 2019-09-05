import mysql.connector
from datetime import datetime

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="password",
    database="demotrading"
)

mycursor = mydb.cursor()


def insertStreamPrice():

    sqlSelect = ("SELECT * from api_subproduct")
    mycursor.execute(sqlSelect)
    subProducts = mycursor.fetchall()

    for item in subProducts:
        subProductId = item[0]
        sqlSelect = """SELECT * FROM api_streamprice WHERE subproduct_id = '%s'""" % (
            subProductId)
        mycursor.execute(sqlSelect)
        streamprice = mycursor.fetchone()

        if (streamprice is None):

            sqlInsert = (
                "INSERT INTO api_streamprice (bid, offer, ts, subProduct_id) VALUES (%s, %s, %s, %s)")
            valInsert = (0, 0, datetime.timestamp(
                datetime.now()), subProductId)
            mycursor.execute(sqlInsert, valInsert)
            # dt_object = datetime.fromtimestamp(timestamp)

    mydb.commit()


def insertGreeks():

    sqlSelect = ("SELECT * from api_subproduct WHERE callPut != ''")
    mycursor.execute(sqlSelect)
    subProducts = mycursor.fetchall()

    for item in subProducts:
        subProductId = item[0]
        sqlSelect = """SELECT * FROM api_greeks WHERE subProduct_id = '%s'""" % (
            subProductId)
        mycursor.execute(sqlSelect)
        greeks = mycursor.fetchone()

        if (greeks is None):

            sqlInsert = (
                "INSERT INTO api_greeks (subProduct_id, iv, delta, gamma, vega, theta, rho, ts) VALUES (%s, %s, %s,%s, %s, %s, %s, %s)")
            valInsert = (subProductId, 0, 0, 0, 0, 0, 0, datetime.now())

            mycursor.execute(sqlInsert, valInsert)
            # dt_object = datetime.fromtimestamp(timestamp)

    mydb.commit()


def insertSubProducts():

    # sql = ("INSERT INTO api_subproduct (name, callPut, strike, product_id, expiryType) VALUES (%s, %s, %s, %s, %s)")
    # val = [
    #     ("OP.D.STXE1.3200P.IP", "P", 3200, 4, "E"),
    #     ("OP.D.STXE1.3225P.IP", "P", 3225, 4, "E"),
    #     ("OP.D.STXE1.3250P.IP", "P", 3250, 4, "E"),
    #     ("OP.D.STXE1.3275P.IP", "P", 3275, 4, "E"),
    #     ("OP.D.STXE1.3300P.IP", "P", 3300, 4, "E"),
    #     ("OP.D.STXE1.3325P.IP", "P", 3325, 4, "E"),
    #     ("OP.D.STXE1.3350P.IP", "P", 3350, 4, "E"),
    #     ("OP.D.STXE1.3375P.IP", "P", 3375, 4, "E"),
    #     ("OP.D.STXE1.3400P.IP", "P", 3400, 4, "E"),
    #     ("OP.D.STXE1.3425P.IP", "P", 3425, 4, "E"),
    #     ("OP.D.STXE1.3450P.IP", "P", 3450, 4, "E"),
    #     ("OP.D.STXE1.3475P.IP", "P", 3475, 4, "E"),
    #     ("OP.D.STXE1.3500P.IP", "P", 3500, 4, "E"),
    #     ("OP.D.STXE1.3525P.IP", "P", 3525, 4, "E"),
    #     ("OP.D.STXE1.3550P.IP", "P", 3550, 4, "E"),
    #     ("OP.D.STXE1.3575P.IP", "P", 3575, 4, "E"),
    #     ("OP.D.STXE1.3200C.IP", "C", 3200, 4, "E"),
    #     ("OP.D.STXE1.3225C.IP", "C", 3225, 4, "E"),
    #     ("OP.D.STXE1.3250C.IP", "C", 3250, 4, "E"),
    #     ("OP.D.STXE1.3275C.IP", "C", 3275, 4, "E"),
    #     ("OP.D.STXE1.3300C.IP", "C", 3300, 4, "E"),
    #     ("OP.D.STXE1.3325C.IP", "C", 3325, 4, "E"),
    #     ("OP.D.STXE1.3350C.IP", "C", 3350, 4, "E"),
    #     ("OP.D.STXE1.3375C.IP", "C", 3375, 4, "E"),
    #     ("OP.D.STXE1.3400C.IP", "C", 3400, 4, "E"),
    #     ("OP.D.STXE1.3425C.IP", "C", 3425, 4, "E"),
    #     ("OP.D.STXE1.3450C.IP", "C", 3450, 4, "E"),
    #     ("OP.D.STXE1.3475C.IP", "C", 3475, 4, "E"),
    #     ("OP.D.STXE1.3500C.IP", "C", 3500, 4, "E"),
    #     ("OP.D.STXE1.3525C.IP", "C", 3525, 4, "E"),
    #     ("OP.D.STXE1.3550C.IP", "C", 3550, 4, "E"),
    #     ("OP.D.STXE1.3575C.IP", "C", 3575, 4, "E"),
    # ]
    # mycursor.executemany(sql, val)

    # Future / Spot / D1
    sql = ("INSERT INTO api_subproduct (name, callPut, strike, product_id, expiryType) VALUES (%s, %s, %s, %s, %s)")
    val = [
        ("L1:CS.D.USDJPY.TODAY.IP", "", 0, 22, ""),
        ("L1:CS.D.GBPUSD.TODAY.IP", "", 0, 23, "")
    ]
    mycursor.executemany(sql, val)

    # Future / Spot / D1
    # sql = ("INSERT INTO api_subproduct (name, callPut, strike, product_id, expiryType) VALUES (%s, %s, %s, %s, %s)")
    # val = ("IX.D.STXE.MONTH2.IP",  "", 0, 5, "")

    # Future / Spot / D1
    # sql = ("INSERT INTO api_subproduct (name, callPut, strike, product_id, expiryType) VALUES (%s, %s, %s, %s, %s)")
    # val = ("CS.D.BITCOIN.TODAY.IP",  "", 0, 7, "")

    # sql = ("INSERT INTO api_subproduct (name, callPut, strike, product_id, expiryType) VALUES (%s, %s, %s, %s, %s)")
    # val = ("L1:IX.D.DAX.DAILY.IP",  "", 0, 10, "")
    # mycursor.execute(sql, val)

    # # Options
    # sql = ("INSERT INTO api_subproduct (name, callPut, strike, product_id, expiryType) VALUES (%s, %s, %s, %s, %s)")
    # val = [
    #     ("L1:OP.D.DAX3.011700C.IP", "C", 11700, 1, ''),
    #     ("L1:OP.D.DAX3.011750C.IP", "C", 11750, 1, ''),
    #     ("L1:OP.D.DAX3.011800C.IP", "C", 11800, 1, ''),
    #     ("L1:OP.D.DAX3.011850C.IP", "C", 11850, 1, ''),
    #     ("L1:OP.D.DAX3.011900C.IP", "C", 11900, 1, ''),
    #     ("L1:OP.D.DAX3.011700P.IP", "P", 11700, 1, ''),
    #     ("L1:OP.D.DAX3.011750P.IP", "P", 11750, 1, ''),
    #     ("L1:OP.D.DAX3.011800P.IP", "P", 11800, 1, ''),
    #     ("L1:OP.D.DAX3.011850P.IP", "P", 11850, 1, ''),
    #     ("L1:OP.D.DAX3.011900P.IP", "P", 11900, 1, ''),
    # ]
    # mycursor.executemany(sql, val)

#     val = [
#         ("L1:OP.D.STXE2.3200P.IP", "P", 3200, 6, "E"),
#         ("L1:OP.D.STXE2.3225P.IP", "P", 3225, 6, "E"),
#         ("L1:OP.D.STXE2.3250P.IP", "P", 3250, 6, "E"),
#         ("L1:OP.D.STXE2.3275P.IP", "P", 3275, 6, "E"),
#         ("L1:OP.D.STXE2.3300P.IP", "P", 3300, 6, "E"),
#         ("L1:OP.D.STXE2.3325P.IP", "P", 3325, 6, "E"),
#         ("L1:OP.D.STXE2.3350P.IP", "P", 3350, 6, "E"),
#         ("L1:OP.D.STXE2.3375P.IP", "P", 3375, 6, "E"),
#         ("L1:OP.D.STXE2.3400P.IP", "P", 3400, 6, "E"),
#         ("L1:OP.D.STXE2.3425P.IP", "P", 3425, 6, "E"),
#         ("L1:OP.D.STXE2.3450P.IP", "P", 3450, 6, "E"),
#         ("L1:OP.D.STXE2.3475P.IP", "P", 3475, 6, "E"),
#         ("L1:OP.D.STXE2.3500P.IP", "P", 3500, 6, "E"),
#         ("L1:OP.D.STXE2.3525P.IP", "P", 3525, 6, "E"),
#         ("L1:OP.D.STXE2.3550P.IP", "P", 3550, 6, "E"),
#         ("L1:OP.D.STXE2.3575P.IP", "P", 3575, 6, "E"),
#         ("L1:OP.D.STXE2.3200C.IP", "C", 3200, 6, "E"),
#         ("L1:OP.D.STXE2.3225C.IP", "C", 3225, 6, "E"),
#         ("L1:OP.D.STXE2.3250C.IP", "C", 3250, 6, "E"),
#         ("L1:OP.D.STXE2.3275C.IP", "C", 3275, 6, "E"),
#         ("L1:OP.D.STXE2.3300C.IP", "C", 3300, 6, "E"),
#         ("L1:OP.D.STXE2.3325C.IP", "C", 3325, 6, "E"),
#         ("L1:OP.D.STXE2.3350C.IP", "C", 3350, 6, "E"),
#         ("L1:OP.D.STXE2.3375C.IP", "C", 3375, 6, "E"),
#         ("L1:OP.D.STXE2.3400C.IP", "C", 3400, 6, "E"),
#         ("L1:OP.D.STXE2.3425C.IP", "C", 3425, 6, "E"),
#         ("L1:OP.D.STXE2.3450C.IP", "C", 3450, 6, "E"),
#         ("L1:OP.D.STXE2.3475C.IP", "C", 3475, 6, "E"),
#         ("L1:OP.D.STXE2.3500C.IP", "C", 3500, 6, "E"),
#         ("L1:OP.D.STXE2.3525C.IP", "C", 3525, 6, "E"),
#         ("L1:OP.D.STXE2.3550C.IP", "C", 3550, 4, "E"),
#         ("L1:OP.D.STXE2.3575C.IP", "C", 3575, 6, "E"),
#     ]
#     mycursor.executemany(sql, val)
# #
#     mydb.commit()


def insertProducts():

    # Option
    # sql = ("INSERT INTO api_product (name, productType, expiry, expiryDate, contractSize) VALUES (%s, %s, %s, %s, %s)")
    # now = datetime(2019, 12, 20, 11, 00)
    # val = ("ODAX", "O", "DEC19", now.strftime('%Y-%m-%d %H:%M:%S'), 5)
    # mycursor.execute(sql, val)

    # now = datetime(2019, 12, 20, 11, 00)
    # val = ("SX5E", "O", "DEC19", now.strftime('%Y-%m-%d %H:%M:%S'), 10)
    # mycursor.execute(sql, val)

    #Future / Spot / D1
    sql = ("INSERT INTO api_product (name, productType, expiryDisplay, expiryTime, contractSize, hedgeSubProductId) VALUES (%s, %s, %s, %s, %s, %s)")
    val = ("GBPUSD", "S", "", 0, 0.0001, 0)
    mycursor.execute(sql, val)

    # sql = ("INSERT INTO api_product (name, productType, expiryDisplay, expiryTime, contractSize, hedgeSubProductId) VALUES (%s, %s, %s, %s, %s, %s)")
    # now = datetime(2019, 9, 20, 11, 00)
    # val = ("FDAX", "F", "SEP19", now.strftime('%Y-%m-%d %H:%M:%S'), 25)
    # mycursor.execute(sql, val)

    # now = datetime(2019, 9, 20, 11, 00)
    # val = ("FESX", "F", "SEP19", now.strftime('%Y-%m-%d %H:%M:%S'), 10)
    # mycursor.execute(sql, val)

    # now = datetime(2019, 9, 20, 11, 00)
    # val = ("BTCUSD", "F", "", now.strftime('%Y-%m-%d %H:%M:%S'), 1)
    # mycursor.execute(sql, val)

    # now = datetime(2019, 9, 20, 11, 00)
    # val = ("FDAX", "S", "", now.strftime('%Y-%m-%d %H:%M:%S'), 5, 0)
    # mycursor.execute(sql, val)

    # now = datetime(2019, 9, 20, 11, 00)
    # val = ("ODAX", "O", "SEP19", now.strftime('%Y-%m-%d %H:%M:%S'), 5, 40)
    # mycursor.execute(sql, val)

    mydb.commit()


def insertStatics():

    pass


def main():

    insertProducts()
    insertSubProducts()
    insertStreamPrice()
    # insertStatics()
    # insertGreeks()


if __name__ == '__main__':
    main()
