"""
elements.py — Element IDs, palettes, names, physics tables, and colour helpers.
Imported by sandbox.py via: from elements import *
"""

# ── Element IDs ───────────────────────────────────────────────────────────────
(EMPTY, SAND, WATER, WOOD, FIRE, STONE, LAVA, SMOKE, STEAM, ACID,
 PLANT, CLOUD, DIRT, SAPLING, LEAF, OIL, ICE, ANIMAL, SNOW, GUNPOWDER,
 GLASS, MUD, VINE, EMBER, SALT, FUNGUS, LIGHTNING, OBSIDIAN, CRYSTAL,
 CHARCOAL, RUST, WETDIRT, ASH, PRESSGAS, MAGMA,
 SLIME, TAR, CONCRETE, CEMENT, GOLD, GRAVEL, MOSS, HONEY, WAX,
 POISON, SEED, RUBBER, WIRE, CHARGED, BUBBLE, SPORE,
 MERCURY, NEON, PLASMA, CLAY, CERAMIC, RESIN, BASALT,
 PEAT, SEAWEED, JELLYFISH, CORAL, SANDSTONE, AIR,
 METHANE, NITRO, QUICKSAND, STEEL, SUGAR, URANIUM, VOID,
 BIRD, FISH, PREDATOR, HUMAN, HYDROGEN, SULFUR, HELIUM, COAL, COPPER,
 TIGER, LION, WHALE, DOLPHIN,
 WHEAT, APPLE, BERRY, BREAD, MEAT,
 BEAR, SNAKE, RABBIT, SPIDER, BEE, FROG, WEB,
 MUSHROOM, CORN, CARROT, COOKED_MEAT, DOUGH,
 FORGE,
 ANVIL,
 BOOK,
) = range(104)

# ── Hex → RGB helper ──────────────────────────────────────────────────────────
def hx(h):
    """Convert '#rrggbb' string to (r,g,b) tuple."""
    h = h.lstrip('#')
    return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16))

def cc(r,g,b):
    return (max(0,min(255,int(r))), max(0,min(255,int(g))), max(0,min(255,int(b))))

def blend(c1, c2, t):
    """Linear-interpolate between two (r,g,b) colours. t=0→c1, t=1→c2."""
    t = max(0.0, min(1.0, t))
    return cc(c1[0]+(c2[0]-c1[0])*t, c1[1]+(c2[1]-c1[1])*t, c1[2]+(c2[2]-c1[2])*t)

def darken(c, amount):
    return cc(c[0]-amount, c[1]-amount, c[2]-amount)

def lighten(c, amount):
    return cc(c[0]+amount, c[1]+amount, c[2]+amount)

