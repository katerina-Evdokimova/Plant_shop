def get_count_plants(cart: dict):
    return sum(cart.values()) if cart else 0 