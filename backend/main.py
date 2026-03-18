from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.tools import tools
from database.services import (
    chat_with_llm,
    search_by_area,
    get_restaurant,
    add_to_cart,
    view_cart,
    place_order,
)

app = FastAPI(title="Restaurant AI Chatbot")

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

session_histories: dict[str, list] = {}

# --------------------------------------------------
# REQUEST MODELS
# --------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class CartItem(BaseModel):
    restaurant_id: int
    item_name: str
    quantity: int

# ✅ NEW: Model to handle data from the Checkout Modal
class OrderDetails(BaseModel):
    address: str
    phone: str
    payment_method: str

# --------------------------------------------------
# CHAT ENDPOINT
# --------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    history = session_histories.get(req.session_id, [])
    reply, updated_history = chat_with_llm(req.message, history)
    session_histories[req.session_id] = updated_history
    return {"response": reply}

# --------------------------------------------------
# MCP TOOLS LIST
# --------------------------------------------------
@app.get("/tools")
def get_tools():
    return tools

# --------------------------------------------------
# MCP TOOL EXECUTION ENDPOINT
# --------------------------------------------------
@app.post("/mcp")
async def mcp_handler(request: dict):
    tool_name = request.get("tool")
    arguments  = request.get("arguments", {})

    if tool_name == "search_by_area":
        result = search_by_area(arguments["area"])
    elif tool_name == "get_restaurant":
        result = get_restaurant(int(arguments["restaurant_id"]))
    elif tool_name == "add_to_cart":
        result = add_to_cart(
            int(arguments["restaurant_id"]),
            arguments["item_name"],
            int(arguments["quantity"]),
        )
    elif tool_name == "view_cart":
        result = view_cart()
    elif tool_name == "place_order":
        # Note: Tool-based orders will use defaults if details aren't passed
        result = place_order()
    else:
        return {"status": "error", "message": f"Unknown tool: {tool_name}"}

    return {"status": "success", "tool": tool_name, "data": result}

# --------------------------------------------------
# REST ROUTES
# --------------------------------------------------
@app.get("/restaurants/search/")
def search_restaurants(area: str):
    return search_by_area(area)

@app.get("/restaurants/{restaurant_id}")
def get_restaurant_by_id(restaurant_id: int):
    result = get_restaurant(restaurant_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result

@app.post("/cart/add")
def add_cart(item: CartItem):
    return add_to_cart(item.restaurant_id, item.item_name, item.quantity)

@app.get("/cart")
def get_cart():
    return view_cart()

# ✅ UPDATED: Now receives address, phone, and payment from the frontend Modal
@app.post("/order/place")
def order(details: OrderDetails):
    return place_order(
        address=details.address,
        phone=details.phone,
        payment=details.payment_method
    )