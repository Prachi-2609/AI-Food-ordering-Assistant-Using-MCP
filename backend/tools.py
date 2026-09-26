tools = [
    {
        "name": "search_by_area",
        "description": "Search restaurants by area/city name. Use this when user asks what restaurants are available in a location.",
        "parameters": {
            "type": "object",
            "properties": {
                "area": {"type": "string", "description": "City or area name e.g. Delhi, Lucknow, Mumbai"}
            },
            "required": ["area"]
        }
    },
    {
        "name": "get_restaurant",
        "description": "Get full details and menu of a restaurant by its ID. Use this when user wants to see the menu.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer", "description": "The numeric ID of the restaurant"}
            },
            "required": ["restaurant_id"]
        }
    },
    {
        "name": "add_to_cart",
        "description": "Add an item to the cart ONLY if that exact item is present in the menu returned by get_restaurant for the selected restaurant. NEVER invent or guess an item. If the user asks for an item that is not in the menu, do not call this tool.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {
                    "type": "integer",
                    "description": "ID of the restaurant"
                },
                "item_name": {
                    "type": "string",
                    "description": "Exact name of a menu item that is actually available at the selected restaurant. Never invent an item."
                },
                "quantity": {
                    "type": "integer",
                    "description": "Number of items to add. Default is 1."
                }
            },
            "required": ["item_name"]
        }
    },
    {
        "name": "view_cart",
        "description": "View all items currently in the user's cart.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "place_order",
        "description": "Place the order for all items in the cart and clear the cart.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]
