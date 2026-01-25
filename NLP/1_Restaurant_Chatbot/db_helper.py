import mysql.connector

cnx = mysql.connector.connect(
        host="localhost",
        user="root",
        password="waleedkamal801@gmail.com",
        database="pandeyji_eatery"
    )

def get_order_status(order_id: int):
    cur = cnx.cursor()
    
    # Write SQL Query
    query = ("Select status from order_tracking where order_id = %s")
    
    # Execute the Query
    cur.execute(query, (order_id,))
    
    # Fetch the result
    result = cur.fetchone()
    
    # Close cursor
    cur.close()
    
    if result is not None:
        return result[0]

    else:
        return None

def get_next_order_id():
    
    cur = cnx.cursor()
    
    query_max_order = "Select max(order_id) from orders"
    
    cur.execute(query_max_order)
    
    result = cur.fetchone()[0]
    
    cur.close()
    print(result)
    if result is None:
        return 1

    else:
        return result + 1
    

    
def get_price(item: str, quantity: float):
    cur = cnx.cursor()
    
    query = "select price from food_items where name = %s"
    print(item)
    
    cur.execute(query, (item,))
    
    result = cur.fetchone()[0]
    
    if result is not None:
        return float(result)*quantity
    
    else:
        return 1
    
def get_item_id(item: str):
    cur = cnx.cursor()
    
    query = "select item_id from food_items where name = %s"
    
    cur.execute(query, (item,))
    
    result = cur.fetchone()[0]
    
    if result is not None:
        return result
    
    else:
        return -1
    
def insert_into_db(order_max: int, item_id: int, v: int, quantity_price: int):
    try:
        cur = cnx.cursor()
        
        query = "Insert into orders (order_id, item_id, quantity, total_price) values (%s, %s, %s, %s)"
        
        values = (order_max, item_id, v, quantity_price)
        
        cur.execute(query, values)
        
        cnx.commit()
        
        return 1
    
    except:
        cnx.rollback()
        return -1

def get_total_order_price(order_id):
    cur = cnx.cursor()
    
    query = "Select sum(total_price) from orders where order_id = %s"
    
    cur.execute(query, (order_id,))
    
    result = cur.fetchone()[0]
    
    if result:
        return float(result)
    
    else:
        return -1
     

def insert_order_tracking(order_id: int, status: str):
    cur = cnx.cursor()
    
    query = "Insert into order_tracking (order_id, status) values (%s, %s)"
    
    cur.execute(query, (order_id, status))
    
    cnx.commit()
    
    return 1
    
    
    