# ── Base palette (all hex) ────────────────────────────────────────────────────
COLORS = {
    EMPTY:      hx('#0c0c10'),
    AIR:        hx('#141620'),
    SAND:       hx('#d4a96a'),
    WATER:      hx('#1e6fcc'),
    WOOD:       hx('#5c3318'),
    FIRE:       hx('#e8520a'),
    STONE:      hx('#6e6e72'),
    LAVA:       hx('#cc3a06'),
    SMOKE:      hx('#484852'),
    STEAM:      hx('#c8cdd8'),
    ACID:       hx('#5ef01a'),
    PLANT:      hx('#1e8c1e'),
    CLOUD:      hx('#d0d4e8'),
    DIRT:       hx('#4a2e0e'),
    SAPLING:    hx('#62b840'),
    LEAF:       hx('#157020'),
    OIL:        hx('#1a1408'),
    ICE:        hx('#a8d8f8'),
    ANIMAL:     hx('#c09070'),
    SNOW:       hx('#eef2ff'),
    GUNPOWDER:  hx('#363638'),
    GLASS:      hx('#b4d8e8'),
    MUD:        hx('#5a3c1c'),
    VINE:       hx('#0e6414'),
    EMBER:      hx('#ff8c0a'),
    SALT:       hx('#f8f8f8'),
    FUNGUS:     hx('#a060c0'),
    LIGHTNING:  hx('#fffff0'),
    OBSIDIAN:   hx('#180e24'),
    CRYSTAL:    hx('#80d8ff'),
    CHARCOAL:   hx('#1e1818'),
    RUST:       hx('#7a3208'),
    WETDIRT:    hx('#2e1c08'),
    ASH:        hx('#888078'),
    PRESSGAS:   hx('#90d890'),
    MAGMA:      hx('#b81800'),
    SLIME:      hx('#40b840'),
    TAR:        hx('#0c0800'),
    CONCRETE:   hx('#8c8880'),
    CEMENT:     hx('#b0a898'),
    GOLD:       hx('#ffc000'),
    GRAVEL:     hx('#706860'),
    MOSS:       hx('#286828'),
    HONEY:      hx('#cc8800'),
    WAX:        hx('#fff0c0'),
    POISON:     hx('#50d020'),
    SEED:       hx('#a07840'),
    RUBBER:     hx('#181818'),
    WIRE:       hx('#a84808'),
    CHARGED:    hx('#ffe020'),
    BUBBLE:     hx('#a8d8ff'),
    SPORE:      hx('#c8a8d8'),
    MERCURY:    hx('#b0c0d0'),
    NEON:       hx('#d040ff'),
    PLASMA:     hx('#b060ff'),
    CLAY:       hx('#9c6040'),
    CERAMIC:    hx('#d0c0a0'),
    RESIN:      hx('#c09020'),
    BASALT:     hx('#302830'),
    PEAT:       hx('#402810'),
    SEAWEED:    hx('#106030'),
    JELLYFISH:  hx('#d8c0f0'),
    CORAL:      hx('#e05040'),
    SANDSTONE:  hx('#c8a868'),
    METHANE:    hx('#b0e8b0'),
    NITRO:      hx('#e8e060'),
    QUICKSAND:  hx('#c88848'),
    STEEL:      hx('#7090b0'),
    SUGAR:      hx('#f4eee4'),
    URANIUM:    hx('#40d830'),
    VOID:       hx('#100018'),
    # ── Animal sub-types ───────────────────────────────────────────────────────
    BIRD:       hx('#f0d880'),
    FISH:       hx('#4090d0'),
    PREDATOR:   hx('#a04828'),
    HUMAN:      hx('#f0c090'),
    TIGER:      hx('#d87820'),
    LION:       hx('#c8a040'),
    WHALE:      hx('#304878'),
    DOLPHIN:    hx('#5090c0'),
    # ── Food items ─────────────────────────────────────────────────────────────
    WHEAT:      hx('#e8c840'),
    APPLE:      hx('#d83020'),
    BERRY:      hx('#8830c0'),
    BREAD:      hx('#c88840'),
    MEAT:       hx('#a02818'),
    # ── Real element replacements ──────────────────────────────────────────────
    HYDROGEN:   hx('#d8f4ff'),
    SULFUR:     hx('#d4c820'),
    HELIUM:     hx('#f0f8e8'),
    COAL:       hx('#1c1818'),
    COPPER:     hx('#b86020'),
    BEAR:       hx('#604020'),
    SNAKE:      hx('#30cc30'),
    RABBIT:     hx('#e0e0e0'),
    SPIDER:     hx('#1a1a1a'),
    BEE:        hx('#ffcc00'),
    FROG:       hx('#40a040'),
    WEB:        hx('#ffffff'),
    MUSHROOM:   hx('#c89060'),
    CORN:       hx('#f0d040'),
    CARROT:     hx('#f07820'),
    COOKED_MEAT:hx('#803010'),
    DOUGH:      hx('#f0e0c0'),
    FORGE:      hx('#5a2800'),   # dark stone-brick with ember glow
    ANVIL:      hx('#4a5a70'),   # cool steel-blue metallic
    BOOK:       hx('#c8a060'),   # parchment tan
}

NAMES = {
    EMPTY:"Eraser",SAND:"Sand",WATER:"Water",WOOD:"Wood",
    FIRE:"Fire",STONE:"Stone",LAVA:"Lava",ACID:"Acid",
    PLANT:"Grass",CLOUD:"Cloud",DIRT:"Dirt",SAPLING:"Sapling",
    OIL:"Oil",ICE:"Ice",LEAF:"Leaf",ANIMAL:"Animal",
    SNOW:"Snow",GUNPOWDER:"Gunpowder",GLASS:"Glass",MUD:"Mud",
    VINE:"Vine",EMBER:"Ember",SALT:"Salt",FUNGUS:"Fungus",
    LIGHTNING:"Lightning",OBSIDIAN:"Obsidian",CRYSTAL:"Crystal",
    CHARCOAL:"Charcoal",RUST:"Rust",WETDIRT:"WetDirt",
    ASH:"Ash",PRESSGAS:"PressGas",MAGMA:"Magma",
    SLIME:"Slime",TAR:"Tar",CONCRETE:"Concrete",CEMENT:"Cement",
    GOLD:"Gold",GRAVEL:"Gravel",MOSS:"Moss",HONEY:"Honey",
    WAX:"Wax",POISON:"Poison",SEED:"Seed",RUBBER:"Rubber",
    WIRE:"Wire",CHARGED:"Charged",BUBBLE:"Bubble",SPORE:"Spore",
    MERCURY:"Mercury",NEON:"Neon",PLASMA:"Plasma",
    CLAY:"Clay",CERAMIC:"Ceramic",RESIN:"Resin",BASALT:"Basalt",
    PEAT:"Peat",SEAWEED:"Seaweed",JELLYFISH:"Jellyfish",
    CORAL:"Coral",SANDSTONE:"Sandstone",AIR:"Air",
    SMOKE:"Smoke",STEAM:"Steam",
    METHANE:"Methane",NITRO:"Nitro",QUICKSAND:"Quicksand",
    STEEL:"Steel",SUGAR:"Sugar",URANIUM:"Uranium",VOID:"Void",
    BIRD:"Bird",FISH:"Fish",PREDATOR:"Wolf",HUMAN:"Human",
    TIGER:"Tiger",LION:"Lion",WHALE:"Whale",DOLPHIN:"Dolphin",
    WHEAT:"Wheat",APPLE:"Apple",BERRY:"Berry",BREAD:"Bread",MEAT:"Meat",
    HYDROGEN:"Hydrogen",SULFUR:"Sulfur",HELIUM:"Helium",
    COAL:"Coal",COPPER:"Copper",
    BEAR:"Bear", SNAKE:"Snake", RABBIT:"Rabbit", SPIDER:"Spider",
    BEE:"Bee", FROG:"Frog", WEB:"Web",
    MUSHROOM:"Mushroom", CORN:"Corn", CARROT:"Carrot",
    COOKED_MEAT:"CookedMeat", DOUGH:"Dough",
    FORGE:"Forge",
    ANVIL:"Anvil",
    BOOK:"Book",
}

