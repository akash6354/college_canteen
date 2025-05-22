from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from pymongo import MongoClient
from bson import ObjectId

app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# MongoDB connection
client = MongoClient("mongodb+srv://proversionofakash:yXmPmDDhLvZfSx62@cluster0.eiefq2m.mongodb.net/?retryWrites=true&w=majority&tls=true&appName=Cluster0")
db = client.canteen_db
foods_collection = db.foods
orders_collection = db.orders

# Pydantic models
class FoodItem(BaseModel):
    name: str
    price: float
    image: str = ""

class OrderItem(BaseModel):
    name: str
    price: float
    qty: int

class OrderCreate(BaseModel):
    name: str
    phone: str
    room: str
    items: list[OrderItem]
    total: float

# Routes
@app.get("/api/foods")
async def get_foods():
    foods = list(foods_collection.find())
    for food in foods:
        food["_id"] = str(food["_id"])
    return foods

@app.post("/api/place-order")
async def place_order(order: OrderCreate):
    order_data = order.dict()
    order_data["timestamp"] = datetime.now()
    result = orders_collection.insert_one(order_data)
    return {"id": str(result.inserted_id), "status": "Order placed"}

@app.get("/api/orders")
async def get_orders():
    orders = list(orders_collection.find().sort("timestamp", -1))
    for order in orders:
        order["_id"] = str(order["_id"])
        order["timestamp"] = order["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    return orders

@app.delete("/api/orders/{order_id}")
async def delete_order(order_id: str):
    try:
        obj_id = ObjectId(order_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid order ID")
    
    result = orders_collection.delete_one({"_id": obj_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"status": "Order deleted successfully"}

