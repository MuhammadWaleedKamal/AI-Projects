from fastapi import FastAPI
from fastapi import Request
from fastapi.responses import JSONResponse
import db_helper
import generic_helper

app = FastAPI()

inprogress_order = {}

@app.post("/")
async def read_root(request: Request):
    if request.method == "POST":
        # Retreive the JSON data from request
        payload = await request.json()

        # Extract necessary information from payload based on the structure of the WebhookRequest Dialogflow
        intent = payload["queryResult"]["intent"]["displayName"]
        parameters = payload["queryResult"]["parameters"]
        output_context = payload["queryResult"]["outputContexts"]

        session_id = generic_helper.extract_session_id(output_context[0]["name"])

        intent_handler = {
            "track.order - context: ongoing-tracking": track_order,
            "order.add - context: ongoing-order": add_to_order,
            "order.remove - context: ongoing-order": remove_from_order,
            "order.complete - context: ongoing-order": complete_order,
        }
        
        return intent_handler[intent](parameters, session_id)
    
inprogress_order = {}

# Add order of user
def add_to_order(parameters: dict, session_id: str):
    global inprogress_order
    food_items = parameters["food-item"]
    quantities = parameters["number"]
    
    if len(food_items) != len(quantities):
        fulfillment_text = "Sorry I didn't understand. Can you specify food item and quantities clearly?"
            
    else:
        new_food_item = dict(zip(food_items, quantities))
        
        if session_id in inprogress_order:
            inprogress_order[session_id].update(new_food_item)
            
        else:
            inprogress_order[session_id] = new_food_item
        
        order_str = generic_helper.get_str_from_food_dict(inprogress_order[session_id])
        fulfillment_text = f"So far you have {order_str}. Do you need anything else?"
  
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })    
        
# Function for complete and adding order in MySQL.
def complete_order(parameters: dict, session_id: str):
    if session_id not in inprogress_order:
        fulfillment_text = "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
    
    else:
        order = inprogress_order[session_id]
        order_id = order_to_db(order)
        fulfillment_text = f"Your order has been Placed. Here is you order id # {order_id}"
        
        if order_id == -1:
            fulfillment_text = "Sorry, I couldn't process your order due to a backend error." \
                                "Please place a new order again"
        
        else:
            order_total = db_helper.get_total_order_price(order_id)
            fulfillment_text = f"Awesome. We placed your order" \
                                f"Here is your order id # {order_id}." \
                                    f"Your order total is {order_total} which you can pay at the time of delivery!"
    
    del inprogress_order[session_id]
    
    return JSONResponse({
        "fulfillmentText": fulfillment_text
    })
    
# Add order in MySQL
def order_to_db(order: dict):    
    next_order_id = db_helper.get_next_order_id()
    
    for k, v in order.items():
        quantity_price = db_helper.get_price(k, v)
        item_id = db_helper.get_item_id(k)
        code = db_helper.insert_into_db(next_order_id, item_id, v, quantity_price)
    
        if code == -1:
            return -1
    
    db_helper.insert_order_tracking(next_order_id, "in progress")
    
    return next_order_id

# Remove ordered item.
def remove_from_order(parameters: dict, session_id: str):
    global inprogress_order
    remove_food_item = parameters["food-item"]
    
    if session_id not in inprogress_order:
        return JSONResponse({
            "fulfillmentText": "I'm having a trouble finding your order. Sorry! Can you place a new order please?"
        })
        
    current_order = inprogress_order[session_id]
    removed_item = []
    no_such_items = []
    
    for item in remove_food_item:
        if item not in inprogress_order[session_id]:
            no_such_items.append(item)
            
        else:
            removed_item.append(item)
            del current_order[item]
            
    if len(removed_item) > 0:     
        fulfillment_text = f"Removed {",".join(removed_item)} from your order."
    
    if len(no_such_items) > 0:
        fulfillment_text = f" Your current order doesn't have {",".join(no_such_items)}."
    
    if len(current_order.keys()) == 0:
        fulfillment_text += " Your order is empty."
    
    else:
        order_str = generic_helper.get_str_from_food_dict(current_order)
        fulfillment_text += f" Here is what is left in your order: {order_str}."
        
    return JSONResponse({
        "fulfillmentText": fulfillment_text
    })
    
def track_order(parameters: dict, session_id: str):
    order_id = int(parameters["order_id"])
    order_status = db_helper.get_order_status(order_id)
    
    if order_status:
        fulfillment_text = f"The order status of order id: {order_id} is: {order_status}"
    
    else:
        fulfillment_text = f"No order found with order id: {order_id}"
        
    return JSONResponse(content={
        "fulfillmentText": fulfillment_text
    })
    
    