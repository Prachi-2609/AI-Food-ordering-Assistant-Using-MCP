import ollama
import re
from database.database import get_connection
from backend.tools import tools
import json
# --------------------------------------------------
# DATABASE SERVICE FUNCTIONS
# --------------------------------------------------

def search_by_area(area: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM restaurants WHERE LOWER(area) = LOWER(?)",
        (area.strip(),)
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_restaurant(restaurant_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, price FROM menu WHERE restaurant_id = ?", (int(restaurant_id),))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return "CRITICAL ERROR: No data found in database for this ID."

    # We label this as "ONLY AVAILABLE ITEMS" to trigger the AI's logic
    menu_string = "\n".join([f"{row[0]} - Rs.{row[1]}" for row in rows])
    return f"STRICT MENU DATA FOR ID {restaurant_id}:\n{menu_string}\nEND OF DATA."

def add_to_cart(restaurant_id: int, item_name: str, quantity: int):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. VALIDATION: Check if item exists
        cursor.execute(
            "SELECT price FROM menu WHERE restaurant_id = ? AND LOWER(item_name) = LOWER(?)",
            (int(restaurant_id), item_name.strip())
        )
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return {"status": "error", "message": f"Sorry, '{item_name}' is not on the menu for this restaurant."}
        
        # 2. Insert into cart
        price = row[0]
        cursor.execute(
            "INSERT INTO cart (restaurant_id, item_name, price, quantity) VALUES (?, ?, ?, ?)",
            (int(restaurant_id), item_name.strip(), price, int(quantity))
        )
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "message": f"Added {quantity}x {item_name} (Rs.{price} each) to cart"
        }
    except Exception as e:
        print(f"Error in add_to_cart: {e}")
        return {"status": "error", "message": "Database error occurred while adding to cart."}

def view_cart():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cart")
    rows = cursor.fetchall()
    conn.close()
    return rows


def place_order(address="Not Provided", phone="Not provided", payment="COD"):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. Get items from cart
        cursor.execute("SELECT restaurant_id, item_name, price, quantity FROM cart")
        cart_items = cursor.fetchall()
        
        if not cart_items:
            return {"status": "empty", "message": "Your cart is empty."}

        total_price = 0
        # 2. Move each item to orders table
        for item in cart_items:
            res_id, name, price, qty = item
            cursor.execute(
                "INSERT INTO orders (restaurant_id, item_name, price, quantity, address, phone, payment_method) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (res_id, name, price, qty, address, phone, payment)
            )
            total_price += price * qty
            
        # 3. Clear the cart
        cursor.execute("DELETE FROM cart")
        conn.commit()
        
        return {
            "status": "success", 
            "total_price": total_price, 
            "total_items": len(cart_items)
        }
    except Exception as e:
        print(f"Order Placement Error: {e}")
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()


# --------------------------------------------------
# FORMATTING HELPERS
# --------------------------------------------------

def format_restaurants(restaurants):
    if not restaurants:
        return "No restaurants found in that area. Try: Lucknow, Delhi, or Mumbai."
    text = "Restaurants found:\n\n"
    for r in restaurants:
        text += f"- [{r[0]}] {r[1]} - {r[2]} Rating: {r[3]}\n"
    text += "\nAsk me to show the menu of any restaurant by its ID!"
    return text


def format_restaurant_detail(data):
    if "error" in data:
        return f"Error: {data['error']}"
    text = f"Restaurant: {data['name']} (ID: {data['id']})\n"
    text += f"Area: {data['area']} | Rating: {data['rating']}\n\n"
    text += "Menu:\n"
    for item in data["menu"]:
        text += f"- {item['item']} - Rs.{item['price']}\n"
    return text


def format_cart(items):
    if not items:
        return "Your cart is empty."
    text = "Items in your cart:\n\n"
    total = 0
    for item in items:
        subtotal = item[3] * item[4]
        total += subtotal
        text += f"- {item[2]} x {item[4]} = Rs.{subtotal}\n"
    text += f"\nTotal: Rs.{round(total, 2)}"
    return text


def format_order_result(result):
    if result["status"] == "empty":
        return "Your cart is empty. Add items before placing an order."
    return (
        f"Order placed successfully!\n\n"
        f"Items ordered: {result['total_item']}\n"
        f"Total bill: Rs.{result['total_price']}\n"
        f"Your food will arrive soon!"
    )


# --------------------------------------------------
# TOOL EXECUTOR
# --------------------------------------------------


def add_to_cart(restaurant_id=None, item_name="", quantity=1):
    conn = None
    try:
        conn = get_connection()
        cursor = conn.cursor()
        
        # 1. CLEANING: Sirf dish ka naam bache
        clean_item = str(item_name).lower()
        for word in ["order", "add", "from", "restaurant", "id", "please", "want"]:
            clean_item = clean_item.replace(word, "")
        clean_item = re.sub(r'\d+', '', clean_item).strip()

        # 2. STRICT VALIDATION: Check if ID and Item match in DB
        # Agar ID di hai toh sirf usi restaurant ke menu mein search karo
        if restaurant_id and int(restaurant_id) != 0:
            cursor.execute(
                "SELECT price, item_name FROM menu WHERE restaurant_id = ? AND LOWER(item_name) LIKE LOWER(?)",
                (int(restaurant_id), f"%{clean_item}%")
            )
        else:
            # Fallback: Agar ID bilkul nahi mili toh error do bajaye kisi bhi restaurant se uthane ke
            return "❌ Please specify the Restaurant ID so I can add the correct item."

        row = cursor.fetchone()
        
        if not row:
            return f"❌ Sorry, '{clean_item}' is not on the menu of Restaurant ID {restaurant_id}."
        
        price = row[0]
        actual_item_name = row[1]

        # 3. INSERT INTO CART
        cursor.execute(
            "INSERT INTO cart (restaurant_id, item_name, price, quantity) VALUES (?, ?, ?, ?)",
            (int(restaurant_id), actual_item_name, float(price), int(quantity))
        )
        conn.commit()
        return f"✅ **{actual_item_name}** added! Add more or **Proceed to Checkout**? 🛒"

    except Exception as e:
        print(f"DB Error: {e}")
        return "⚠️ Database error. Please try again."
    finally:
        if conn: conn.close()

def execute_tool(tool_name: str, args: dict):
    if tool_name == "search_by_area":
        rows = search_by_area(args.get("area", ""))
        return format_restaurants(rows)
        
    elif tool_name == "get_restaurant":
        # Restaurant ID ko integer mein convert karna zaroori hai
        res_id = args.get("restaurant_id", 0)
        return get_restaurant(int(res_id) if res_id else 0)
        
    elif tool_name == "add_to_cart":
        # ✅ SMART FIX: Naya add_to_cart ab seedha string return karta hai
        return add_to_cart(
            restaurant_id=args.get("restaurant_id", 0),
            item_name=args.get("item_name", ""),
            quantity=args.get("quantity", 1)
        )

    elif tool_name == "view_cart":
        items = view_cart()
        return format_cart(items)
        
    elif tool_name == "place_order":
        # Note: Frontend modal se details aayengi, par tool call fallback ke liye
        result = place_order()
        return format_order_result(result)
        
    return "Unknown tool requested."


# --------------------------------------------------
# PARSE A SINGLE TOOL CALL LINE
# e.g. search_by_area("Delhi")
#      get_restaurant(2)
#      add_to_cart(2, "Burger", 1)
#      view_cart()
#      place_order()
# --------------------------------------------------

def parse_single_tool_call(line: str):
    """
    Try to parse one line as a tool call.
    Handles both positional and keyword argument formats:
      search_by_area("Delhi")          or  search_by_area(area="Delhi")
      get_restaurant(2)                or  get_restaurant(restaurant_id=2)
      add_to_cart(2, "Burger", 1)      or  add_to_cart(restaurant_id=2, item_name="Burger", quantity=1)
    Returns (tool_name, args_dict) or None if not a tool call.
    """
    line = line.strip()
    # Handle JSON format: {"name": "get_restaurant", "parameters": {"restaurant_id": "4"}}
    import json
    try:
        obj = json.loads(line)
        if isinstance(obj, dict) and "name" in obj:
            tool_name = obj["name"]
            params = obj.get("parameters", obj.get("arguments", {}))
            if "restaurant_id" in params:
                params["restaurant_id"] = int(params["restaurant_id"])
            if "quantity" in params:
                params["quantity"] = int(params["quantity"])
            return (tool_name, params)
    except (json.JSONDecodeError, ValueError):
        pass
    # --- search_by_area ---
    # positional: search_by_area("Delhi")
    m = re.match(r'search_by_area\(\s*["\']([^"\']+)["\']\s*\)', line)
    if m:
        return ("search_by_area", {"area": m.group(1).strip()})
    # keyword: search_by_area(area="Delhi")
    m = re.match(r'search_by_area\(\s*area\s*=\s*["\']([^"\']+)["\']\s*\)', line)
    if m:
        return ("search_by_area", {"area": m.group(1).strip()})

    # --- get_restaurant ---
    # positional: get_restaurant(2)
    m = re.match(r'get_restaurant\(\s*(\d+)\s*\)', line)
    if m:
        return ("get_restaurant", {"restaurant_id": int(m.group(1))})
    # keyword: get_restaurant(restaurant_id=2)
    m = re.match(r'get_restaurant\(\s*restaurant_id\s*=\s*(\d+)\s*\)', line)
    if m:
        return ("get_restaurant", {"restaurant_id": int(m.group(1))})

    # --- add_to_cart ---
    # positional: add_to_cart(2, "Burger", 1)
    m = re.match(r'add_to_cart\(\s*(\d+)\s*,\s*["\']([^"\']+)["\']\s*,\s*(\d+)\s*\)', line)
    if m:
        return ("add_to_cart", {
            "restaurant_id": int(m.group(1)),
            "item_name":     m.group(2),
            "quantity":      int(m.group(3)),
        })
    # keyword: add_to_cart(restaurant_id=2, item_name="Burger", quantity=1)
    m = re.search(
        r'add_to_cart\(.*?restaurant_id\s*=\s*(\d+).*?item_name\s*=\s*["\']([^"\']+)["\'].*?quantity\s*=\s*(\d+).*?\)',
        line
    )
    if m:
        return ("add_to_cart", {
            "restaurant_id": int(m.group(1)),
            "item_name":     m.group(2),
            "quantity":      int(m.group(3)),
        })

    # --- view_cart ---
    if re.match(r'view_cart\(\s*\)', line):
        return ("view_cart", {})

    # --- place_order ---
    if re.match(r'place_order\(\s*\)', line):
        return ("place_order", {})

    return None


# --------------------------------------------------
# ✅ HANDLE MULTI-TOOL TEXT RESPONSES
# Handles <|python_tag|> prefix and multiple tool
# calls written across multiple lines
# --------------------------------------------------

def extract_and_run_text_tool_calls(text: str):
    """
    Strips <|python_tag|> and similar tags, then scans every line
    for tool calls and executes ALL of them in order.
    Returns combined results string, or None if no tool calls found.
    """
    # Strip special LLM tags like <|python_tag|>
    text = re.sub(r'<\|[^|]+\|>', '', text).strip()

    # Try parsing whole text as a single JSON tool call
    import json
    try:
        obj = json.loads(text)
        if isinstance(obj, dict) and "name" in obj:
            parsed = parse_single_tool_call(text)
            if parsed:
                tool_name, args = parsed
                return execute_tool(tool_name, args)
    except (json.JSONDecodeError, ValueError):
        pass

    lines = text.splitlines()
    results = []

    for line in lines:
        parsed = parse_single_tool_call(line.strip())
        if parsed:
            tool_name, args = parsed
            result = execute_tool(tool_name, args)
            results.append(result)

    return "\n\n".join(results) if results else None


# --------------------------------------------------
# LLM TOOL-CALL FLOW

SYSTEM_PROMPT = """
You are a helpful Food Ordering Assistant. 
1. When a user says "order [item]", ALWAYS call the 'add_to_cart' tool.
2. If you don't know the restaurant_id, use 0. Our system will find it.
3. After adding an item, ALWAYS ask: "Would you like to add more items, or proceed to checkout?"
4. DO NOT repeat function names like add_to_cart() in the chat.
5. Keep track of the context. If the user adds one item, and then another, acknowledge both.
"""

def chat_with_llm(user_prompt: str, history: list):
    text = user_prompt.lower().strip()

    # --- 1. CONTEXT EXTRACTOR (History se aakhri Restaurant ID nikalna) ---
    last_viewed_id = 0
    for msg in reversed(history):
        id_match = re.search(r'ID:\s*(\d+)', msg['content'])
        if id_match:
            last_viewed_id = int(id_match.group(1))
            break

    # --- 2. ORDER LOGIC (Strict Mapping) ---
    if any(w in text for w in ["order", "add", "want"]):
        # A. Current message mein ID dhoondo
        msg_id_match = re.search(r'id\s*(\d+)', text)
        target_id = int(msg_id_match.group(1)) if msg_id_match else last_viewed_id
        
        if target_id == 0:
            return "I need to know which restaurant you're ordering from. Please use the Restaurant ID.", history

        # B. Call the strict add function
        db_res = add_to_cart(restaurant_id=target_id, item_name=text)
        return db_res, history + [{"role": "user", "content": user_prompt}, {"role": "assistant", "content": db_res}]

    # --- 3. VIEW CART / CHECKOUT ---
    if any(w in text for w in ["view", "cart", "checkout"]):
        result = format_cart(view_cart())
        if "empty" not in result.lower():
            result += "\n\nReady? Click **Proceed to Checkout**! 🛒"
        return result, history + [{"role": "user", "content": user_prompt}, {"role": "assistant", "content": result}]

    # --- 4. CITY DETECTION ---
    city = next((c.capitalize() for c in ["lucknow", "delhi", "mumbai"] if c in text), None)
    if city:
        restaurants = search_by_area(city)
        menu_summary = f"Restaurants in {city}. Use the ID to order:\n"
        for r in restaurants:
            menu_summary += f"\n🍴 **{r[1]}** (ID: {r[0]})\n{get_restaurant(r[0])}\n"
        return menu_summary, history + [{"role": "user", "content": user_prompt}, {"role": "assistant", "content": menu_summary}]

    return "I can help you order! Just say 'order [item]' or name a city like Delhi.", history