ANIMAL_TYPES = {ANIMAL, BIRD, FISH, PREDATOR, HUMAN, TIGER, LION, WHALE, DOLPHIN,
                BEAR, SNAKE, RABBIT, SPIDER, BEE, FROG}

ELEMENT_LIST = [
    # Eraser
    EMPTY,
    # Powders / grains
    SAND, DIRT, GRAVEL, SALT, GUNPOWDER, SUGAR, SULFUR, COAL,
    # Liquids
    WATER, LAVA, ACID, OIL, HONEY, SLIME, TAR, MERCURY, MUD, WETDIRT, NITRO,
    # Gases
    STEAM, SMOKE, METHANE, HYDROGEN, AIR, CLOUD,
    # Solids / terrain
    STONE, WOOD, GLASS, CONCRETE, CEMENT, OBSIDIAN, BASALT, SANDSTONE,
    CLAY, CERAMIC, CHARCOAL, PEAT, RUST,
    # Crafting structures
    FORGE, ANVIL, BOOK,
    # Valuables
    GOLD, COPPER, STEEL, CRYSTAL, WIRE, RUBBER, WAX, RESIN,
    # Biology / food
    PLANT, LEAF, VINE, MOSS, SEED, SAPLING, FUNGUS, SEAWEED,
    MUSHROOM, CORN, CARROT, COOKED_MEAT, DOUGH,
    WHEAT, APPLE, BERRY, BREAD, MEAT,
    # Animals
    ANIMAL, BIRD, FISH, PREDATOR, HUMAN, TIGER, LION, WHALE, DOLPHIN,
    BEAR, SNAKE, RABBIT, SPIDER, BEE, FROG, WEB,
    # Natural reactive / special
    FIRE, ICE, SNOW, EMBER, MAGMA, URANIUM, QUICKSAND,
    JELLYFISH, CORAL, POISON, LIGHTNING,
]

# ── Physics tables ────────────────────────────────────────────────────────────
DENSITY = {
    EMPTY:0, LIGHTNING:0, CHARGED:0,
    AIR:1.2, NEON:0.9, PLASMA:0.01,
    SMOKE:0.6, STEAM:0.6, PRESSGAS:1.2, POISON:1.5,
    CLOUD:0.5, EMBER:50, FIRE:0.3, BUBBLE:0.1,
    ASH:570, SNOW:100, LEAF:200, SPORE:30,
    OIL:800, RESIN:1050, HONEY:1420, SLIME:1200,
    WATER:1000, ACID:1200, MERCURY:13534,
    VINE:400, SEAWEED:1030, FUNGUS:300, PLANT:400,
    SAPLING:600, SEED:850, JELLYFISH:1050, ANIMAL:985,
    ICE:917, RUBBER:920, CLAY:1800,
    WETDIRT:1600, MUD:1500, SAND:1600, DIRT:1400, SALT:2165,
    GRAVEL:1680, PEAT:400, GUNPOWDER:1700,
    CHARCOAL:400, SANDSTONE:2300, RUST:5240, CRYSTAL:2650,
    GLASS:2500, CORAL:2700,
    TAR:1070, WAX:900, WOOD:700, STONE:2600, MOSS:400,
    WIRE:7850, CONCRETE:2400, CEMENT:3150, CERAMIC:2300,
    LAVA:2700, MAGMA:2800, GOLD:19300, BASALT:3000, OBSIDIAN:2350,
    METHANE:0.7, NITRO:1600, QUICKSAND:1550, STEEL:7800,
    SUGAR:1580, URANIUM:19050, VOID:0,
    BIRD:0.9, FISH:1010, PREDATOR:980, HUMAN:970,
    TIGER:1000, LION:1005, WHALE:1015, DOLPHIN:1008,
    WHEAT:500, APPLE:600, BERRY:400, BREAD:700, MEAT:950,
    HYDROGEN:0.09, SULFUR:2070, HELIUM:0.18, COAL:1400, COPPER:8960,
    BEAR:1200, SNAKE:900, RABBIT:600, SPIDER:200, BEE:10, FROG:800, WEB:50,
    BOOK:350,
}

