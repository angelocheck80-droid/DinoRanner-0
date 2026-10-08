CREATE TABLE save_slots (
    slot_name TEXT PRIMARY KEY,
    location_id TEXT NOT NULL,
    player_x REAL NOT NULL,
    player_y REAL NOT NULL,
    player_velocity REAL NOT NULL,
    player_jumping INTEGER NOT NULL CHECK (player_jumping IN (0, 1)),
    location_inside INTEGER NOT NULL CHECK (location_inside IN (0, 1)),
    hp INTEGER NOT NULL CHECK (hp >= 0),
    inventory_capacity INTEGER NOT NULL CHECK (inventory_capacity > 0),
    dialogue_index INTEGER NOT NULL DEFAULT 0 CHECK (dialogue_index >= 0),
    saved_at TEXT NOT NULL
);

CREATE TABLE inventory_items (
    slot_name TEXT NOT NULL REFERENCES save_slots(slot_name) ON DELETE CASCADE,
    item_name TEXT NOT NULL,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    max_stack INTEGER NOT NULL CHECK (max_stack > 0),
    PRIMARY KEY (slot_name, item_name)
);
