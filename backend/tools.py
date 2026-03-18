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
        "description": "Add a food item to the cart.",
        "parameters": {
            "type": "object",
            "properties": {
                "restaurant_id": {"type": "integer", "description": "ID of the restaurant (use 0 if unknown)"},
                "item_name":     {"type": "string",  "description": "Name of the item"},
                "quantity":      {"type": "integer", "description": "Number of items (default 1)"}
            },
            "required": ["item_name"] # Sirf item_name zaroori rakho
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