FLAMMABLE = {
    OIL:0.85, GUNPOWDER:0.99, WOOD:0.15, CHARCOAL:0.25,
    LEAF:0.45, PLANT:0.35, VINE:0.30, SAPLING:0.35,
    ANIMAL:0.08, FUNGUS:0.20, TAR:0.90,
    SLIME:0.05, WAX:0.35, HONEY:0.10, RUBBER:0.40,
    MOSS:0.35, SEED:0.30, PEAT:0.60, RESIN:0.75, SEAWEED:0.15,
    METHANE:0.95, SUGAR:0.55, NITRO:0.99,
    HYDROGEN:0.97, SULFUR:0.30, COAL:0.18, BIRD:0.05, HUMAN:0.04,
    TIGER:0.06, LION:0.06,
    WHEAT:0.55, BREAD:0.12, MEAT:0.15,
}

CONDUCT = {
    WATER:0.6, ICE:2.2, STONE:3.0, SAND:0.25, WOOD:0.15,
    CHARCOAL:0.08, LAVA:1.5, MAGMA:2.0, GLASS:1.0, DIRT:0.25,
    MUD:0.5, WETDIRT:0.8, GOLD:310.0, MERCURY:8.3,
    CONCRETE:1.7, TAR:0.17, RUBBER:0.13, WAX:0.25,
    CLAY:0.25, CERAMIC:1.5, BASALT:2.0, SANDSTONE:2.3,
    WIRE:80.0, OBSIDIAN:1.2, CRYSTAL:2.5,
    AIR:0.024, EMPTY:0.024,
    SMOKE:0.026, STEAM:0.016, NEON:0.049, PLASMA:0.1,
    HYDROGEN:0.18, HELIUM:0.15, SULFUR:0.27, COAL:0.26, COPPER:380.0,
    BIRD:0.024, FISH:0.58, PREDATOR:0.2, HUMAN:0.2,
    TIGER:0.21, LION:0.21, WHALE:0.6, DOLPHIN:0.6,
}

HAZARDS = {FIRE, LAVA, ACID, MAGMA, NITRO}   # elements that damage/kill animals

LIQUIDS      = {WATER, ACID, LAVA, OIL, HONEY, SLIME, TAR, MERCURY, POISON, MAGMA, MUD, WETDIRT, NITRO}
STATIC_SOLIDS= {STONE, WOOD, GLASS, CONCRETE, CEMENT, OBSIDIAN, BASALT, CERAMIC, SANDSTONE, STEEL, COPPER, WEB, FORGE, ANVIL}
GROUND_SOLIDS= {STONE, DIRT, SAND, GRAVEL, WETDIRT, MUD, WOOD, CONCRETE, CEMENT, BASALT,
                SANDSTONE, OBSIDIAN, COAL, COPPER, STEEL, CERAMIC, CHARCOAL, PEAT, RUST,
                CRYSTAL, GLASS, WAX, RUBBER, RESIN, GOLD, WIRE, CLAY, SALT, GUNPOWDER,
                SUGAR, SULFUR, QUICKSAND, ICE, CORAL, FORGE, ANVIL}

# ── Biome weather probabilities (imported by sandbox.py) ─────────────────────
_BIOME_WEATHER = {
    'desert':       {'heatwave': 0.04, 'sandstorm': 0.03, 'tornado': 0.01},
    'plains':       {'rain': 0.05, 'storm': 0.03, 'fog': 0.02, 'tornado': 0.005},
    'forest':       {'rain': 0.06, 'fog': 0.04, 'storm': 0.02},
    'ocean':        {'rain': 0.07, 'storm': 0.04, 'fog': 0.03},
    'mountains':    {'snow': 0.06, 'blizzard': 0.03, 'storm': 0.02},
    'swamp':        {'fog': 0.07, 'rain': 0.05, 'acid_rain': 0.01},
    'civilization': {'rain': 0.04, 'storm': 0.02, 'fog': 0.015},
    None:           {},
}
