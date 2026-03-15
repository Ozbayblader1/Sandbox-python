"""
Elemental Sandbox v4.3 – Enhanced Graphics & Realistic Physics
Run: python sandbox.py
Controls:
  Left-click = draw | Right-click = erase | Scroll = brush size
  R=Rain  S=Snow  T=Storm  N=Tornado  B=Blizzard  F=Fog  H=Heatwave
  A=AcidRain  W=Clear Weather  C=Clear Grid  P=Pause  ESC=Menu
"""
import pygame, random, math, sys
import numpy as np
from typing import Any, Optional, Dict, List

WIDTH, HEIGHT = 960, 720
CELL = 4
WORLD_MULT = 1
COLS = (WIDTH * WORLD_MULT)  // CELL
ROWS = (HEIGHT * WORLD_MULT) // CELL
FPS  = 60

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
) = range(101)

# Animal-type set for sidebar filtering
ANIMAL_TYPES = None   # filled after all IDs defined (below)

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
    BEAR:1200, SNAKE:900, RABBIT:600, SPIDER:200, BEE:10, FROG:800, WEB:50
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
STATIC_SOLIDS= {STONE, WOOD, GLASS, CONCRETE, CEMENT, OBSIDIAN, BASALT, CERAMIC, SANDSTONE, STEEL, COPPER, WEB}
GROUND_SOLIDS= {STONE, DIRT, SAND, GRAVEL, WETDIRT, MUD, WOOD, CONCRETE, CEMENT, BASALT,
                SANDSTONE, OBSIDIAN, COAL, COPPER, STEEL, CERAMIC, CHARCOAL, PEAT, RUST,
                CRYSTAL, GLASS, WAX, RUBBER, RESIN, GOLD, WIRE, CLAY, SALT, GUNPOWDER,
                SUGAR, SULFUR, QUICKSAND, ICE, CORAL}

# ── Pygame init ───────────────────────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Elemental Sandbox v4.3")
clock  = pygame.time.Clock()

# Pixel-level surface for rendering (draw each cell as raw pixels)
pixel_surf  = pygame.Surface((COLS, ROWS), 0, 24)
_scale_surf = pygame.Surface((WIDTH, HEIGHT), 0, 24)   # same format, screen-sized

try:
    font  = pygame.font.SysFont("consolas", 13, bold=True)
    tfont = pygame.font.SysFont("consolas", 40, bold=True)
    sfont = pygame.font.SysFont("consolas", 15)
except:
    font  = pygame.font.SysFont("monospace", 13, bold=True)
    tfont = pygame.font.SysFont("monospace", 40, bold=True)
    sfont = pygame.font.SysFont("monospace", 15)

# ── Grids ─────────────────────────────────────────────────────────────────────
grid: List[List[int]]       = [[EMPTY]*ROWS for _ in range(COLS)]
updated: List[List[bool]]   = [[False]*ROWS for _ in range(COLS)]
life: List[List[int]]       = [[0]*ROWS     for _ in range(COLS)]
data: List[List[int]]       = [[0]*ROWS     for _ in range(COLS)]
gene: List[List[Optional[Dict[str, Any]]]] = [[None]*ROWS  for _ in range(COLS)]
temp_g: List[List[float]]   = [[20.0]*ROWS  for _ in range(COLS)]
oxy: List[List[float]]      = [[1.0]*ROWS   for _ in range(COLS)]
pressure: List[List[float]] = [[0.0]*ROWS   for _ in range(COLS)]

# Add floor
for _x in range(COLS):
    for _y in range(ROWS - 5, ROWS):
        grid[_x][_y] = STONE

# Per-cell "noise seed" for stable visual variation
noise_seed = [[(x*2654435761 ^ y*1013904223) & 0xFFFF for y in range(ROWS)] for x in range(COLS)]

# ── Numpy rendering setup ──────────────────────────────────────────────────────
_MAX_EL   = max(COLORS.keys()) + 1 if COLORS else 126
_clr_lut  = np.zeros((_MAX_EL, 3), dtype=np.int16)
for _eid, _col in COLORS.items():
    if 0 <= _eid < _MAX_EL:
        _clr_lut[_eid] = _col
_ns        = np.array(noise_seed, dtype=np.int32)
_noise_r   = (_ns % 29 - 14).astype(np.int16)
_noise_g   = ((_ns >> 1) % 17 - 8).astype(np.int16)
_noise_b   = ((_ns >> 2) % 13 - 6).astype(np.int16)
_render_buf= np.zeros((COLS, ROWS, 3), dtype=np.uint8)
_X_ARR     = np.tile(np.arange(COLS, dtype=np.float32)[:,None], (1, ROWS))
_Y_ARR     = np.tile(np.arange(ROWS, dtype=np.float32)[None,:], (COLS, 1))

# ── Weather / environment ─────────────────────────────────────────────────────
cur_el      = SAND
brush       = 5
wind_x      = 0.0
raining: bool     = False
snowing: bool     = False
storming: bool    = False
storm_t: int      = 0
ltng_t: int       = 0
tornado_on: bool  = False
tornado_x: int    = COLS//2
tornado_str: int  = 0
tornado_life: int = 0
temperature: float = 20.0
blizzard: bool    = False
blizzard_t: int   = 0
fog_on: bool      = False
fog_t: int        = 0
heatwave: bool    = False
heatwave_t: int   = 0
acid_rain: bool   = False
acidrain_t: int   = 0
global_hum: float = 0.3
day_timer: int    = 0
DAY_LEN: int      = 21600   # 6 min full cycle at 60fps (3 min day, 3 min night)
is_day: bool      = True
sun_ang: float    = 0.0
paused: bool      = False
frame_t: int      = 0   # global tick counter for animations
zoom_level: float = 1.0
cam_offset_x: float = -(WIDTH * WORLD_MULT - WIDTH) / 2.0
cam_offset_y: float = -(HEIGHT * WORLD_MULT - HEIGHT) / 2.0

# ── Sidebar ────────────────────────────────────────────────────────────────────
SIDEBAR_W         = 240
sidebar_open         = False
sidebar_scroll       = 0
sidebar_search       = ""
sidebar_search_active= False
sidebar_animal_mode  = False   # when True: show only animal sub-types
_placed_animal       = False   # one-at-a-time spawn gate for animals

# ── Genetics ──────────────────────────────────────────────────────────────────
def make_genes(p1=None, p2=None):
    base = {
        'speed':0.25+random.uniform(-0.1,0.1),
        'color_r':180,'color_g':140,'color_b':120,
        'lifespan':random.randint(400,800),
        'herbivore':True,'carnivore':False,
        'amphibious':False,'flying':False,
        'generation':0,
        'heat_resist':random.uniform(0,0.25),
        'cold_resist':random.uniform(0,0.25),
        'poison_resist':random.uniform(0,0.15),
        'metabolism':random.uniform(0.8,1.2),
    }
    if p1 and p2:
        for k in ('speed','lifespan','heat_resist','cold_resist','poison_resist','metabolism'):
            val = (p1.get(k, base[k]) + p2.get(k, base[k])) / 2
            if random.random() < 0.15: val *= random.uniform(0.85, 1.15)
            base[k] = val
        for k in ('herbivore','carnivore','amphibious','flying'):
            base[k]=p1.get(k,False) if random.random()>0.5 else p2.get(k,False)
            if random.random()<0.05: base[k]=not base[k]
        for c in ('color_r','color_g','color_b'):
            base[c]=int((p1.get(c,150)+p2.get(c,150))/2)
            if random.random()<0.2: base[c]=max(50,min(255,base[c]+random.randint(-20,20)))
        base['generation']=int(max(p1.get('generation',0),p2.get('generation',0)))+1
        base['speed']=max(0.1,min(0.8,float(base.get('speed', 0.25))))
        base['lifespan']=int(max(200,min(1200,float(base.get('lifespan', 400)))))
        base['metabolism']=max(0.5,min(2.0,float(base.get('metabolism', 1.0))))
    return base

# ── UI ────────────────────────────────────────────────────────────────────────
class Button:
    def __init__(self,x,y,w,h,lbl,col,hcol,fn):
        self.r=pygame.Rect(x,y,w,h); self.lbl=lbl
        self.col=hx(col); self.hcol=hx(hcol); self.fn=fn; self.hov=False
    def draw(self,s):
        c=self.hcol if self.hov else self.col
        pygame.draw.rect(s,c,self.r,border_radius=5)
        pygame.draw.rect(s,hx('#646478'),self.r,width=1,border_radius=5)
        # Highlight strip on top
        hr=pygame.Rect(self.r.x+2,self.r.y+1,self.r.w-4,3)
        hi=pygame.Surface((hr.w,hr.h),pygame.SRCALPHA)
        hi.fill((255,255,255,40))
        s.blit(hi,(hr.x,hr.y))
        ts=font.render(self.lbl,True,hx('#f0f0f8'))
        s.blit(ts,ts.get_rect(center=self.r.center))
    def check(self,pos): self.hov=self.r.collidepoint(pos)
    def event(self,ev):
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and self.hov:
            self.fn(); return True
        return False

class Slider:
    def __init__(self,x,y,w,items):
        self.r=pygame.Rect(x,y,w,22); self.items=items
        self.idx=1; self.drag=False; self.kr=11
    def draw(self,s):
        pygame.draw.rect(s,hx('#1e1e2e'),self.r,border_radius=8)
        pygame.draw.rect(s,hx('#505068'),self.r,width=2,border_radius=8)
        sw=self.r.w/max(1,len(self.items)-1)
        kx=int(self.r.x+self.idx*sw); ky=self.r.centery
        pygame.draw.line(s,hx('#383858'),(self.r.left+self.kr,ky),(self.r.right-self.kr,ky),3)
        el=self.items[self.idx]
        kc=COLORS.get(el,hx('#a0a0a0'))
        # Knob with glow
        pygame.draw.circle(s,darken(kc,20),(kx,ky),self.kr+2)
        pygame.draw.circle(s,kc,(kx,ky),self.kr)
        pygame.draw.circle(s,lighten(kc,60),(kx-3,ky-3),self.kr//3)
        nm=NAMES.get(el,'?')
        ts=font.render(nm,True,hx('#e0e0f0'))
        s.blit(ts,(self.r.right+10,self.r.y+3))
    def event(self,ev):
        global cur_el
        if ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1 and self.r.collidepoint(ev.pos):
            self.drag=True; self._upd(ev.pos[0]); return True
        if ev.type==pygame.MOUSEBUTTONUP and ev.button==1: self.drag=False
        if ev.type==pygame.MOUSEMOTION and self.drag:
            self._upd(ev.pos[0]); return True
        return False
    def _upd(self,mx):
        global cur_el
        rel=max(0,min(self.r.w,mx-self.r.x))
        sw=self.r.w/max(1,len(self.items)-1)
        self.idx=max(0,min(len(self.items)-1,int(round(rel/sw))))
        cur_el=self.items[self.idx]

# ── Weather helpers ───────────────────────────────────────────────────────────
def clear_grid():
    global grid,life,data,gene,temp_g,oxy,pressure
    for x in range(COLS):
        for y in range(ROWS):
            if y >= ROWS - 5:
                grid[x][y]=STONE
            else:
                grid[x][y]=EMPTY
            life[x][y]=0; data[x][y]=0; gene[x][y]=None
            temp_g[x][y]=temperature; oxy[x][y]=1.0; pressure[x][y]=0.0

def clear_weather():
    global raining,snowing,storming,storm_t,blizzard,blizzard_t
    global tornado_on,tornado_life,wind_x,fog_on,fog_t,heatwave,heatwave_t,acid_rain,acidrain_t
    raining=snowing=storming=blizzard=fog_on=heatwave=tornado_on=acid_rain=False
    storm_t=blizzard_t=fog_t=heatwave_t=tornado_life=acidrain_t=0; wind_x=0.0

def toggle_rain():
    global raining,snowing
    raining=not raining
    if raining: snowing=False

def toggle_snow():
    global snowing,raining
    snowing=not snowing
    if snowing: raining=False

def trigger_storm():
    global storming,storm_t,raining
    storming=True; storm_t=random.randint(400,750); raining=True

def trigger_tornado():
    global tornado_on,tornado_x,tornado_str,tornado_life
    tornado_on=True; tornado_x=random.randint(COLS//4,3*COLS//4)
    tornado_str=random.randint(4,9); tornado_life=random.randint(300,700)

def trigger_blizzard():
    global blizzard,blizzard_t,snowing,raining,wind_x
    blizzard=True; blizzard_t=random.randint(500,950)
    snowing=True; raining=False; wind_x=6.0 if random.random()>0.5 else -6.0

def trigger_fog():
    global fog_on,fog_t
    fog_on=True; fog_t=random.randint(500,1000)

def trigger_heatwave():
    global heatwave,heatwave_t
    heatwave=True; heatwave_t=random.randint(400,800)

def trigger_acid_rain():
    global acid_rain,acidrain_t,raining
    acid_rain=True; acidrain_t=random.randint(300,600); raining=False

def raise_temp():
    global temperature
    temperature=min(120,temperature+5)

def lower_temp():
    global temperature
    temperature=max(-40,temperature-5)

_ZOOM_STEPS = [0.15, 0.20, 0.25, 0.33, 0.40, 0.50, 0.65, 0.80, 1.0,
               1.25, 1.5, 2.0, 2.5, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0]

def _world_w(): return COLS * CELL * zoom_level
def _world_h(): return ROWS * CELL * zoom_level

def _clamp_camera():
    """Keep camera so that world always fills the screen (no black bars)."""
    global cam_offset_x, cam_offset_y
    ww = _world_w(); wh = _world_h()
    # If world is wider than screen, clamp so edges don't show outside
    if ww >= WIDTH:
        cam_offset_x = int(max(WIDTH - ww, min(0, cam_offset_x)))
    else:
        cam_offset_x = int((WIDTH - ww) / 2)
    if wh >= HEIGHT:
        cam_offset_y = int(max(HEIGHT - wh, min(0, cam_offset_y)))
    else:
        cam_offset_y = int((HEIGHT - wh) / 2)

def _min_zoom():
    """Minimum zoom that fits world entirely on screen (no black bars)."""
    return max(WIDTH / (COLS * CELL), HEIGHT / (ROWS * CELL))

def _zoom_toward(new_z, px, py):
    """Zoom so that world point under screen pixel (px, py) stays fixed."""
    global zoom_level, cam_offset_x, cam_offset_y
    old_z = zoom_level
    zoom_level = max(new_z, _min_zoom())   # never smaller than world fits screen
    cam_offset_x = int(px - (px - cam_offset_x) * (zoom_level / old_z))
    cam_offset_y = int(py - (py - cam_offset_y) * (zoom_level / old_z))
    _clamp_camera()

def zoom_in(px=None, py=None):
    if px is None: px = WIDTH//2
    if py is None: py = HEIGHT//2
    idx = next((i for i,z in enumerate(_ZOOM_STEPS) if z > zoom_level), len(_ZOOM_STEPS)-1)
    _zoom_toward(_ZOOM_STEPS[min(idx, len(_ZOOM_STEPS)-1)], px, py)

def zoom_out(px=None, py=None):
    if px is None: px = WIDTH//2
    if py is None: py = HEIGHT//2
    idx = next((i for i,z in enumerate(reversed(_ZOOM_STEPS)) if z < zoom_level), len(_ZOOM_STEPS)-1)
    _zoom_toward(_ZOOM_STEPS[max(0, len(_ZOOM_STEPS)-1-idx)], px, py)

def pan_left():
    global cam_offset_x
    cam_offset_x += 40; _clamp_camera()

def pan_right():
    global cam_offset_x
    cam_offset_x -= 40; _clamp_camera()

def pan_up():
    global cam_offset_y
    cam_offset_y += 40; _clamp_camera()

def pan_down():
    global cam_offset_y
    cam_offset_y -= 40; _clamp_camera()

def wind_left():
    global wind_x
    wind_x=max(-10.0,wind_x-1.0)

def wind_right():
    global wind_x
    wind_x=min(10.0,wind_x+1.0)

def calm_wind():
    global wind_x
    wind_x=0.0

def toggle_pause():
    global paused
    paused=not paused

def toggle_sidebar():
    global sidebar_open, sidebar_scroll, sidebar_search, sidebar_search_active
    sidebar_open = not sidebar_open
    if sidebar_open:
        sidebar_scroll = 0
        sidebar_search_active = True
    else:
        sidebar_search_active = False

# UI
R1,R2,R3=114,140,168
buttons=[
    Button(10,R1,50,22,"Clear",'#a02020','#d04040',clear_grid),
    Button(65,R1,48,22,"Rain",'#1e4eb0','#3878e0',toggle_rain),
    Button(118,R1,48,22,"Snow",'#4898b8','#78c8e8',toggle_snow),
    Button(171,R1,52,22,"Storm",'#503090','#7850c0',trigger_storm),
    Button(228,R1,62,22,"Tornado",'#706020','#a08830',trigger_tornado),
    Button(295,R1,62,22,"Blizzard",'#204880','#3878c0',trigger_blizzard),
    Button(362,R1,60,22,"AcidRain",'#207820','#38a838',trigger_acid_rain),
    Button(10,R2,40,22,"Fog",'#406080','#608898',trigger_fog),
    Button(55,R2,78,22,"Heatwave",'#a03008','#d05010',trigger_heatwave),
    Button(138,R2,87,22,"ClrWeather",'#206040','#38a060',clear_weather),
    Button(230,R2,36,22,"< W",'#303040','#505068',wind_left),
    Button(271,R2,36,22,"W >",'#303040','#505068',wind_right),
    Button(312,R2,44,22,"Calm",'#303040','#505068',calm_wind),
    Button(361,R2,36,22,"T+",'#a03010','#d05020',raise_temp),
    Button(402,R2,36,22,"T-",'#103080','#2050b0',lower_temp),
    Button(443,R2,48,22,"Pause",'#404040','#686880',toggle_pause),
    Button(10,R3,100,22,"Elements",'#183860','#2858a0',toggle_sidebar),
    Button(120,R3,40,22,"Z+",'#408040','#50a050',zoom_in),
    Button(165,R3,40,22,"Z-",'#804040','#a05050',zoom_out),
]

# ── Bounds / swap ─────────────────────────────────────────────────────────────
def inb(x,y): return 0<=x<COLS and 0<=y<ROWS

def swap(x1,y1,x2,y2):
    if not(inb(x1,y1) and inb(x2,y2)): return False
    grid[x1][y1],grid[x2][y2]=grid[x2][y2],grid[x1][y1]
    life[x1][y1],life[x2][y2]=life[x2][y2],life[x1][y1]
    data[x1][y1],data[x2][y2]=data[x2][y2],data[x1][y1]
    gene[x1][y1],gene[x2][y2]=gene[x2][y2],gene[x1][y1]
    temp_g[x1][y1],temp_g[x2][y2]=temp_g[x2][y2],temp_g[x1][y1]
    updated[x1][y1]=updated[x2][y2]=True
    return True

def can_powder_fall(el):
    if el in (EMPTY,AIR): return True
    if el in LIQUIDS: return random.random()<0.85
    return False

# ── Physics helpers ───────────────────────────────────────────────────────────
def explode(cx,cy,radius,heat=1000):
    for r in range(radius+1):
        for angle in range(0,360,max(1,30-r*3)):
            rad=math.radians(angle)
            x=int(cx+r*math.cos(rad)); y=int(cy+r*math.sin(rad))
            if not inb(x,y): continue
            dist=math.sqrt((x-cx)**2+(y-cy)**2)
            if dist>radius: continue
            intensity=1.0-(dist/radius)
            if grid[x][y] not in (STONE,OBSIDIAN,CONCRETE,GOLD):
                if intensity>0.7:
                    grid[x][y]=FIRE; life[x][y]=random.randint(100,220); temp_g[x][y]=heat*intensity
                elif intensity>0.4 and grid[x][y] not in (EMPTY,AIR,FIRE):
                    if random.random()<intensity:
                        grid[x][y]=EMBER if random.random()<0.3 else SMOKE
                        life[x][y]=random.randint(50,150)

def spawn_lightning(lx: int):
    for ly in range(ROWS):
        if not inb(lx,ly): continue
        if ly>0 and random.random()<0.15:
            lx+=random.choice([-1,0,1]); lx=max(0,min(COLS-1,lx))
        tgt=grid[lx][ly]
        if tgt in (STONE,WOOD,SAND,DIRT,WATER,ANIMAL,PLANT,WIRE,MERCURY,GOLD):
            if tgt==WIRE:
                grid[lx][ly]=CHARGED; life[lx][ly]=50; conduct_charge(lx,ly)
            elif tgt==MERCURY:
                grid[lx][ly]=PLASMA; life[lx][ly]=random.randint(60,120); explode(lx,ly,4,1500)
            elif tgt==WATER:
                for dx in range(-3,4):
                    for dy in range(-3,4):
                        ex,ey=lx+dx,ly+dy
                        if inb(ex,ey) and grid[ex][ey]==WATER:
                            grid[ex][ey]=STEAM; life[ex][ey]=random.randint(40,80)
            else:
                explode(lx,ly,3,1200)
            for fy in range(0,ly,2):
                if inb(lx,fy) and grid[lx][fy] in (EMPTY,AIR):
                    grid[lx][fy]=LIGHTNING; life[lx][fy]=3
            break

def conduct_charge(x,y,visited=None,depth=0):
    if depth>20: return
    if visited is None: visited=set()
    if (x,y) in visited: return
    visited.add((x,y))
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and (nx,ny) not in visited and grid[nx][ny]==WIRE:
            grid[nx][ny]=CHARGED; life[nx][ny]=max(10,35-depth)
            updated[nx][ny]=True; conduct_charge(nx,ny,visited,depth+1)

def update_tornado():
    global tornado_on,tornado_x,tornado_life,wind_x
    if not tornado_on: return
    tornado_life-=1
    if tornado_life<=0: tornado_on=False; wind_x=0.0; return
    tornado_x+=random.randint(-2,2); tornado_x=max(15,min(COLS-15,tornado_x))
    wind_x=(tornado_str/2.0)*(1 if tornado_x<COLS//2 else -1)
    for dy in range(min(60,ROWS)):
        radius=int(min(dy//2+3,tornado_str*2))
        for dx in range(-radius,radius+1):
            tx,ty=tornado_x+dx,ROWS-1-dy
            if not inb(tx,ty): continue
            el=grid[tx][ty]
            if el in (EMPTY,AIR,STONE,OBSIDIAN,CONCRETE): continue
            dist=abs(dx)
            if dist<radius and random.random()<(1.0-dist/radius)*tornado_str*0.3:
                ny2=ty-random.randint(1,max(1,tornado_str//2))
                nx2=tx+random.randint(-tornado_str//3,tornado_str//3)
                if inb(nx2,ny2) and grid[nx2][ny2] in (EMPTY,AIR):
                    swap(tx,ty,nx2,ny2)

def diffuse_heat():
    for _ in range(600):
        x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
        el=grid[x][y]
        cond=CONDUCT.get(el,0.05)/100.0
        neighbors=[temp_g[x+dx][y+dy] for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)] if inb(x+dx,y+dy)]
        if neighbors:
            avg=sum(neighbors)/len(neighbors)
            temp_g[x][y]=max(-60.0,min(3000.0,temp_g[x][y]+(avg-temp_g[x][y])*cond*0.25))
    for _ in range(200):
        x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
        temp_g[x][y]+=(temperature-temp_g[x][y])*0.0005

def update_oxygen():
    for _ in range(200):
        x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
        el=grid[x][y]
        if el in (FIRE,EMBER,PLASMA):
            rate=0.02 if el==FIRE else 0.01
            oxy[x][y]=max(0.0,oxy[x][y]-rate)
            for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx,ny=x+dx,y+dy
                if inb(nx,ny): oxy[nx][ny]=max(0.0,oxy[nx][ny]-rate*0.25)
            if oxy[x][y]<0.1 and random.random()<0.1:
                grid[x][y]=ASH if el==FIRE else SMOKE
                life[x][y]=random.randint(30,80) if el!=FIRE else 0
        elif el in (PLANT,LEAF,MOSS,SEAWEED) and is_day:
            oxy[x][y]=min(1.0,oxy[x][y]+0.015)
        elif y==0 or el in (EMPTY,AIR):
            oxy[x][y]=min(1.0,oxy[x][y]+0.03)
        if y>0 and inb(x,y-1):
            oxy[x][y]=min(1.0,oxy[x][y]+(oxy[x][y-1]-oxy[x][y])*0.1)

# ── Element update functions ──────────────────────────────────────────────────

def update_fire(x,y):
    if oxy[x][y]<0.05:
        grid[x][y]=ASH if random.random()<0.5 else SMOKE
        life[x][y]=random.randint(20,60) if grid[x][y]==SMOKE else 0; return
    temp_g[x][y]=min(1200.0,temp_g[x][y]+random.uniform(4,18))
    if random.random()<0.55:
        ny=y-1; nx=x+random.randint(-1,1)
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny)
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        nb=grid[nx][ny]
        f=FLAMMABLE.get(nb,0)
        if f>0 and random.random()<f*0.1*min(2.0,temp_g[x][y]/500.0):
            grid[nx][ny]=FIRE; life[nx][ny]=random.randint(80,200); temp_g[nx][ny]=400.0
    life[x][y]-=1
    if life[x][y]<=0:
        grid[x][y]=SMOKE if random.random()<0.65 else ASH
        life[x][y]=random.randint(30,80) if grid[x][y]==SMOKE else 0

def update_ember(x,y):
    temp_g[x][y]=max(180.0,temp_g[x][y]-1.5)
    if random.random()<0.25:
        ny=y-1; nx=x+random.randint(-1,1)
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and FLAMMABLE.get(grid[nx][ny],0)>0 and random.random()<0.04:
            grid[nx][ny]=FIRE; life[nx][ny]=random.randint(80,180)
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=ASH; life[x][y]=0

def update_smoke(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    dirs=[(-1,-1),(0,-1),(1,-1)]
    if wind_x!=0: dirs=[(d[0]+(1 if wind_x>0 else -1),d[1]) for d in dirs]
    random.shuffle(dirs)
    for dx,dy in dirs:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny); return
    for dx in [random.choice([-1,1])]:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_steam(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=WATER if temp_g[x][y]<90 else EMPTY; return
    temp_g[x][y]=max(temperature,temp_g[x][y]-0.4)
    for dx in [0,random.choice([-1,1])]:
        nx,ny=x+dx,y-1
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR,CLOUD): swap(x,y,nx,ny); return
    for dx in [random.choice([-1,1])]:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_water(x,y):
    if temp_g[x][y]<0 and random.random()<0.01: grid[x][y]=ICE; return
    if temp_g[x][y]>100 and random.random()<0.04: grid[x][y]=STEAM; life[x][y]=random.randint(60,120); return
    if inb(x,y+1):
        below=grid[x][y+1]
        if below in (EMPTY,AIR): swap(x,y,x,y+1); return
        if below==OIL and random.random()<0.6: swap(x,y,x,y+1); return
    # Try diagonal-down before spreading sideways (more gravity-like)
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return
    # Dissolve salt
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==SALT and random.random()<0.015: grid[nx][ny]=EMPTY

def update_lava(x,y):
    temp_g[x][y]=max(700.0,temp_g[x][y])
    if random.random()<0.002:
        temp_g[x][y]-=5
        if temp_g[x][y]<700: grid[x][y]=OBSIDIAN if random.random()<0.4 else STONE; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        nb=grid[nx][ny]
        if nb==WATER: grid[nx][ny]=STEAM; life[nx][ny]=random.randint(60,120); grid[x][y]=OBSIDIAN; return
        elif nb in (WOOD,PLANT,LEAF,OIL,PEAT,TAR) and random.random()<0.08: grid[nx][ny]=FIRE; life[nx][ny]=random.randint(100,200)
        elif nb==SAND and random.random()<0.015: grid[nx][ny]=GLASS
        elif nb==ICE: grid[nx][ny]=WATER; temp_g[nx][ny]=60.0
    # Flow like sand: always try straight down, then diagonal down, then sideways
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_sand(x,y):
    if wind_x!=0 and random.random()<abs(wind_x)*0.035:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y] in (EMPTY,AIR): swap(x,y,x+wx,y); return
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    # Wet contact
    for dx,dy in [(-1,0),(1,0),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==WATER and random.random()<0.002: grid[x][y]=WETDIRT

def update_snow(x,y):
    if temp_g[x][y]>1 and random.random()<0.025: grid[x][y]=WATER; return
    if wind_x!=0 and random.random()<abs(wind_x)*0.07:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y] in (EMPTY,AIR): swap(x,y,x+wx,y); return
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return

def update_ice(x,y):
    if temp_g[x][y]>4 and random.random()<0.01: grid[x][y]=WATER; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==WATER and temp_g[nx][ny]<2 and random.random()<0.004: grid[nx][ny]=ICE

def update_oil(x,y):
    if temp_g[x][y]>180 and random.random()<0.04: grid[x][y]=FIRE; life[x][y]=random.randint(100,200); return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    if inb(x,y+1) and grid[x][y+1]==WATER and random.random()<0.25: swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return

def update_acid(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    dissolve={STONE,WOOD,DIRT,SAND,GLASS,CONCRETE,GRAVEL,RUST,PLANT,ANIMAL,CORAL,MUD,LEAF,MOSS,FUNGUS,SEED,VINE,CHARCOAL}
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        tgt=grid[nx][ny]
        if tgt in dissolve and random.random()<0.03:
            grid[nx][ny]=EMPTY; life[x][y]=max(0,life[x][y]-5)
        elif tgt==WIRE and random.random()<0.04: grid[nx][ny]=RUST
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return

def update_gunpowder(x,y):
    hot=temp_g[x][y]>200 or any(inb(x+dx,y+dy) and grid[x+dx][y+dy] in (FIRE,LAVA,EMBER,LIGHTNING,CHARGED,PLASMA) for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)])
    if hot: explode(x,y,random.randint(4,9),1200); grid[x][y]=EMPTY; return
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return

def update_cloud(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    if wind_x!=0 and random.random()<0.25:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y] in (EMPTY,AIR,CLOUD): swap(x,y,x+wx,y); return
    if random.random()<0.08:
        nx=x+random.choice([-1,1])
        if inb(nx,y) and grid[nx][y] in (EMPTY,AIR): swap(x,y,nx,y); return
    if raining and random.random()<0.003 and inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR):
        grid[x][y+1]=SNOW if temperature<0 else WATER
        if grid[x][y+1]==WATER: temp_g[x][y+1]=max(temperature,10.0)

def update_ash(x,y):
    if wind_x!=0 and random.random()<abs(wind_x)*0.08:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y] in (EMPTY,AIR): swap(x,y,x+wx,y); return
    if random.random()<0.35:
        if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
        dirs=[-1,1]; random.shuffle(dirs)
        for dx in dirs:
            if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return

def update_salt(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==WATER and random.random()<0.018: grid[x][y]=EMPTY; return

def update_dirt(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==WATER and random.random()<0.01: grid[x][y]=WETDIRT; grid[nx][ny]=EMPTY; return

def update_wetdirt(x,y):
    if temp_g[x][y]>38 and random.random()<0.003: grid[x][y]=DIRT; return
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return

def update_mud(x,y):
    if temp_g[x][y]>42 and random.random()<0.002: grid[x][y]=DIRT; return
    if random.random()>0.35: return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR) and random.random()<0.3: swap(x,y,x+dx,y); return

def update_mercury(x,y):
    if inb(x,y+1):
        below=grid[x][y+1]
        if below in (EMPTY,AIR): swap(x,y,x,y+1); return
        if below in LIQUIDS and DENSITY[MERCURY]>DENSITY.get(below,0) and random.random()<0.8: swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return

def update_honey(x,y):
    if random.random()>0.12: return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    if random.random()<0.25:
        dx=random.choice([-1,1])
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_slime(x,y):
    if random.random()>0.4: return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return

def update_tar(x,y):
    if temp_g[x][y]>70 and random.random()<FLAMMABLE.get(TAR,0)*0.04: grid[x][y]=FIRE; life[x][y]=random.randint(120,260); return
    spd=0.22 if temp_g[x][y]>40 else 0.04
    if random.random()>spd: return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dx=random.choice([-1,1])
    if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_poison(x,y):
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==ANIMAL:
            g=gene[nx][ny]; resist=g.get('poison_resist',0) if g else 0
            if random.random()<0.04*(1-resist): grid[nx][ny]=EMPTY; gene[nx][ny]=None

def update_magma(x,y):
    temp_g[x][y]=max(900.0,temp_g[x][y])
    if random.random()<0.001 and temp_g[x][y]<900: grid[x][y]=BASALT; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny]==WATER: grid[nx][ny]=STEAM; life[nx][ny]=random.randint(60,120); grid[x][y]=BASALT; return
    if random.random()<0.2:
        if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
        dx=random.choice([-1,1])
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_seed(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    if inb(x,y+1) and grid[x][y+1] in (DIRT,WETDIRT,MUD,SAND):
        has_water=any(inb(x+dx,y+dy) and grid[x+dx][y+dy] in (WATER,WETDIRT,MUD) for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)])
        if has_water and random.random()<0.003:
            # Randomly grow into sapling, corn, or carrot
            r = random.random()
            if r < 0.15:   grid[x][y]=CORN;    life[x][y]=0
            elif r < 0.30: grid[x][y]=CARROT;  life[x][y]=0
            else:          grid[x][y]=SAPLING; life[x][y]=0

def update_sapling(x,y):
    life[x][y]+=1
    if life[x][y]>300 and random.random()<0.01:
        if inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR): grid[x][y-1]=WOOD
        if life[x][y]>500: tree_canopy(x,y-3)
        grid[x][y]=WOOD

def update_wheat(x,y):
    # Falls like a powder
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dx=random.choice([-1,1])
    if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    # Cook into bread near heat (fire/ember), burn near lava
    for ddx,ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx2,ny2=x+ddx,y+ddy
        if not inb(nx2,ny2): continue
        if grid[nx2][ny2] in (FIRE,EMBER) and random.random()<0.05:
            grid[x][y]=BREAD; return
        if grid[nx2][ny2] in (LAVA,MAGMA) and random.random()<0.08:
            grid[x][y]=FIRE; life[x][y]=random.randint(40,90); return

def update_apple(x,y):
    life[x][y]+=1
    if life[x][y]>2200: grid[x][y]=EMPTY; return  # rots
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dx=random.choice([-1,1])
    if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return

def update_berry(x,y):
    life[x][y]+=1
    if life[x][y]>900: grid[x][y]=EMPTY; return  # rots faster
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return

def update_bread(x,y):
    # Static food — burns near extreme heat only
    for ddx,ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx2,ny2=x+ddx,y+ddy
        if inb(nx2,ny2) and grid[nx2][ny2] in (LAVA,MAGMA) and random.random()<0.03:
            grid[x][y]=FIRE; life[x][y]=random.randint(80,150); return

def update_meat(x,y):
    life[x][y]+=1
    if life[x][y]>700: grid[x][y]=ASH; return  # rots to ash
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dx=random.choice([-1,1])
    if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    # Burns
    for ddx,ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx2,ny2=x+ddx,y+ddy
        if inb(nx2,ny2) and grid[nx2][ny2] in (FIRE,LAVA) and random.random()<0.06:
            grid[x][y]=FIRE; life[x][y]=random.randint(30,70); return

def update_vine(x,y):
    if random.random()<0.002:
        dirs=[(0,1),(-1,0),(1,0),(0,-1)]; random.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): grid[nx][ny]=VINE; break
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,EMBER) and random.random()<0.25: grid[x][y]=FIRE; life[x][y]=random.randint(80,160); return

def update_moss(x,y):
    if random.random()<0.001:
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,-1),(-1,1),(1,1)]:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (STONE,DIRT,WETDIRT,SAND):
                if any(inb(nx+sx,ny+sy) and grid[nx+sx][ny+sy]==WATER for sx,sy in [(-1,0),(1,0),(0,-1),(0,1)]):
                    if random.random()<0.3: grid[nx][ny]=MOSS; break

def update_fungus(x,y):
    if random.random()<0.002:
        dirs=[(-1,0),(1,0),(0,-1),(0,1)]
        for dx,dy in random.sample(dirs,len(dirs)):
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (DIRT,WETDIRT,WOOD,MUD,PEAT):
                if random.random()<0.5: grid[nx][ny]=FUNGUS; break
    if random.random()<0.0005 and inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR):
        grid[x][y-1]=SPORE; life[x][y-1]=random.randint(60,200)
    # Occasionally sprout a mushroom above
    if random.random()<0.0002 and inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR):
        grid[x][y-1]=MUSHROOM; life[x][y-1]=0

def update_spore(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    if wind_x!=0 and random.random()<abs(wind_x)*0.1:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y] in (EMPTY,AIR): swap(x,y,x+wx,y); return
    if random.random()<0.4:
        ny=y+(-1 if random.random()<0.6 else 1); nx=x+random.choice([-1,0,1])
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny)

def update_gravel(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return

def update_clay(x,y):
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,LAVA) and random.random()<0.04: grid[x][y]=CERAMIC; return

def update_resin(x,y):
    if random.random()>0.05: return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dx=random.choice([-1,1])
    if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_wax(x,y):
    if temp_g[x][y]>60 and random.random()<0.04:
        if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==FIRE and random.random()<FLAMMABLE.get(WAX,0)*0.08: grid[x][y]=FIRE; life[x][y]=random.randint(150,300); return

def update_peat(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,EMBER) and random.random()<FLAMMABLE.get(PEAT,0)*0.04: grid[x][y]=FIRE; life[x][y]=random.randint(200,500); return

def update_seaweed(x,y):
    if inb(x,y-1) and grid[x][y-1]==WATER and random.random()<0.001: grid[x][y-1]=SEAWEED
    if not any(inb(x+dx,y+dy) and grid[x+dx][y+dy]==WATER for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]) and random.random()<0.005: grid[x][y]=PLANT

def update_jellyfish(x,y):
    if not any(inb(x+dx,y+dy) and grid[x+dx][y+dy]==WATER for dx,dy in [(-1,0),(1,0),(0,-1),(0,1),(0,1)]):
        if random.random()<0.02: grid[x][y]=EMPTY; return
    if random.random()<0.3:
        dy2=-1 if random.random()<0.6 else 1; dx2=random.choice([-1,0,1])
        if inb(x+dx2,y+dy2) and grid[x+dx2][y+dy2]==WATER: swap(x,y,x+dx2,y+dy2)

def update_bubble(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    if random.random()<0.5:
        dx=random.choice([-1,0,1])
        if inb(x+dx,y-1) and grid[x+dx][y-1] in (EMPTY,AIR,WATER): swap(x,y,x+dx,y-1)

def update_plasma(x,y):
    temp_g[x][y]=max(2000.0,temp_g[x][y])
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] not in (EMPTY,AIR,PLASMA,STONE,OBSIDIAN) and random.random()<0.08: grid[nx][ny]=FIRE; life[nx][ny]=100
    if random.random()<0.5:
        nx=x+random.randint(-1,1)
        if inb(nx,y-1) and grid[nx][y-1] in (EMPTY,AIR): swap(x,y,nx,y-1)

def update_neon(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    if random.random()<0.4:
        dx2=random.choice([-1,0,1]); dy2=-1 if random.random()<0.7 else 0
        if inb(x+dx2,y+dy2) and grid[x+dx2][y+dy2] in (EMPTY,AIR): swap(x,y,x+dx2,y+dy2)

def update_lightning_bolt(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY

def update_charged(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=WIRE; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny]==ANIMAL and random.random()<0.2: grid[nx][ny]=EMPTY; gene[nx][ny]=None
        elif grid[nx][ny]==WATER and random.random()<0.1: grid[nx][ny]=STEAM; life[nx][ny]=random.randint(40,80)

def update_pressgas(x,y):
    dirs=[(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)]
    for dx,dy in random.sample(dirs,len(dirs)):
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny); return
    life[x][y]+=1
    if life[x][y]>200: grid[x][y]=EMPTY

def update_air_cell(x,y):
    life[x][y]+=1
    if life[x][y]>280: grid[x][y]=EMPTY; return
    if wind_x!=0 and random.random()<abs(wind_x)*0.1:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y]==EMPTY: swap(x,y,x+wx,y); return
    if random.random()<0.3:
        dx2=random.choice([-1,0,1]); dy2=-1 if random.random()<0.6 else 0
        if inb(x+dx2,y+dy2) and grid[x+dx2][y+dy2]==EMPTY: swap(x,y,x+dx2,y+dy2)

def update_charcoal(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,LAVA,EMBER) and random.random()<FLAMMABLE[CHARCOAL]*0.05: grid[x][y]=FIRE; life[x][y]=random.randint(200,500); return

def update_rust(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return

def update_sandstone(x,y):
    for dx,dy in [(-1,0),(1,0)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==ACID and random.random()<0.02: grid[x][y]=SAND; return

def tree_canopy(cx: int, cy: int):
    radius=random.randint(3,6)
    for dx in range(-radius,radius+1):
        for dy in range(-radius,radius+1):
            d=dx*dx+dy*dy
            if d<=radius*radius:
                nx,ny=cx+dx,cy+dy
                if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR):
                    if random.random()<0.92-(d/(radius*radius))*0.4: grid[nx][ny]=LEAF

def update_plant(x,y):
    if not inb(x,y+1) or grid[x][y+1] not in (DIRT,SAND,MUD,WETDIRT,PEAT):
        if random.random()<0.01: grid[x][y]=EMPTY
        return
    has_water=any(inb(x+dx,y+dy) and grid[x+dx][y+dy] in (WATER,WETDIRT,MUD) for dx,dy in [(-1,0),(1,0),(0,1)])
    has_light=is_day and y<ROWS*0.8
    good_temp=10<temp_g[x][y]<38
    rate=0.004*(3 if has_water else 1)*(2 if has_light else 1)*(0.25 if not good_temp else 1)
    if random.random()<rate:
        dirs=[(-1,-1),(0,-1),(1,-1),(-1,0),(1,0)]; random.shuffle(dirs)
        for dx,dy in dirs:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR):
                if any(inb(nx+sx,ny+sy) and grid[nx+sx][ny+sy] in (DIRT,SAND,MUD,WETDIRT) for sx,sy in [(0,1),(-1,1),(1,1)]):
                    grid[nx][ny]=PLANT; break
    if random.random()<0.0002 and inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR): grid[x][y-1]=SEED

def update_leaf(x,y):
    life[x][y]+=1
    if life[x][y]>2200 and random.random()<0.001: grid[x][y]=DIRT; return
    if wind_x!=0 and random.random()<abs(wind_x)*0.04:
        wx=1 if wind_x>0 else -1
        if inb(x+wx,y) and grid[x+wx][y] in (EMPTY,AIR): swap(x,y,x+wx,y); return
    attached=inb(x,y+1) and grid[x][y+1] not in (EMPTY,AIR)
    if not attached and random.random()<0.04:
        if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1)

def update_animal(x,y):
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    age=data[x][y]; ct=temp_g[x][y]
    if ct>35+g['heat_resist']*30 and random.random()<0.02*(1-g['heat_resist']): grid[x][y]=EMPTY; gene[x][y]=None; return
    if ct<-5-g['cold_resist']*20 and random.random()<0.02*(1-g['cold_resist']): grid[x][y]=EMPTY; gene[x][y]=None; return
    direction: int = int(life[x][y]) if life[x][y]!=0 else random.choice([-1,1]); life[x][y]=direction
    can_fly=g['flying'] and age>50; can_swim=g['amphibious']
    if not can_fly:
        if inb(x,y+1):
            below=grid[x][y+1]
            if below in (EMPTY,AIR) or (below==WATER and not can_swim):
                swap(x,y,x,y+1)
                if below==WATER and not can_swim and random.random()<0.03: grid[x][y+1]=EMPTY; gene[x][y+1]=None
                return
    if random.random() < float(g.get('speed', 0.1)):
        for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx,ny=x+dx,y+dy
            if not inb(nx,ny): continue
            tgt=grid[nx][ny]
            if g['herbivore'] and tgt in (PLANT,LEAF,MOSS,SEED): grid[nx][ny]=EMPTY; data[x][y]=max(0,data[x][y]-10)
            elif g['carnivore'] and tgt==ANIMAL:
                tg=gene[nx][ny]
                if tg and data[nx][ny]<age: grid[nx][ny]=EMPTY; gene[nx][ny]=None; data[x][y]=max(0,data[x][y]-20)
        nx=x+direction
        if inb(nx,y) and grid[nx][y] in (EMPTY,AIR): swap(x,y,nx,y)
        else: life[x][y]=-direction
    data[x][y]+=g.get('metabolism',1.0)
    if data[x][y]>g['lifespan']: grid[x][y]=DIRT; gene[x][y]=None; return
    if age>100 and age<g['lifespan']*0.8 and random.random()<0.001:
        for dx,dy in [(-2,0),(2,0),(0,-2),(0,2)]:
            mx,my=x+dx,y+dy
            if inb(mx,my) and grid[mx][my]==ANIMAL:
                mg=gene[mx][my]
                if mg and data[mx][my]>100:
                    for bx,by in [(x-1,y),(x+1,y),(x,y-1)]:
                        if inb(bx,by) and grid[bx][by] in (EMPTY,AIR):
                            grid[bx][by]=ANIMAL; gene[bx][by]=make_genes(g,mg)
                            data[bx][by]=0; life[bx][by]=random.choice([-1,1]); break
                    break

# ── New element update functions ──────────────────────────────────────────────

def update_methane(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,EMBER,LIGHTNING,PLASMA,CHARGED):
            explode(x,y,random.randint(4,10),1400); grid[x][y]=EMPTY; return
    dirs=[(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)]
    random.shuffle(dirs)
    for dx,dy in dirs:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny); return

def update_nitro(x,y):
    if temp_g[x][y]>60:
        explode(x,y,random.randint(8,18),2200); grid[x][y]=EMPTY; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny] in (FIRE,EMBER,LIGHTNING,PLASMA,LAVA,MAGMA):
            explode(x,y,random.randint(10,20),2500); grid[x][y]=EMPTY; return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def update_quicksand(x,y):
    if random.random()>0.65: return
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR) and random.random()<0.25: swap(x,y,x+dx,y); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny]==ANIMAL and random.random()<0.04:
            grid[nx][ny]=EMPTY; gene[nx][ny]=None

def update_steel(x,y):
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny]==ACID and random.random()<0.012: grid[x][y]=RUST; return
        if grid[nx][ny]==WATER and random.random()<0.0002: grid[x][y]=RUST; return

def update_sugar(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny]==WATER and random.random()<0.025: grid[x][y]=EMPTY; return
        if grid[nx][ny] in (FIRE,EMBER,LAVA) and random.random()<0.18:
            grid[x][y]=FIRE; life[x][y]=random.randint(80,160); return

def update_uranium(x,y):
    temp_g[x][y]=min(temp_g[x][y]+0.3, 180.0)
    if random.random()<0.0025:
        dx,dy=random.randint(-4,4),random.randint(-4,4)
        nx,ny=x+dx,y+dy
        if inb(nx,ny):
            tgt=grid[nx][ny]
            if tgt==ANIMAL: grid[nx][ny]=EMPTY; gene[nx][ny]=None
            elif tgt in (PLANT,SAND,DIRT,MOSS): grid[nx][ny]=ASH
            elif tgt in (EMPTY,AIR) and random.random()<0.15:
                grid[nx][ny]=NEON; life[nx][ny]=random.randint(20,60)
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny): temp_g[nx][ny]=min(temp_g[nx][ny]+0.4,200.0)

def update_void(x,y):
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] not in (EMPTY,VOID,AIR,STONE,OBSIDIAN):
            if random.random()<0.18:
                grid[nx][ny]=EMPTY; life[nx][ny]=0; data[nx][ny]=0; gene[nx][ny]=None

# ── Real element physics ───────────────────────────────────────────────────────

def update_hydrogen(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,EMBER,LIGHTNING,LAVA,MAGMA):
            explode(x,y,random.randint(6,14),1800)
            # H2 + O2 → H2O
            for ex in range(max(0,x-6),min(COLS,x+6)):
                for ey in range(max(0,y-6),min(ROWS,y+6)):
                    if grid[ex][ey]==HYDROGEN and random.random()<0.5:
                        grid[ex][ey]=STEAM; life[ex][ey]=random.randint(40,90)
            grid[x][y]=STEAM; life[x][y]=random.randint(30,70); return
    dirs=[(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)]; random.shuffle(dirs)
    for dx,dy in dirs:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny); return

def update_sulfur(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny] in (FIRE,EMBER,LAVA,MAGMA) and random.random()<0.10:
            grid[x][y]=FIRE; life[x][y]=random.randint(50,120); return
        # S + H2O → weak H2SO4
        if grid[nx][ny]==WATER and random.random()<0.004:
            grid[nx][ny]=ACID; life[nx][ny]=random.randint(60,130)
            grid[x][y]=EMPTY; return

def update_helium(x,y):
    life[x][y]-=1
    if life[x][y]<=0: grid[x][y]=EMPTY; return
    dirs=[(0,-1),(-1,-1),(1,-1),(-1,0),(1,0)]; random.shuffle(dirs)
    for dx,dy in dirs:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR): swap(x,y,nx,ny); return

def update_coal(x,y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1); return
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FIRE,LAVA,EMBER,MAGMA) and random.random()<0.04:
            grid[x][y]=FIRE; life[x][y]=random.randint(500,1100); temp_g[x][y]=900.0; return

def update_copper(x,y):
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if not inb(nx,ny): continue
        if grid[nx][ny]==ACID   and random.random()<0.015: grid[x][y]=EMPTY; return
        if grid[nx][ny]==WATER  and random.random()<0.0003: grid[x][y]=RUST; return
        if grid[nx][ny] in (FIRE,LAVA,MAGMA) and random.random()<0.0005: grid[x][y]=LAVA; return

# ── Animal sub-types ──────────────────────────────────────────────────────────

def _is_hazard_at(nx, ny):
    return inb(nx,ny) and grid[nx][ny] in HAZARDS

_FORGE_HEAT = {FIRE, LAVA, MAGMA, CHARCOAL, EMBER}
def _is_forge_nearby(x, y):
    """True if STONE + heat source (fire/lava/charcoal) are both within 3 cells."""
    has_stone = has_heat = False
    for ox in range(-3, 4):
        for oy in range(-3, 4):
            c = grid[x+ox][y+oy] if inb(x+ox,y+oy) else EMPTY
            if c == STONE:    has_stone = True
            if c in _FORGE_HEAT: has_heat  = True
            if has_stone and has_heat: return True
    return False

def _ground_under(nx, ny):
    """True when cell (nx,ny+1) is a solid the animal can stand on."""
    return inb(nx,ny+1) and grid[nx][ny+1] in GROUND_SOLIDS

def _try_breed(x, y, etype, min_age, lifespan, spawn_in=(EMPTY, AIR), chance=0.0004):
    """Spawn a baby of etype near (x,y) if a mature same-type mate is close. Returns True on success."""
    if data[x][y] < min_age or data[x][y] > lifespan * 0.75: return False
    if random.random() > chance: return False
    for dx, dy in [(-2,0),(2,0),(0,-2),(0,2),(-1,0),(1,0),(0,-1),(0,1)]:
        mx, my = x+dx, y+dy
        if not inb(mx,my) or grid[mx][my] != etype or data[mx][my] < min_age: continue
        spots = [(x-1,y),(x+1,y),(x,y-1),(x-1,y-1),(x+1,y-1),(x,y+1)]
        random.shuffle(spots)
        for bx, by in spots:
            if inb(bx,by) and grid[bx][by] in spawn_in:
                grid[bx][by] = etype
                gene[bx][by] = make_genes(gene[x][y], gene[mx][my])
                data[bx][by] = 0
                life[bx][by] = random.choice([-1,1])
                return True
        break
    return False

def update_bird(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); g['flying']=True; gene[x][y]=g
    data[x][y]+=1
    if data[x][y]>4800: grid[x][y]=EMPTY; gene[x][y]=None; return  # starve
    # Die from hazards
    if grid[x][y] in HAZARDS: grid[x][y]=EMPTY; gene[x][y]=None; return
    # Flee immediate hazards
    for dx,dy in [(-1,0),(1,0),(0,1),(0,-1)]:
        nx,ny=x+dx,y+dy
        if _is_hazard_at(nx,ny) or (inb(nx,ny) and grid[nx][ny]==WATER):
            for fx,fy in [(0,-1),(-1,-1),(1,-1)]:
                tx,ty=x+fx,y+fy
                if inb(tx,ty) and grid[tx][ty] in (EMPTY,AIR): swap(x,y,tx,ty); return
    # Eat seeds / plants
    for dx,dy in [(-1,0),(1,0),(0,1),(0,-1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (SEED,PLANT,MOSS) and random.random()<0.06:
            grid[nx][ny]=EMPTY; data[x][y]=max(0,data[x][y]-40); break
    # Fly
    if random.random()<0.55:
        d=life[x][y] if life[x][y]!=0 else random.choice([-1,1])
        for dx,dy in [(d,0),(d,-1),(0,-1),(0,1),(-d,0)]:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (EMPTY,AIR):
                if not _is_hazard_at(nx,ny) and grid[nx][ny]!=WATER:
                    swap(x,y,nx,ny); life[x][y]=d; return
        life[x][y]=-d
    # Occasional glide down
    elif random.random()<0.08 and inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR):
        swap(x,y,x,y+1)
    _try_breed(x, y, BIRD, 600, 4800)

def update_fish(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    in_water=any(inb(x+dx,y+dy) and grid[x+dx][y+dy] in (WATER,MUD,WETDIRT)
                 for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)])
    if not in_water:
        # Suffocate on land
        life[x][y]-=1
        if life[x][y]<=0: grid[x][y]=EMPTY; gene[x][y]=None; return
        # Flop toward nearest water direction
        for dx,dy in [(0,1),(0,-1),(-1,0),(1,0)]:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (WATER,MUD,WETDIRT): swap(x,y,nx,ny); return
        if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1)
        return
    life[x][y]=60  # reset air-timer when in water
    data[x][y]+=1
    if data[x][y]>6000: grid[x][y]=EMPTY; gene[x][y]=None; return
    # Eat seaweed / jellyfish
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (SEAWEED,JELLYFISH) and random.random()<0.04:
            grid[nx][ny]=WATER; data[x][y]=max(0,data[x][y]-50)
    # Swim: prefer horizontal motion with gentle bob
    if random.random()<0.55:
        d=life[x][y]%2*2-1 if life[x][y]>1 else random.choice([-1,1])
        d=life[x][y] if abs(life[x][y])==1 else d
        for dx,dy in [(d,0),(0,-1),(0,1),(-d,0),(d,-1),(d,1)]:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (WATER,MUD,WETDIRT):
                swap(x,y,nx,ny)
                if abs(dx)==1: life[x][y]=dx
                return
        life[x][y]=-life[x][y] if abs(life[x][y])==1 else random.choice([-1,1])
    _try_breed(x, y, FISH, 500, 6000, spawn_in=(WATER, MUD, WETDIRT))

def update_predator(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); g['carnivore']=True; gene[x][y]=g
    data[x][y]+=1
    if data[x][y]>7200: grid[x][y]=EMPTY; gene[x][y]=None; return
    d=life[x][y] if life[x][y]!=0 else random.choice([-1,1])
    # Avoid hazards & deep water ahead
    nx_fwd=x+d
    if _is_hazard_at(nx_fwd,y) or (inb(nx_fwd,y) and grid[nx_fwd][y]==WATER):
        d=-d; life[x][y]=d
    # Gravity
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR):
        swap(x,y,x,y+1); return
    # Hunt prey in range
    prey_found=False
    for dx in range(-4,5):
        for dy in range(-2,3):
            nx,ny=x+dx,y+dy
            if not inb(nx,ny): continue
            if grid[nx][ny] in (ANIMAL,BIRD,HUMAN):
                mdx=1 if nx>x else -1 if nx<x else 0
                tx,ty=x+mdx,y
                if inb(tx,y) and grid[tx][y] in (EMPTY,AIR) and not _is_hazard_at(tx,y):
                    if (tx==nx and ty==ny):
                        gene[nx][ny]=None; grid[nx][ny]=MEAT; life[nx][ny]=0; data[x][y]=max(0,data[x][y]-150)
                    else:
                        swap(x,y,tx,y); life[x][y]=mdx if mdx!=0 else d
                    prey_found=True; break
        if prey_found: break
    if not prey_found and random.random()<0.5:
        nx=x+d
        if inb(nx,y) and grid[nx][y] in (EMPTY,AIR) and _ground_under(nx,y):
            swap(x,y,nx,y)
        elif inb(nx,y-1) and grid[nx][y] not in (EMPTY,AIR) and grid[nx][y-1] in (EMPTY,AIR):
            swap(x,y,nx,y-1)  # step up
        else:
            life[x][y]=-d
    _try_breed(x, y, PREDATOR, 1000, 7200)

_HUMAN_FOOD  = {PLANT, SEED, MOSS, FUNGUS, LEAF, HONEY, SEAWEED, SUGAR, SAPLING,
                WHEAT, APPLE, BERRY, BREAD, MEAT, COOKED_MEAT, MUSHROOM, CORN, CARROT, DOUGH}
_HUMAN_DRINK  = {WATER, MUD, WETDIRT, ICE}   # sources of drinkable water
_MINEABLE     = {STONE, DIRT, WOOD, GRAVEL, SAND, CLAY, COAL, COPPER, GOLD,
                 SANDSTONE, BASALT, OBSIDIAN, CHARCOAL, PEAT}  # blocks humans can mine
_SHELTER_MAT  = WOOD    # material humans build shelters from
_HUMAN_PREY   = {ANIMAL, BIRD, FISH, RABBIT}
_HUMAN_THREAT = {PREDATOR, TIGER, LION, BEAR, SNAKE}
_VALUABLES    = {GOLD, COPPER, CRYSTAL, COAL}   # humans prospect for these

# ── Tier-1 tools: crafted from raw materials, no forge needed (knowledge ≥ 250)
_CRAFT_TOOLS_BASIC = {
    frozenset({WOOD,   STONE  }): 'axe',      # chop/mine wood faster
    frozenset({WOOD,   COPPER }): 'spear',    # fight and hunt
    frozenset({STONE,  COAL   }): 'pick',     # mine ore/stone faster
    frozenset({COPPER, STONE  }): 'knife',    # better food efficiency
    frozenset({CLAY,   CHARCOAL}): 'torch',   # light + knowledge aura
    frozenset({WOOD,   VINE   }): 'bow',      # ranged: attack from 3 cells
}
# ── Tier-2 tools: require a FORGE (stone+fire/lava/charcoal within 3 cells)
#    and knowledge ≥ 600
_CRAFT_TOOLS_FORGE = {
    frozenset({COPPER, COAL   }): 'copper_sword',  # +50% spear damage, more durability
    frozenset({STEEL,  COAL   }): 'steel_pick',    # best mining speed, breaks obsidian
    frozenset({STEEL,  STONE  }): 'steel_axe',     # best wood harvesting
    frozenset({COPPER, CRYSTAL}): 'copper_armor',  # halves combat damage taken
    frozenset({GOLD,   CRYSTAL}): 'crown',         # prestige: +200 knowledge, max wealth
    frozenset({STEEL,  COPPER }): 'sword',         # balanced weapon, 60 durability
    frozenset({CRYSTAL,STONE  }): 'lens',          # +50 knowledge/tick when held, rare
}
# All tool recipes combined for quick lookup
_CRAFT_TOOLS = {**_CRAFT_TOOLS_BASIC, **_CRAFT_TOOLS_FORGE}

# Tool stats: (knowledge_req, dur, forge_needed)
_TOOL_STATS = {
    'axe':          (250,  60, False),
    'spear':        (250,  60, False),
    'pick':         (250,  60, False),
    'knife':        (250,  55, False),
    'torch':        (200,  80, False),
    'bow':          (300,  50, False),
    'copper_sword': (600, 100, True),
    'steel_pick':   (700, 120, True),
    'steel_axe':    (700, 110, True),
    'copper_armor': (600,  90, True),
    'crown':        (800,  999, True),
    'sword':        (600,  80, True),
    'lens':         (750,  40, True),
}

# Goods humans can carry for trading: element -> trade value in "credits"
_TRADE_VALUE  = {GOLD:10, COPPER:5, CRYSTAL:8, COAL:2, STEEL:7,
                 BREAD:4, COOKED_MEAT:4, APPLE:2, HONEY:3}
_FOOD_VALUE  = {
    BREAD:500, COOKED_MEAT:450, MEAT:400, HONEY:350, APPLE:300,
    CORN:280, CARROT:260, MUSHROOM:220, WHEAT:200,
    BERRY:150, SUGAR:150, DOUGH:140, FUNGUS:120, SEAWEED:120, PLANT:120,
    MOSS:100, SAPLING:100, SEED:80, LEAF:70,
}

def update_human(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    # ── Initialise state keys ─────────────────────────────────────────────────
    g.setdefault('hunger',   0)
    g.setdefault('thirst',   0)     # NEW: dehydration counter (dies > 600)
    g.setdefault('fear_dir', 0)
    g.setdefault('fear_age', 0)
    g.setdefault('courage',  random.randint(60,130))
    g.setdefault('goal',     'idle')
    g.setdefault('tx',       -1)
    g.setdefault('ty',       -1)
    g.setdefault('scan_cd',  0)
    g.setdefault('mem_fx',   -1)    # remembered food location
    g.setdefault('mem_fy',   -1)
    g.setdefault('mem_age',  0)
    g.setdefault('mem_wx',   -1)    # remembered water location
    g.setdefault('mem_wy',   -1)
    g.setdefault('mem_wage', 0)
    g.setdefault('rev_ct',    0)
    g.setdefault('idle_t',    0)
    g.setdefault('knowledge', 720)
    g.setdefault('craft_cd',  0)
    g.setdefault('blocks',    5)
    g.setdefault('mine_cd',   0)
    g.setdefault('health',    100)   # combat health 0-100
    g.setdefault('fight_cd',  0)     # attack cooldown
    g.setdefault('tools',     {})    # {'axe':dur,'spear':dur,'pick':dur,'knife':dur,'torch':dur}
    g.setdefault('inv',       {})    # {'gold':n,'copper':n,'coal':n,'crystal':n,...}
    g.setdefault('tool_cd',   0)     # tool crafting cooldown

    # ── Age, hunger, thirst ───────────────────────────────────────────────────
    data[x][y] += 1
    age = data[x][y]
    if age % 3 == 0: g['hunger'] += 1        # hunger: +1 every 3 ticks
    if age % 2 == 0: g['thirst'] += 1        # thirst: +1 every 2 ticks (faster!)
    if age > 36000 or g['hunger'] > 1000 or g['thirst'] > 600 or g['health'] <= 0:
        grid[x][y]=EMPTY; gene[x][y]=None; return

    # ── Knowledge gain (fast — humans learn quickly) ──────────────────────────
    near_humans = sum(1 for ox,oy in [(-3,0),(-2,0),(-1,0),(1,0),(2,0),(3,0)]
                      if inb(x+ox,y+oy) and grid[x+ox][y+oy]==HUMAN)
    g['knowledge'] = min(1000, g['knowledge'] + max(1, near_humans * 8) + 2)

    d = life[x][y] if life[x][y] != 0 else random.choice([-1,1])

    # ── Drink adjacent water ──────────────────────────────────────────────────
    for ddx,ddy in [(-1,0),(1,0),(0,1),(0,-1),(0,0)]:
        nx2,ny2 = x+ddx, y+ddy
        if inb(nx2,ny2) and grid[nx2][ny2] in _HUMAN_DRINK:
            g['thirst'] = max(0, g['thirst'] - 400)
            g['mem_wx'] = nx2; g['mem_wy'] = ny2; g['mem_wage'] = 0
            if g['goal'] == 'drink': g['goal']='idle'; g['tx']=-1
            break

    # ── Pick up valuables when walking over them ──────────────────────────────
    for ddx,ddy in [(0,0),(-1,0),(1,0),(0,1),(0,-1)]:
        nx2,ny2 = x+ddx, y+ddy
        if inb(nx2,ny2) and grid[nx2][ny2] in _VALUABLES:
            el = grid[nx2][ny2]
            grid[nx2][ny2] = EMPTY
            key = {GOLD:'gold', COPPER:'copper', COAL:'coal', CRYSTAL:'crystal'}.get(el,'gold')
            g['inv'][key] = g['inv'].get(key, 0) + 1
            g['knowledge'] = min(1000, g['knowledge'] + _TRADE_VALUE.get(el,1)*3)
            if g['goal'] == 'prospect': g['goal']='idle'; g['tx']=-1
            break

    # ── Eat adjacent food ─────────────────────────────────────────────────────
    for ddx,ddy in [(-1,0),(1,0),(0,1),(0,-1),(0,0)]:
        nx2,ny2 = x+ddx, y+ddy
        if inb(nx2,ny2) and grid[nx2][ny2] in _HUMAN_FOOD:
            nv = _FOOD_VALUE.get(grid[nx2][ny2], 150)
            # Knife makes eating more efficient
            if g['tools'].get('knife',0) > 0: nv = int(nv * 1.3)
            grid[nx2][ny2] = EMPTY
            g['hunger'] = max(0, g['hunger'] - nv)
            g['mem_fx'] = -1
            if g['goal'] in ('forage','hunt'): g['goal']='idle'; g['tx']=-1
            break

    # ── Hunt: spear allows killing from range 2, bare-hand kills adjacent ────
    hunt_range = 2 if g['tools'].get('spear',0) > 0 else 1
    if g['hunger'] > 300:
        for ddx in range(-hunt_range, hunt_range+1):
            for ddy in range(-hunt_range, hunt_range+1):
                nx2,ny2 = x+ddx, y+ddy
                if inb(nx2,ny2) and grid[nx2][ny2] in _HUMAN_PREY:
                    gene[nx2][ny2]=None; grid[nx2][ny2]=MEAT
                    g['hunger'] = max(0, g['hunger'] - _FOOD_VALUE.get(MEAT,400))
                    if g['tools'].get('spear',0) > 0:
                        g['tools']['spear'] = max(0, g['tools']['spear'] - 1)
                    if g['goal'] == 'hunt': g['goal']='idle'; g['tx']=-1
                    break
            else: continue; break

    # ── Combat: fight threats with spear, take damage without ─────────────────
    g['fight_cd'] = max(0, g['fight_cd'] - 1)
    for ddx in range(-2, 3):
        for ddy in range(-2, 3):
            nx2,ny2 = x+ddx, y+ddy
            if not inb(nx2,ny2) or grid[nx2][ny2] not in _HUMAN_THREAT: continue
            if g['tools'].get('spear',0) > 0 and g['fight_cd'] == 0:
                # Attack with spear: deal damage to threat gene's health
                tg = gene[nx2][ny2]
                if tg is None: tg = make_genes(); gene[nx2][ny2] = tg
                tg['health'] = tg.get('health', 100) - random.randint(25, 45)
                if tg['health'] <= 0:
                    grid[nx2][ny2] = MEAT
                    gene[nx2][ny2] = None
                    g['inv']['gold'] = g['inv'].get('gold',0) + 1  # trophy
                g['fight_cd'] = 18
                g['tools']['spear'] = max(0, g['tools']['spear'] - 1)
            elif g['fight_cd'] == 0:
                # Unarmed (or sword): take reduced damage if armored
                dmg = random.randint(8, 18)
                if g['tools'].get('copper_armor', 0) > 0:
                    dmg = dmg // 2
                    g['tools']['copper_armor'] = max(0, g['tools']['copper_armor'] - 1)
                g['health'] = max(0, g['health'] - dmg)
                g['fight_cd'] = 12
            break
        else: continue; break
    # Heal slowly over time when fed and watered
    if g['hunger'] < 300 and g['thirst'] < 200 and age % 20 == 0:
        g['health'] = min(100, g['health'] + 1)
    # Lens: passive knowledge gain aura
    if g['tools'].get('lens', 0) > 0 and age % 4 == 0:
        g['knowledge'] = min(1000, g['knowledge'] + 3)
        g['tools']['lens'] = max(0, g['tools']['lens'] - 1)
    # Bow: ranged attack on threats up to 3 cells (cost 1 durability per shot)
    if g['tools'].get('bow', 0) > 0 and g['fight_cd'] == 0:
        for ox in range(-3, 4):
            for oy in range(-2, 3):
                nx2,ny2 = x+ox, y+oy
                if inb(nx2,ny2) and grid[nx2][ny2] in _HUMAN_THREAT:
                    tg2 = gene[nx2][ny2]
                    if tg2 is None: tg2 = make_genes(); gene[nx2][ny2] = tg2
                    tg2['health'] = tg2.get('health', 100) - random.randint(15, 30)
                    if tg2['health'] <= 0:
                        grid[nx2][ny2] = MEAT; gene[nx2][ny2] = None
                    g['tools']['bow'] = max(0, g['tools']['bow'] - 1)
                    g['fight_cd'] = 25; break
            else: continue; break
    # Copper armor: damage reduction applied in combat (flag check)
    # Crown: mark as high-status (knowledge always 1000 while held)
    if g['tools'].get('crown', 0) > 0:
        g['knowledge'] = 1000

    # ── Tool crafting (tiered: basic / forge) ────────────────────────────────
    g['tool_cd'] = max(0, g['tool_cd'] - 1)
    if g['tool_cd'] == 0:
        adj = []
        for ddx,ddy in [(-1,0),(1,0),(0,1),(0,-1)]:
            nx2,ny2 = x+ddx, y+ddy
            if inb(nx2,ny2) and grid[nx2][ny2] not in (EMPTY,AIR,HUMAN):
                adj.append((nx2, ny2, grid[nx2][ny2]))
        for i in range(len(adj)):
            for j in range(i+1, len(adj)):
                ax,ay,ae = adj[i]; bx,by,be = adj[j]
                key = frozenset({ae, be})
                if key not in _CRAFT_TOOLS: continue
                tool = _CRAFT_TOOLS[key]
                req_k, dur, needs_forge = _TOOL_STATS.get(tool, (300, 60, False))
                if g['knowledge'] < req_k: continue
                if needs_forge and not _is_forge_nearby(x, y): continue
                # Craft it
                grid[ax][ay] = EMPTY; grid[bx][by] = EMPTY
                g['tools'][tool] = g['tools'].get(tool, 0) + dur
                kn_gain = 120 if needs_forge else 80
                g['knowledge'] = min(1000, g['knowledge'] + kn_gain)
                g['tool_cd'] = 120 if needs_forge else 80
                # Crown is special: instant knowledge boost
                if tool == 'crown': g['knowledge'] = 1000
                # Lens: passive knowledge aura handled below
                break
            else: continue; break

    # ── Element crafting (food + materials) ───────────────────────────────────
    g['craft_cd'] = max(0, g['craft_cd'] - 1)
    if g['knowledge'] >= 50 and g['craft_cd'] == 0:
        adj = []
        for ddx,ddy in [(-1,0),(1,0),(0,1),(0,-1)]:
            nx2,ny2 = x+ddx, y+ddy
            if inb(nx2,ny2) and grid[nx2][ny2] not in (EMPTY,AIR,HUMAN):
                adj.append((nx2, ny2, grid[nx2][ny2]))
        crafted = False
        for i in range(len(adj)):
            if crafted: break
            for j in range(i+1, len(adj)):
                ax,ay,ae = adj[i]; bx,by,be = adj[j]
                key = frozenset({ae, be})
                if key in _CRAFT_RECIPES and key not in _CRAFT_TOOLS:
                    needs_k = {frozenset({SAND,STONE}):200, frozenset({CLAY,WATER}):150}
                    if g['knowledge'] >= needs_k.get(key, 50):
                        grid[ax][ay] = _CRAFT_RECIPES[key]; life[ax][ay]=0; data[ax][ay]=0
                        grid[bx][by] = EMPTY
                        g['knowledge'] = min(1000, g['knowledge'] + 60)
                        g['craft_cd'] = 40
                        crafted = True; break

    # ── Reproduction ─────────────────────────────────────────────────────────
    if (age > 2000 and age < 28000 and
            g['hunger'] < 300 and g['thirst'] < 200 and random.random() < 0.0005):
        for ox,oy in [(-2,0),(2,0),(-1,0),(1,0),(0,-1),(0,1)]:
            mx,my = x+ox, y+oy
            if not inb(mx,my) or grid[mx][my] != HUMAN: continue
            mg = gene[mx][my]
            if mg is None or data[mx][my] < 2000 or mg.get('hunger',999) > 300: continue
            spots = [(x-1,y),(x+1,y),(x,y-1),(x-1,y-1),(x+1,y-1)]
            random.shuffle(spots)
            for bx,by in spots:
                if inb(bx,by) and grid[bx][by] in (EMPTY,AIR):
                    cg = make_genes(g, mg)
                    cg['hunger'] = 0; cg['thirst'] = 0
                    cg['knowledge'] = max(720, (g['knowledge'] + mg.get('knowledge',0)) // 2)
                    cg['blocks'] = 3   # children born with starter blocks
                    cg['mine_cd'] = 0
                    grid[bx][by]=HUMAN; gene[bx][by]=cg
                    data[bx][by]=0; life[bx][by]=random.choice([-1,1])
                    g['hunger'] += 100
                    break
            break

    # ── Age memories ─────────────────────────────────────────────────────────
    g['mem_age']  += 1;  g['mem_wage'] += 1
    if g['mem_age']  > 200: g['mem_fx']=-1;  g['mem_fy']=-1
    if g['mem_wage'] > 300: g['mem_wx']=-1;  g['mem_wy']=-1

    # ── Social exchange: knowledge, memories, tools, trading ─────────────────
    for ox,oy in [(-1,0),(1,0),(0,-1),(0,1),(-2,0),(2,0)]:
        nx2,ny2 = x+ox, y+oy
        if not inb(nx2,ny2) or grid[nx2][ny2] != HUMAN: continue
        ng = gene[nx2][ny2]
        if ng is None: continue
        # Knowledge transfer (always net upward)
        their_k = ng.get('knowledge', 0)
        if their_k > g['knowledge']:
            g['knowledge'] = min(1000, g['knowledge'] + (their_k - g['knowledge']) // 4 + 5)
        # Food memory
        if g['hunger'] > 60 and g['mem_fx'] < 0 and ng.get('mem_fx',-1) >= 0:
            if ng.get('mem_age',999) < 180:
                g['mem_fx']=ng['mem_fx']; g['mem_fy']=ng['mem_fy']; g['mem_age']=ng['mem_age']+3
        # Water memory
        if g['thirst'] > 60 and g['mem_wx'] < 0 and ng.get('mem_wx',-1) >= 0:
            if ng.get('mem_wage',999) < 250:
                g['mem_wx']=ng['mem_wx']; g['mem_wy']=ng['mem_wy']; g['mem_wage']=ng['mem_wage']+3
        # ── Economy: barter goods ───────────────────────────────────────────
        # If I'm hungry and they have food surplus, trade a valuable for food
        ng_inv = ng.get('inv', {})
        my_inv = g['inv']
        my_wealth   = sum(my_inv.get(k,0)*_TRADE_VALUE.get(
                          {'gold':GOLD,'copper':COPPER,'coal':COAL,'crystal':CRYSTAL}.get(k,GOLD),1)
                          for k in my_inv)
        their_food  = ng.get('hunger', 999)
        if g['hunger'] > 400 and my_wealth >= 5 and their_food < 200:
            # Pay gold for the neighbour's food surplus (they reduce my hunger)
            best_val = 0; pay_key = None
            for k,tv in [('gold',10),('copper',5),('crystal',8),('coal',2)]:
                if my_inv.get(k,0) > 0 and tv >= 5:
                    if tv > best_val: best_val=tv; pay_key=k
            if pay_key:
                my_inv[pay_key] = my_inv[pay_key] - 1
                ng_inv[pay_key] = ng_inv.get(pay_key,0) + 1
                g['hunger']  = max(0, g['hunger']  - 300)
                ng['hunger'] = min(1000, ng.get('hunger',0) + 80)
                ng['knowledge'] = min(1000, ng.get('knowledge',0) + 15)
                g['knowledge']  = min(1000, g['knowledge'] + 10)
        # Share a spare tool copy (if they have none of that type)
        for tool_name in ['spear','axe','pick','knife']:
            if g['tools'].get(tool_name,0) > 40 and ng.get('tools',{}).get(tool_name,0) == 0:
                g['tools'][tool_name] -= 20
                if 'tools' not in ng: ng['tools'] = {}
                ng['tools'][tool_name] = ng['tools'].get(tool_name,0) + 20
                g['knowledge'] = min(1000, g['knowledge'] + 20)
                break
        break  # one exchange per tick

    # ── Learn from panicking neighbours ──────────────────────────────────────
    g['fear_age'] += 1
    if g['fear_age'] > g['courage']: g['fear_dir'] = 0
    for ox,oy in [(-3,0),(-2,0),(-1,0),(1,0),(2,0),(3,0)]:
        nx2,ny2 = x+ox, y+oy
        if inb(nx2,ny2) and grid[nx2][ny2] in ANIMAL_TYPES and gene[nx2][ny2] is not None:
            if gene[nx2][ny2].get('panicked',0) > 0:
                g['fear_dir']=-gene[nx2][ny2].get('flee_dir',0); g['fear_age']=0; break

    # ── Goal state machine ────────────────────────────────────────────────────
    g['scan_cd'] = max(0, g['scan_cd']-1)
    if g['scan_cd'] == 0:
        g['scan_cd'] = 5 + random.randint(0,3)

        # P1 — flee threats immediately (scan all 8 directions, wide radius)
        fled = False
        nearest_threat_dist = 9999; flee_d_best = 1
        for px in range(x-12, x+13):
            if fled: break
            for py in range(y-5, y+6):
                if inb(px,py) and grid[px][py] in _HUMAN_THREAT:
                    dist = abs(px-x)+abs(py-y)
                    if dist < nearest_threat_dist:
                        nearest_threat_dist = dist
                        flee_d_best = 1 if x >= px else -1
                        fled = True
        if fled:
            # Rally: seek a direction with other humans for safety
            ally_counts = {1:0, -1:0}
            for ox2 in range(-8,9):
                for oy2 in range(-3,4):
                    if inb(x+ox2,y+oy2) and grid[x+ox2][y+oy2]==HUMAN:
                        ally_counts[1 if ox2>0 else -1] += 1
            # Prefer fleeing toward more allies if same threat distance
            if ally_counts[flee_d_best] < ally_counts[-flee_d_best] and nearest_threat_dist > 4:
                flee_d_best = -flee_d_best
            g['goal']='flee'
            g['tx']=max(0,min(COLS-1,x+flee_d_best*22)); g['ty']=y
            d=flee_d_best; life[x][y]=d
            g['panicked']=30; g['flee_dir']=flee_d_best; g['rev_ct']=0
        if not fled and g['goal']=='flee': g['goal']='idle'

        if g['goal'] != 'flee':
            g['idle_t'] += 1
            scan_r = 16 if (g['hunger']>400 or g['thirst']>300) else 11

            # P2 — drink if thirsty (score by distance, prefer shallow water)
            if g['thirst'] > 120 and g['goal'] != 'drink':
                best_score=-1; wbx=-1; wby=-1
                for fx in range(x-scan_r, x+scan_r+1):
                    for fy in range(y-scan_r, y+scan_r+1):
                        if not inb(fx,fy) or grid[fx][fy] not in _HUMAN_DRINK: continue
                        dist = abs(fx-x)+abs(fy-y)+1
                        # Prefer accessible water (not surrounded by deep water)
                        accessible = not (inb(fx,fy-1) and grid[fx][fy-1]==WATER)
                        score = (200 if accessible else 80) / dist
                        if score > best_score: best_score=score; wbx=fx; wby=fy
                if wbx >= 0:
                    g['goal']='drink'; g['tx']=wbx; g['ty']=wby
                    g['mem_wx']=wbx; g['mem_wy']=wby; g['mem_wage']=0; g['idle_t']=0
                elif g['mem_wx'] >= 0 and inb(g['mem_wx'],g['mem_wy']):
                    if grid[g['mem_wx']][g['mem_wy']] in _HUMAN_DRINK:
                        g['goal']='drink'; g['tx']=g['mem_wx']; g['ty']=g['mem_wy']; g['idle_t']=0
                    else:
                        g['mem_wx']=-1

            # P3 — forage/hunt: pick best value-per-distance food target
            elif g['hunger'] > 100 and g['goal'] not in ('forage','hunt','drink'):
                best_score=-1; bx=-1; by=-1
                for fx in range(x-scan_r, x+scan_r+1):
                    for fy in range(y-scan_r, y+scan_r+1):
                        if not inb(fx,fy): continue
                        cell = grid[fx][fy]
                        if cell in _HUMAN_FOOD:
                            val  = _FOOD_VALUE.get(cell, 120)
                            dist = abs(fx-x)+abs(fy-y)+1
                            score = val / dist
                            if score > best_score: best_score=score; bx=fx; by=fy
                        elif g['hunger'] > 350 and cell in _HUMAN_PREY:
                            dist = abs(fx-x)+abs(fy-y)+1
                            score = 300 / dist
                            if score > best_score: best_score=score; bx=fx; by=fy
                if bx >= 0:
                    g['goal']='forage' if grid[bx][by] in _HUMAN_FOOD else 'hunt'
                    g['tx']=bx; g['ty']=by
                    g['mem_fx']=bx; g['mem_fy']=by; g['mem_age']=0; g['idle_t']=0
                elif g['mem_fx'] >= 0 and inb(g['mem_fx'],g['mem_fy']):
                    if grid[g['mem_fx']][g['mem_fy']] in _HUMAN_FOOD:
                        g['goal']='forage'; g['tx']=g['mem_fx']; g['ty']=g['mem_fy']; g['idle_t']=0
                    else:
                        g['mem_fx']=-1

            # P4 — prospect for valuables when comfortable
            elif g['hunger'] < 300 and g['thirst'] < 200:
                my_wealth = sum(g['inv'].get(k,0) for k in ('gold','copper','crystal'))
                if my_wealth < 8:   # not yet wealthy enough
                    best_score=-1; pbx=-1; pby=-1
                    for fx in range(x-scan_r, x+scan_r+1):
                        for fy in range(y-scan_r, y+scan_r+1):
                            if not inb(fx,fy) or grid[fx][fy] not in _VALUABLES: continue
                            val = _TRADE_VALUE.get(grid[fx][fy], 2)
                            dist = abs(fx-x)+abs(fy-y)+1
                            score = val / dist
                            if score > best_score: best_score=score; pbx=fx; pby=fy
                    if pbx >= 0:
                        g['goal']='prospect'; g['tx']=pbx; g['ty']=pby; g['idle_t']=0

            # P5 — explore (bias toward unexplored territory)
            elif g['idle_t'] > 8:
                g['idle_t'] = 0
                # Bias exploration away from current direction to discover new areas
                explore_d = d if random.random() < 0.65 else -d
                step = 12 + random.randint(0, 16)
                g['tx'] = max(0, min(COLS-1, x+explore_d*step)); g['ty'] = y
                life[x][y] = explore_d

            # P5 — socialise: find nearest human and share knowledge
            elif g['hunger'] < 120 and g['thirst'] < 120:
                best_dist=9999; hx2=-1; hy2=-1
                for ox2 in range(-14, 15):
                    for oy2 in range(-6, 7):
                        nx2,ny2=x+ox2,y+oy2
                        if inb(nx2,ny2) and grid[nx2][ny2]==HUMAN and (nx2!=x or ny2!=y):
                            dist=abs(ox2)+abs(oy2)
                            if dist < best_dist: best_dist=dist; hx2=nx2; hy2=ny2
                if hx2 >= 0:
                    g['goal']='social'; g['tx']=hx2; g['ty']=hy2

    # ── Direction from active goal ────────────────────────────────────────────
    if g['goal'] in ('forage','hunt','social','flee','drink','prospect') and g['tx'] >= 0:
        tx,ty = g['tx'], g['ty']
        if inb(tx,ty):
            cell = grid[tx][ty]
            valid = ((g['goal']=='forage'   and cell in _HUMAN_FOOD) or
                     (g['goal']=='hunt'     and cell in _HUMAN_PREY) or
                     (g['goal']=='drink'    and cell in _HUMAN_DRINK) or
                     (g['goal']=='social'   and cell==HUMAN) or
                     (g['goal']=='prospect' and cell in _VALUABLES) or
                      g['goal']=='flee')
            if valid:
                d = 1 if tx>x else -1 if tx<x else d
            else:
                g['goal']='idle'; g['tx']=-1
        else:
            g['goal']='idle'; g['tx']=-1

    # ── Hazard avoidance (don't avoid water when goal is drink) ───────────────
    blocked = False
    if g['goal'] != 'flee':
        for dist in [1,2]:
            ax = x+d*dist
            if _is_hazard_at(ax,y): blocked=True; break
            if inb(ax,y) and grid[ax][y] in (EMPTY,AIR):
                for fall_y in range(y+1, min(ROWS,y+5)):
                    cell=grid[ax][fall_y] if inb(ax,fall_y) else STONE
                    if cell in HAZARDS or cell in LIQUIDS: blocked=True; break
                    if cell not in (EMPTY,AIR): break
        # Avoid deep water only when not seeking drink
        if g['goal'] != 'drink':
            if inb(x+d,y) and grid[x+d][y]==WATER:
                if inb(x+d,y-1) and grid[x+d][y-1]==WATER: blocked=True
        if g['fear_dir']==d and random.random()<0.55: blocked=True

    g['mine_cd'] = max(0, g['mine_cd'] - 1)
    if blocked:
        nx2 = x+d; climbed = False
        # Try to climb first
        for climb in [1,2,3]:
            if (inb(nx2,y-climb) and grid[nx2][y-climb] in (EMPTY,AIR) and
                    grid[nx2][y] not in HAZARDS and
                    all(grid[nx2][y-c] not in (EMPTY,AIR) for c in range(climb))):
                swap(x,y,nx2,y-climb); life[x][y]=d; climbed=True; break
        if not climbed:
            # Try mining the obstacle instead of turning around
            mined = False
            if g['mine_cd'] == 0:
                for my_off in [0, -1, -2]:   # try at eye level, one up, two up
                    mx2, my2 = nx2, y+my_off
                    if inb(mx2,my2) and grid[mx2][my2] in _MINEABLE:
                        grid[mx2][my2] = EMPTY
                        g['blocks'] = min(30, g['blocks'] + 1)
                        g['knowledge'] = min(1000, g['knowledge'] + 3)
                        g['mine_cd'] = 8
                        mined = True; break
            if not mined:
                d=-d; life[x][y]=d
                g['panicked']=8; g['flee_dir']=d; g['rev_ct']+=1
                if g['rev_ct'] > 5: g['goal']='idle'; g['tx']=-1; g['rev_ct']=0
    else:
        g['panicked'] = max(0, g.get('panicked',0)-1)
        g['rev_ct'] = 0

    # ── Gravity ───────────────────────────────────────────────────────────────
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR):
        swap(x,y,x,y+1); return

    # ── Move (fast!) ──────────────────────────────────────────────────────────
    speed = 0.97 if g['goal']=='flee' else 0.92 if g['goal'] in ('hunt','forage','drink') else 0.85
    if random.random() < speed:
        nx2 = x+d
        if inb(nx2,y) and grid[nx2][y] in (EMPTY,AIR) and _ground_under(nx2,y):
            swap(x,y,nx2,y); life[x][y]=d; return
        # Climb up to 4 blocks
        for climb in [1,2,3,4]:
            if (inb(nx2,y-climb) and grid[nx2][y-climb] in (EMPTY,AIR) and
                    grid[nx2][y] not in HAZARDS and
                    all(grid[nx2][y-c] not in (EMPTY,AIR) for c in range(climb))):
                swap(x,y,nx2,y-climb); life[x][y]=d; return
        life[x][y]=-d; g['goal']='idle'; g['tx']=-1

    # ── Build shelter when idle with blocks ───────────────────────────────────
    # A shelter is a roof (solid block 2-4 cells above) + walls on threatened side
    if g['blocks'] > 0 and g['goal'] == 'idle' and random.random() < 0.06:
        # 1. Build a roof overhead if exposed
        roof_needed = all(inb(x, y-ry) and grid[x][y-ry] in (EMPTY,AIR)
                          for ry in range(1, 5))
        if roof_needed:
            roof_y = y - 3   # 3 cells above head
            if inb(x, roof_y) and grid[x][roof_y] in (EMPTY,AIR):
                grid[x][roof_y] = _SHELTER_MAT
                g['blocks'] -= 1
        # 2. Build a wall on the side a threat approached from
        elif g['fear_dir'] != 0:
            wall_x = x + g['fear_dir']
            if inb(wall_x, y) and grid[wall_x][y] in (EMPTY,AIR):
                grid[wall_x][y] = _SHELTER_MAT
                g['blocks'] -= 1
        # 3. Fill a gap directly above (reinforce ceiling)
        elif g['blocks'] >= 3:
            for ry in range(1, 4):
                if inb(x, y-ry) and grid[x][y-ry] in (EMPTY,AIR):
                    # Only fill if something solid is above the gap (makes it a real ceiling)
                    if inb(x, y-ry-1) and grid[x][y-ry-1] not in (EMPTY,AIR,HUMAN):
                        grid[x][y-ry] = _SHELTER_MAT
                        g['blocks'] -= 1
                        break

    # ── Mine resources proactively when well-fed (gather materials) ───────────
    if g['blocks'] < 8 and g['hunger'] < 400 and g['thirst'] < 300 and g['mine_cd']==0:
        for ddx,ddy in [(-1,0),(1,0),(0,1),(0,-1)]:
            nx2,ny2 = x+ddx, y+ddy
            if inb(nx2,ny2) and grid[nx2][ny2] in _MINEABLE:
                grid[nx2][ny2] = EMPTY
                g['blocks'] = min(30, g['blocks'] + 1)
                g['mine_cd'] = 12; break

    # ── Plant a seed when well-fed and watered ────────────────────────────────
    if g['hunger'] < 150 and g['thirst'] < 150 and random.random() < 0.002:
        if inb(x,y+1) and grid[x][y+1] in (DIRT,WETDIRT,MUD):
            if inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR):
                grid[x][y-1] = SEED

# ── Tiger: fast aggressive land predator, ambush pounce ──────────────────────
def update_tiger(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    g.setdefault('carnivore', True); g.setdefault('pounce', 0)
    data[x][y]+=1
    if data[x][y]>8400: grid[x][y]=EMPTY; gene[x][y]=None; return
    d=life[x][y] if life[x][y]!=0 else random.choice([-1,1])
    # Avoid hazards (tigers are cautious about fire)
    for dist in [1,2]:
        if _is_hazard_at(x+d*dist,y): d=-d; life[x][y]=d; break
    # Gravity
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR):
        swap(x,y,x,y+1); return
    # Hunt in wider range (6 tiles), pounce 2 tiles when close
    prey_found=False
    for dx in range(-6,7):
        for dy in range(-2,3):
            nx,ny=x+dx,y+dy
            if not inb(nx,ny): continue
            if grid[nx][ny] in (ANIMAL,BIRD,HUMAN,FISH):
                mdx=1 if nx>x else -1 if nx<x else 0
                dist_x=abs(nx-x)
                # Pounce: move 2 tiles when within 3
                step=2 if dist_x<=3 and g['pounce']==0 else 1
                if step==2: g['pounce']=6
                tx,ty=x+mdx*step,y
                if not inb(tx,ty): tx=x+mdx; ty=y
                if inb(tx,ty) and grid[tx][ty] in (EMPTY,AIR) and not _is_hazard_at(tx,ty):
                    if tx==nx and ty==ny:
                        gene[nx][ny]=None; grid[nx][ny]=MEAT; life[nx][ny]=0; data[x][y]=max(0,data[x][y]-200)
                    else:
                        swap(x,y,tx,ty); life[x][y]=mdx if mdx!=0 else d
                    prey_found=True; break
        if prey_found: break
    g['pounce']=max(0,g['pounce']-1)
    if not prey_found and random.random()<0.65:
        nx=x+d
        if inb(nx,y) and grid[nx][y] in (EMPTY,AIR) and _ground_under(nx,y):
            swap(x,y,nx,y)
        elif inb(nx,y) and grid[nx][y] not in (EMPTY,AIR) and inb(nx,y-1) and grid[nx][y-1] in (EMPTY,AIR):
            swap(x,y,nx,y-1)
        else:
            life[x][y]=-d
    _try_breed(x, y, TIGER, 1200, 8400)

# ── Lion: social land predator, coordinates with nearby lions ─────────────────
def update_lion(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    g.setdefault('carnivore', True); g.setdefault('rally_dir', 0)
    data[x][y]+=1
    if data[x][y]>9600: grid[x][y]=EMPTY; gene[x][y]=None; return
    d=life[x][y] if life[x][y]!=0 else random.choice([-1,1])
    # Avoid hazards
    if _is_hazard_at(x+d,y): d=-d; life[x][y]=d
    # Gravity
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR):
        swap(x,y,x,y+1); return
    # Social coordination: align direction with nearby lions
    lions_near=0
    lion_dir_sum=0
    for ox in range(-5,6):
        for oy in range(-2,3):
            nx2,ny2=x+ox,y+oy
            if inb(nx2,ny2) and grid[nx2][ny2]==LION and (ox!=0 or oy!=0):
                lions_near+=1
                lion_dir_sum+=life[nx2][ny2]
    if lions_near>0 and random.random()<0.4:
        d=1 if lion_dir_sum>0 else -1 if lion_dir_sum<0 else d
        life[x][y]=d
    # Hunt, flanking with pack bonus
    prey_found=False
    hunt_range=5+lions_near  # wider hunt with more lions nearby
    for dx in range(-hunt_range,hunt_range+1):
        for dy in range(-2,3):
            nx,ny=x+dx,y+dy
            if not inb(nx,ny): continue
            if grid[nx][ny] in (ANIMAL,BIRD,HUMAN,FISH):
                mdx=1 if nx>x else -1 if nx<x else 0
                tx,ty=x+mdx,y
                if inb(tx,ty) and grid[tx][ty] in (EMPTY,AIR) and not _is_hazard_at(tx,ty):
                    if tx==nx and ty==ny:
                        gene[nx][ny]=None; grid[nx][ny]=MEAT; life[nx][ny]=0; data[x][y]=max(0,data[x][y]-180)
                    else:
                        swap(x,y,tx,ty); life[x][y]=mdx if mdx!=0 else d
                    prey_found=True; break
        if prey_found: break
    if not prey_found and random.random()<0.55:
        nx=x+d
        if inb(nx,y) and grid[nx][y] in (EMPTY,AIR) and _ground_under(nx,y):
            swap(x,y,nx,y)
        elif inb(nx,y) and grid[nx][y] not in (EMPTY,AIR) and inb(nx,y-1) and grid[nx][y-1] in (EMPTY,AIR):
            swap(x,y,nx,y-1)
        else:
            life[x][y]=-d
    _try_breed(x, y, LION, 1500, 9600)

# ── Whale: massive ocean creature, needs deep water, occasional breach ─────────
def update_whale(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    g.setdefault('breach_cd', 0)
    data[x][y]+=1
    if data[x][y]>18000: grid[x][y]=EMPTY; gene[x][y]=None; return
    in_water=inb(x,y) and grid[x][y] in (WATER,MUD)
    neighbors_water=sum(1 for dx,dy in [(-1,0),(1,0),(0,-1),(0,1),(0,2)]
                        if inb(x+dx,y+dy) and grid[x+dx][y+dy] in (WATER,MUD))
    if not in_water:
        # On surface / beached — slowly suffocate
        life[x][y]-=1
        if life[x][y]<=0: grid[x][y]=EMPTY; gene[x][y]=None; return
        # Fall / slide back to water
        if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR,WATER,MUD):
            swap(x,y,x,y+1); return
        for dx2 in [-1,1]:
            if inb(x+dx2,y) and grid[x+dx2][y] in (WATER,MUD):
                swap(x,y,x+dx2,y); return
        return
    life[x][y]=200  # reset breath
    g['breach_cd']=max(0,g['breach_cd']-1)
    # Breach: leap upward occasionally
    if g['breach_cd']==0 and random.random()<0.002:
        if inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR,WATER):
            swap(x,y,x,y-1); g['breach_cd']=120; return
    # Swim slowly, prefers deep water (needs ≥3 water neighbours)
    d=life[x][y]%2*2-1 if life[x][y]>1 else random.choice([-1,1])
    d=gene[x][y].get('swim_d',random.choice([-1,1]))
    if random.random()<0.35:
        for dx,dy in [(d,0),(0,1),(0,-1),(-d,0)]:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (WATER,MUD):
                nw=sum(1 for ox,oy in [(-1,0),(1,0),(0,-1),(0,1)]
                       if inb(nx+ox,ny+oy) and grid[nx+ox][ny+oy] in (WATER,MUD))
                if nw>=2:  # prefer staying in decent water depth
                    swap(x,y,nx,ny)
                    if abs(dx)==1: g['swim_d']=dx
                    return
        g['swim_d']=-d
    _try_breed(x, y, WHALE, 2500, 18000, spawn_in=(WATER, MUD))

# ── Dolphin: agile, can leap out of water briefly, playful swimmer ────────────
def update_dolphin(x,y):
    if apply_realistic_survival(x, y): return
    g=gene[x][y]
    if g is None: g=make_genes(); gene[x][y]=g
    g.setdefault('air_t', 0); g.setdefault('leap_cd', 0)
    data[x][y]+=1
    if data[x][y]>12000: grid[x][y]=EMPTY; gene[x][y]=None; return
    in_water=inb(x,y) and grid[x][y] in (WATER,MUD)
    g['leap_cd']=max(0,g['leap_cd']-1)
    if not in_water:
        g['air_t']+=1
        if g['air_t']>40: grid[x][y]=EMPTY; gene[x][y]=None; return  # drown in air too long
        # Arc back into water — fall with slight forward momentum
        d=life[x][y] if life[x][y]!=0 else 1
        if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR,WATER):
            swap(x,y,x,y+1); return
        if inb(x+d,y) and grid[x+d][y] in (EMPTY,AIR,WATER):
            swap(x,y,x+d,y); return
        return
    g['air_t']=0
    # Eat fish / jellyfish nearby
    for dx,dy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx,ny=x+dx,y+dy
        if inb(nx,ny) and grid[nx][ny] in (FISH,JELLYFISH) and random.random()<0.05:
            grid[nx][ny]=WATER; data[x][y]=max(0,data[x][y]-80)
    # Leap out of water
    if g['leap_cd']==0 and random.random()<0.008:
        if inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR):
            swap(x,y,x,y-1); g['leap_cd']=30; return
    # Fast swimming, direction changes more often
    d=life[x][y] if life[x][y]!=0 else random.choice([-1,1])
    if random.random()<0.7:
        for dx,dy in [(d,0),(d,-1),(0,-1),(0,1),(-d,0)]:
            nx,ny=x+dx,y+dy
            if inb(nx,ny) and grid[nx][ny] in (WATER,MUD):
                swap(x,y,nx,ny)
                if abs(dx)==1: life[x][y]=dx
                return
        life[x][y]=-d
    _try_breed(x, y, DOLPHIN, 1500, 12000, spawn_in=(WATER, MUD))

# ── Shared physics helpers ────────────────────────────────────────────────────
def fall_powder(x, y):
    if inb(x,y+1) and can_powder_fall(grid[x][y+1]): swap(x,y,x,y+1); return
    dx=random.choice([-1,1])
    if inb(x+dx,y+1) and can_powder_fall(grid[x+dx][y+1]): swap(x,y,x+dx,y+1)

def fall_liquid(x, y):
    if inb(x,y+1) and grid[x][y+1] in (EMPTY,AIR): swap(x,y,x,y+1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y+1) and grid[x+dx][y+1] in (EMPTY,AIR): swap(x,y,x+dx,y+1); return
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

def fall_gas(x, y):
    if inb(x,y-1) and grid[x][y-1] in (EMPTY,AIR): swap(x,y,x,y-1); return
    dirs=[-1,1]; random.shuffle(dirs)
    for dx in dirs:
        if inb(x+dx,y) and grid[x+dx][y] in (EMPTY,AIR): swap(x,y,x+dx,y); return

# ── 15 New Features Implementations ───────────────────────────────────────────
def bleed_animal(x, y):
    pass  # no visual effect needed

def apply_realistic_survival(x, y) -> bool:
    '''Returns True if animal died.'''
    g = gene[x][y]
    if g is None: return False
    g.setdefault('oxygen', 100)
    g.setdefault('fall_speed', 0.0)
    g.setdefault('hp', 100)
    
    # 1. Oxygen/Drowning: lose oxygen if in water/mud and not fish/frog
    in_water = inb(x, y) and grid[x][y] in [WATER, MUD]
    is_aquatic = grid[x][y] in [FISH, WHALE, DOLPHIN, FROG]
    if in_water and not is_aquatic:
        if random.random() < 0.2: g['oxygen'] -= 1   # drowns in ~8 sec instead of 1.7
        if random.random() < 0.1 and inb(x, y-1) and grid[x][y-1]==WATER:
            grid[x][y-1] = BUBBLE
    else:
        g['oxygen'] = min(100, g['oxygen']+5)
    
    if g['oxygen'] <= 0:
        grid[x][y] = MEAT
        gene[x][y] = None
        return True
        
    # 2. Hazards damage (Fire, Acid, Lava)
    if grid[x][y] in HAZARDS or (inb(x, y+1) and grid[x][y+1] in HAZARDS):
        g['hp'] -= 10
        bleed_animal(x, y)
        if g['hp'] <= 0:
            grid[x][y] = ASH if grid[x][y] in [FIRE, LAVA] else MEAT
            gene[x][y] = None
            return True
            
    # 3. Fall damage tracking
    if inb(x, y+1) and grid[x][y+1] in [EMPTY, AIR]:
        g['fall_speed'] += 1.0
    elif g['fall_speed'] > 15: # hit ground hard
        g['hp'] -= g['fall_speed'] * 2
        g['fall_speed'] = 0.0
        bleed_animal(x, y)
        if g['hp'] <= 0:
            grid[x][y] = MEAT
            gene[x][y] = None
            return True
    else:
        g['fall_speed'] = 0.0
        
    return False

def update_bear(x, y):
    if apply_realistic_survival(x, y): return
    g = gene[x][y]
    if g is None: g = make_genes(); gene[x][y] = g
    data[x][y] += 1
    # Sleep in freezing temp
    if temp_g[x][y] < -5:
        if inb(x, y+1) and grid[x][y+1] in [EMPTY, AIR]: swap(x, y, x, y+1)
        return
    d = life[x][y] if life[x][y] != 0 else random.choice([-1, 1])
    # Hunt Fish, Meat, Honey
    prey = False
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            nx, ny = x+dx, y+dy
            if inb(nx, ny) and grid[nx][ny] in [FISH, MEAT, HONEY, HUMAN]:
                if random.random() < 0.5:
                    swap(x,y, nx,ny)
                    if grid[x][y] != BEAR: grid[x][y] = EMPTY
                prey = True
                break
        if prey: break
    if not prey:
        update_animal(x, y)
    if grid[x][y] == BEAR:
        _try_breed(x, y, BEAR, 1000, 12000)

def update_snake(x, y):
    if apply_realistic_survival(x, y): return
    if random.random() < 0.6: # fast
        update_animal(x, y)
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        nx, ny = x+dx, y+dy
        if inb(nx, ny) and grid[nx][ny] in [HUMAN, RABBIT, BIRD]:
            grid[nx][ny] = POISON
            updated[nx][ny] = True
    if grid[x][y] == SNAKE:
        _try_breed(x, y, SNAKE, 400, 5000)

def update_rabbit(x, y):
    if apply_realistic_survival(x, y): return
    # Flee easily
    for dx in range(-3, 4):
        for dy in range(-3, 4):
            nx, ny = x+dx, y+dy
            if inb(nx, ny) and grid[nx][ny] in [PREDATOR, TIGER, LION, SNAKE, BEAR]:
                life[x][y] = 1 if x > nx else -1
                update_animal(x, y)
                return
    if random.random() < 0.05 and inb(x, y-1) and grid[x][y-1] in [EMPTY, AIR]:
        swap(x,y, x,y-1) # hop
    update_animal(x, y)
    if grid[x][y] == RABBIT:
        _try_breed(x, y, RABBIT, 200, 4000, chance=0.002)  # rabbits breed quickly

def update_spider(x, y):
    if apply_realistic_survival(x, y): return
    # Climb walls
    for dx in [-1, 1]:
        if inb(x+dx, y) and grid[x+dx][y] in STATIC_SOLIDS:
            if inb(x, y-1) and grid[x][y-1] == EMPTY and random.random() < 0.5:
                swap(x,y, x,y-1)
                if random.random() < 0.1 and inb(x, y+1): grid[x][y+1] = WEB
                return
    update_animal(x, y)

def update_bee(x, y):
    if apply_realistic_survival(x, y): return
    d = life[x][y] if life[x][y] != 0 else random.choice([-1, 1])
    if random.random() < 0.8:
        nx, ny = x+random.choice([-1,1,0]), y+random.choice([-1,1,0])
        if inb(nx, ny) and grid[nx][ny] == EMPTY:
            swap(x,y, nx,ny)
    # Pollinate / Honey
    for dx in range(-2, 3):
        for dy in range(-2, 3):
            nx, ny = x+dx, y+dy
            if inb(nx, ny) and grid[nx][ny] in [PLANT, VINE]:
                if random.random() < 0.05 and inb(x, y+1) and grid[x][y+1] == EMPTY:
                    grid[x][y+1] = HONEY
                break

def update_frog(x, y):
    if apply_realistic_survival(x, y): return
    if random.random() < 0.05:
        dx = random.choice([-1, 1, -2, 2])
        dy = random.randint(-4, -1)
        if inb(x+dx, y+dy) and grid[x+dx][y+dy] == EMPTY:
            swap(x,y, x+dx, y+dy)
            return
    # Eats buzzy things
    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
        if inb(x+dx, y+dy) and grid[x+dx][y+dy] == BEE:
            grid[x+dx][y+dy] = EMPTY
    if inb(x, y+1) and grid[x][y+1] in [EMPTY, AIR]:
        swap(x,y, x,y+1)
    if grid[x][y] == FROG:
        _try_breed(x, y, FROG, 300, 4000, spawn_in=(EMPTY, AIR, WATER))

def update_web(x, y):
    if random.random() < 0.01: # highly flammable
        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
            nx, ny = x+dx, y+dy
            if inb(nx, ny) and grid[nx][ny] == FIRE:
                grid[x][y] = FIRE
                return

# ── Food element update functions ─────────────────────────────────────────────
def update_mushroom(x, y):
    life[x][y] += 1
    if life[x][y] > 1800: grid[x][y] = EMPTY; return  # rots
    fall_powder(x, y)
    # Spreads near fungus
    if random.random() < 0.0003:
        for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx2, ny2 = x+ddx, y+ddy
            if inb(nx2, ny2) and grid[nx2][ny2] == FUNGUS:
                if inb(nx2, ny2-1) and grid[nx2][ny2-1] in (EMPTY, AIR):
                    grid[nx2][ny2-1] = MUSHROOM; life[nx2][ny2-1] = 0; break

def update_corn(x, y):
    life[x][y] += 1
    if life[x][y] > 2500: grid[x][y] = EMPTY; return
    fall_powder(x, y)

def update_carrot(x, y):
    life[x][y] += 1
    if life[x][y] > 2000: grid[x][y] = EMPTY; return
    fall_powder(x, y)

def update_cooked_meat(x, y):
    life[x][y] += 1
    if life[x][y] > 1200: grid[x][y] = ASH; return  # burns to ash eventually
    fall_powder(x, y)
    for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx2, ny2 = x+ddx, y+ddy
        if inb(nx2, ny2) and grid[nx2][ny2] in (FIRE, LAVA) and random.random() < 0.04:
            grid[x][y] = FIRE; life[x][y] = random.randint(30, 60); return

def update_dough(x, y):
    fall_powder(x, y)
    for ddx, ddy in [(-1,0),(1,0),(0,-1),(0,1)]:
        nx2, ny2 = x+ddx, y+ddy
        if inb(nx2, ny2):
            if grid[nx2][ny2] in (FIRE, EMBER) and random.random() < 0.06:
                grid[x][y] = BREAD; return
            if grid[nx2][ny2] in (LAVA, MAGMA) and random.random() < 0.10:
                grid[x][y] = FIRE; life[x][y] = random.randint(40, 80); return

# ── Crafting knowledge system ─────────────────────────────────────────────────
# Recipes: frozenset of two input element IDs -> output element ID
_CRAFT_RECIPES = {
    frozenset({WHEAT, WATER}): DOUGH,
    frozenset({DOUGH, EMBER}): BREAD,
    frozenset({MEAT, EMBER}): COOKED_MEAT,
    frozenset({MEAT, FIRE}): COOKED_MEAT,
    frozenset({SEED, FUNGUS}): MUSHROOM,
    frozenset({SAND, STONE}): SANDSTONE,
    frozenset({CLAY, WATER}): MUD,
}

# Dispatch table ────────────────────────────────────────────────────────────
UPDATE_FN = {
    FIRE:update_fire, EMBER:update_ember, SMOKE:update_smoke, STEAM:update_steam,
    WATER:update_water, LAVA:update_lava, MAGMA:update_magma, SAND:update_sand,
    SNOW:update_snow, ICE:update_ice, OIL:update_oil, ACID:update_acid,
    GUNPOWDER:update_gunpowder, CLOUD:update_cloud, ASH:update_ash, SALT:update_salt,
    DIRT:update_dirt, WETDIRT:update_wetdirt, MUD:update_mud, MERCURY:update_mercury,
    HONEY:update_honey, SLIME:update_slime, TAR:update_tar, POISON:update_poison,
    SEED:update_seed, SAPLING:update_sapling, VINE:update_vine, MOSS:update_moss,
    FUNGUS:update_fungus, SPORE:update_spore, GRAVEL:update_gravel, CLAY:update_clay,
    RESIN:update_resin, WAX:update_wax, PEAT:update_peat, SEAWEED:update_seaweed,
    JELLYFISH:update_jellyfish, BUBBLE:update_bubble, PLASMA:update_plasma,
    NEON:update_neon, LIGHTNING:update_lightning_bolt, CHARGED:update_charged,
    PRESSGAS:update_pressgas, AIR:update_air_cell, CHARCOAL:update_charcoal,
    RUST:update_rust, SANDSTONE:update_sandstone, PLANT:update_plant,
    LEAF:update_leaf, ANIMAL:update_animal,
    METHANE:update_methane, NITRO:update_nitro, QUICKSAND:update_quicksand,
    STEEL:update_steel, SUGAR:update_sugar, URANIUM:update_uranium, VOID:update_void,
    HYDROGEN:update_hydrogen, SULFUR:update_sulfur, HELIUM:update_helium,
    COAL:update_coal, COPPER:update_copper,
    WHEAT:update_wheat, APPLE:update_apple, BERRY:update_berry,
    BREAD:update_bread, MEAT:update_meat,
    BIRD:update_bird, FISH:update_fish, PREDATOR:update_predator, HUMAN:update_human,
    TIGER:update_tiger, LION:update_lion, WHALE:update_whale, DOLPHIN:update_dolphin,
    BEAR:update_bear, SNAKE:update_snake, RABBIT:update_rabbit, SPIDER:update_spider,
    BEE:update_bee, FROG:update_frog, WEB:update_web,
    MUSHROOM:update_mushroom, CORN:update_corn, CARROT:update_carrot,
    COOKED_MEAT:update_cooked_meat, DOUGH:update_dough,
}

# ── Main grid update ──────────────────────────────────────────────────────────
def update_grid():
    global storm_t,storming,raining,ltng_t,blizzard,blizzard_t
    global snowing,tornado_on,wind_x,fog_on,fog_t,heatwave,heatwave_t,acid_rain,acidrain_t

    for x in range(COLS):
        for y in range(ROWS): updated[x][y]=False

    if storming:
        storm_t-=1
        if storm_t<=0: storming=raining=False
        else:
            for _ in range(14):
                rx=int((random.randint(0,COLS-1)-wind_x*2)%COLS)
                if grid[rx][0]==EMPTY: grid[rx][0]=WATER; temp_g[rx][0]=max(temperature,8.0)
            ltng_t-=1
            if ltng_t<=0: spawn_lightning(random.randint(10,COLS-10)); ltng_t=random.randint(18,70)
    elif raining:
        for _ in range(6):
            rx=int((random.randint(0,COLS-1)-wind_x)%COLS)
            if grid[rx][0]==EMPTY: grid[rx][0]=WATER; temp_g[rx][0]=max(temperature,10.0)

    if snowing:
        for _ in range(9 if blizzard else 4):
            rx=int((random.randint(0,COLS-1)-wind_x*2)%COLS)
            if grid[rx][0]==EMPTY: grid[rx][0]=SNOW; temp_g[rx][0]=min(temperature,-2.0)

    if blizzard:
        blizzard_t-=1
        if blizzard_t<=0: blizzard=snowing=False; wind_x=0.0

    if acid_rain:
        acidrain_t-=1
        if acidrain_t<=0: acid_rain=False
        else:
            for _ in range(5):
                rx=int((random.randint(0,COLS-1)-wind_x)%COLS)
                if grid[rx][0]==EMPTY: grid[rx][0]=ACID; life[rx][0]=random.randint(100,200)

    if fog_on:
        fog_t-=1
        if fog_t<=0: fog_on=False
        elif random.random()<0.3:
            fx=random.randint(0,COLS-1); fy=random.randint(ROWS//2,ROWS-1)
            if grid[fx][fy]==EMPTY: grid[fx][fy]=SMOKE; life[fx][fy]=random.randint(300,800)

    if heatwave:
        heatwave_t-=1
        if heatwave_t<=0: heatwave=False
        else:
            for _ in range(80):
                x=random.randint(0,COLS-1); y=random.randint(0,ROWS-1)
                temp_g[x][y]=min(temp_g[x][y]+0.6, temperature+55)

    update_tornado(); diffuse_heat(); update_oxygen()

    for y in range(ROWS-1,-1,-1):
        d=1 if y%2==0 else -1
        xs=0 if d==1 else COLS-1; xe=COLS if d==1 else -1
        for x in range(xs,xe,d):
            if updated[x][y]: continue
            el=grid[x][y]
            if el==EMPTY or el in STATIC_SOLIDS: continue
            fn=UPDATE_FN.get(el)
            if fn: fn(x,y)

# ── Per-pixel colour computation ──────────────────────────────────────────────
# Pre-compute per-cell stable noise (spatial hash → [-1,1])
def stable_noise(x, y):
    s = noise_seed[x][y]
    return (s / 32767.5) - 1.0   # range -1 to 1

def cell_color(x, y, el, t):
    """Return (r,g,b) with rich per-pixel visual effects."""
    base = COLORS.get(el, hx('#ff00ff'))
    ns   = stable_noise(x, y)        # static cell noise  -1..1
    tf   = frame_t                    # global animation tick

    # ── FIRE — multi-layer hot core + orange mantle + flicker ────────────────
    if el == FIRE:
        age     = life[x][y] / 220.0
        oxygen  = oxy[x][y]
        flicker = math.sin(tf*0.15 + x*0.7 + y*0.4 + ns*3) * 0.5 + 0.5
        heat    = min(1.0, temp_g[x][y] / 900.0)
        # Core: white → yellow → orange → red
        core_t  = max(0.0, min(1.0, flicker * heat * oxygen))
        if core_t > 0.75:
            r,g,b = 255, 245, int(200*(core_t-0.75)*4)
        elif core_t > 0.5:
            r,g,b = 255, int(180*(core_t-0.5)*4), 0
        elif core_t > 0.25:
            r,g,b = 240, int(80+60*core_t), 0
        else:
            r,g,b = int(180+40*core_t), int(30+40*core_t), 0
        # Darken edges and dying fire
        fade = max(0.3, age) * oxygen
        return cc(r*fade, g*fade, b*fade)

    # ── LAVA — pulsing orange glow with cooler crust patches ─────────────────
    elif el == LAVA:
        pulse = (math.sin(tf*0.018 + x*0.3 + y*0.5) + 1) * 0.5
        heat  = min(1.0, temp_g[x][y] / 1200.0)
        crust = (ns + 1) * 0.5     # 0..1, static variation
        if crust < 0.3:             # crust patch
            c = blend(hx('#301010'), hx('#601808'), pulse)
        else:                       # molten
            hot = blend(hx('#ff6000'), hx('#ffd000'), pulse * heat)
            c   = blend(hx('#c03000'), hot, heat * 0.8)
        return c

    # ── WATER — depth shading + animated surface shimmer ─────────────────────
    elif el == WATER:
        # Depth: check if open above → surface, else deeper blue
        surface = not inb(x, y-1) or grid[x][y-1] in (EMPTY, AIR, STEAM, CLOUD)
        wave   = math.sin(tf*0.025 + x*0.4 + ns*2) * 0.5 + 0.5
        depth_t = min(1.0, data[x][y] / 20.0 + abs(ns)*0.3)
        if surface:
            c = blend(hx('#3090f0'), hx('#80c8ff'), wave * 0.6)
            # Foam fleck on surface
            if wave > 0.85 and (x + y) % 7 == 0:
                c = blend(c, hx('#ddf4ff'), 0.5)
        else:
            c = blend(hx('#0a4898'), hx('#1460c0'), wave * 0.3)
        if temp_g[x][y] < 5:        # cold water tint
            c = blend(c, hx('#a0d0f8'), 0.25)
        return c

    # ── ICE — crystalline facets ──────────────────────────────────────────────
    elif el == ICE:
        facet = (math.cos(x*0.8+ns) * math.sin(y*0.8)) * 0.5 + 0.5
        c = blend(hx('#80c8f0'), hx('#e8f8ff'), facet)
        # Refraction shimmer
        if (x+y)%5 == 0: c = lighten(c, 30)
        return c

    # ── MAGMA — darker, denser than lava ─────────────────────────────────────
    elif el == MAGMA:
        pulse = (math.sin(tf*0.012 + x*0.5 + y*0.3 + ns) + 1) * 0.5
        return blend(hx('#780000'), hx('#e03000'), pulse * min(1.0, temp_g[x][y]/1400.0))

    # ── SAND — granular variation with warm/cold hues ────────────────────────
    elif el == SAND:
        grain = ns * 22
        wet   = 1.0 if any(inb(x+dx,y+dy) and grid[x+dx][y+dy] in (WATER,MUD) for dx,dy in [(-1,0),(1,0),(0,1)]) else 0.0
        c = cc(0xd4+grain, 0xa9+grain//2, 0x6a-grain//3)
        if wet > 0: c = blend(c, hx('#a07840'), 0.4)
        return c

    # ── STEAM — wispy semi-transparent ───────────────────────────────────────
    elif el == STEAM:
        alpha = min(1.0, life[x][y] / 120.0)
        wave  = math.sin(tf*0.03 + x*0.5 + ns) * 0.5 + 0.5
        c = blend(hx('#8090a0'), hx('#d8e0f0'), wave)
        return blend(COLORS[EMPTY], c, alpha * 0.7 + 0.3)

    # ── SMOKE — dark wispy + density fade ────────────────────────────────────
    elif el == SMOKE:
        fade = max(0.1, min(1.0, life[x][y] / 120.0))
        v = int(0x30 + ns*20 + (1-fade)*40)
        return cc(v, v, v+8)

    # ── SNOW — sparkle variation ──────────────────────────────────────────────
    elif el == SNOW:
        sparkle = 1.0 if (frame_t//4 + x*3 + y*7) % 31 == 0 else 0.0
        v = int(0xe8 + ns*12)
        c = cc(v, v+4, v+12)
        if sparkle: c = hx('#ffffff')
        return c

    # ── OBSIDIAN — glassy dark with purple sheen ─────────────────────────────
    elif el == OBSIDIAN:
        sheen = max(0.0, math.cos((x+y)*0.4 + ns*2)) * 0.35
        c = blend(hx('#18102a'), hx('#5030a0'), sheen)
        if (x*3+y*7)%17==0: c = lighten(c, 20)
        return c

    # ── GOLD — metallic shimmer ───────────────────────────────────────────────
    elif el == GOLD:
        shine = (math.sin(tf*0.01 + x*0.8 + ns*2) + 1) * 0.5
        return blend(hx('#c88000'), hx('#ffe060'), shine * 0.7 + 0.15)

    # ── MERCURY — liquid metal reflection ────────────────────────────────────
    elif el == MERCURY:
        ref = (math.sin(tf*0.02 + x*1.2 + ns*3) + 1) * 0.5
        return blend(hx('#6080a0'), hx('#d0e0f8'), ref * 0.7 + 0.2)

    # ── CRYSTAL — prismatic ───────────────────────────────────────────────────
    elif el == CRYSTAL:
        prism = (math.sin(x*0.6+ns+tf*0.005) + 1) * 0.5
        r_c = blend(hx('#60b8f0'), hx('#e0f8ff'), prism)
        if (x+y)%4==0: r_c = lighten(r_c, 40)
        return r_c

    # ── GLASS — transparent blue-grey with edge highlight ────────────────────
    elif el == GLASS:
        edge = 1.0 if (not inb(x-1,y) or grid[x-1][y]==EMPTY or not inb(x+1,y) or grid[x+1][y]==EMPTY) else 0.0
        c = hx('#90c0d8')
        if edge: c = lighten(c, 35)
        return c

    # ── PLANT / GRASS — varied green health ──────────────────────────────────
    elif el == PLANT:
        health = 1.0 if is_day else 0.7
        v = int(ns*15)
        return cc(0x10+v, int(0x80*health)+v, 0x10+v//2)

    # ── LEAF — autumn tint when old ──────────────────────────────────────────
    elif el == LEAF:
        age_frac = min(1.0, life[x][y] / 2000.0)
        spring = hx('#187030')
        autumn = hx('#c07010')
        c = blend(spring, autumn, age_frac * 0.8)
        v = int(ns*12)
        return cc(c[0]+v, c[1]+v//2, c[2])

    # ── EMBER — hot spark ────────────────────────────────────────────────────
    elif el == EMBER:
        glow = min(1.0, life[x][y]/120.0)
        pulse = (math.sin(tf*0.2 + x + y + ns*4) + 1) * 0.5
        return blend(hx('#c04000'), hx('#ffcc00'), glow * pulse)

    # ── PLASMA — electric purple-white ───────────────────────────────────────
    elif el == PLASMA:
        arc = (math.sin(tf*0.04+x*2+y+ns*5)+1)*0.5
        return blend(hx('#8000d0'), hx('#ffffff'), arc*0.7+0.2)

    # ── NEON — electric colour shift ─────────────────────────────────────────
    elif el == NEON:
        hue_t = (tf*0.008 + ns) % 1.0
        # Cycle through purple → cyan → pink
        if hue_t < 0.33: c = blend(hx('#c000ff'), hx('#00ffcc'), hue_t*3)
        elif hue_t < 0.66: c = blend(hx('#00ffcc'), hx('#ff00a0'), (hue_t-0.33)*3)
        else: c = blend(hx('#ff00a0'), hx('#c000ff'), (hue_t-0.66)*3)
        return c

    # ── LIGHTNING — white-yellow flash ───────────────────────────────────────
    elif el == LIGHTNING:
        return hx('#ffffff') if frame_t%2==0 else hx('#ffffaa')

    # ── CHARGED wire ─────────────────────────────────────────────────────────
    elif el == CHARGED:
        spark = (math.sin(tf*0.3 + x*3 + ns*8) + 1) * 0.5
        return blend(hx('#a06000'), hx('#ffff00'), spark)

    # ── ACID — bubbling toxic green ───────────────────────────────────────────
    elif el == ACID:
        bubble_t = (tf*0.05 + x*0.7 + y*0.3) % (2*math.pi)
        bubble   = (math.sin(bubble_t) + 1) * 0.5
        return blend(hx('#20a008'), hx('#90ff30'), bubble * 0.6 + 0.2)

    # ── OIL — dark with iridescent surface sheen ─────────────────────────────
    elif el == OIL:
        surface = not inb(x,y-1) or grid[x][y-1] in (EMPTY,AIR)
        if surface:
            sheen_t = (x*0.3 + tf*0.004 + ns) % 1.0
            if sheen_t < 0.33: return blend(hx('#1a1408'), hx('#3050a0'), 0.3)
            elif sheen_t < 0.66: return blend(hx('#1a1408'), hx('#308020'), 0.25)
            else: return blend(hx('#1a1408'), hx('#802080'), 0.2)
        return hx('#120e04')

    # ── ANIMAL — age & trait colouring ───────────────────────────────────────
    elif el == ANIMAL:
        g = gene[x][y]
        if g:
            r,gv,b = g['color_r'],g['color_g'],g['color_b']
            if g.get('carnivore'): r=min(255,r+50)
            if g.get('flying'):    b=min(255,b+50)
            if g.get('amphibious'):gv=min(255,gv+50)
            af = 1.0 - min(0.35, data[x][y]/max(1,g['lifespan']))
            breathe = (math.sin(tf*0.06+ns*4)+1)*0.5*0.12
            return cc(r*af+breathe*30, gv*af, b*af)
        return base

    # ── WOOD — grain lines ───────────────────────────────────────────────────
    elif el == WOOD:
        grain = math.sin(x*0.25 + ns*2) * 0.5 + 0.5
        return blend(hx('#3a1c0a'), hx('#6e3818'), grain * 0.6 + 0.2)

    # ── STONE — varied grey ───────────────────────────────────────────────────
    elif el == STONE:
        v = int(ns * 18)
        return cc(0x60+v, 0x62+v, 0x68+v)

    # ── DIRT ─────────────────────────────────────────────────────────────────
    elif el == DIRT:
        v = int(ns*14)
        return cc(0x42+v, 0x26+v//2, 0x08)

    # ── WETDIRT ──────────────────────────────────────────────────────────────
    elif el == WETDIRT:
        return cc(0x25+int(ns*8), 0x12, 0x04)

    # ── MUD — ripple ─────────────────────────────────────────────────────────
    elif el == MUD:
        rip = (math.sin(tf*0.01 + x*0.5 + ns) + 1) * 0.5 * 0.15
        return blend(hx('#3c2010'), hx('#6a4020'), rip + 0.2)

    # ── ASH — subtle texture ──────────────────────────────────────────────────
    elif el == ASH:
        v = int(ns*16)
        return cc(0x78+v, 0x74+v, 0x70+v)

    # ── CLOUD ─────────────────────────────────────────────────────────────────
    elif el == CLOUD:
        edge = (math.sin(tf*0.006+x*0.5+ns*2)+1)*0.5
        return blend(hx('#9090a0'), hx('#e8eaf8'), edge*0.8+0.1)

    # ── CONCRETE / CEMENT ────────────────────────────────────────────────────
    elif el in (CONCRETE, CEMENT):
        v = int(ns * 12)
        base_col = (0x80, 0x7c, 0x78) if el==CONCRETE else (0xa0, 0x98, 0x90)
        return cc(base_col[0]+v, base_col[1]+v, base_col[2]+v)

    # ── HONEY — thick amber ───────────────────────────────────────────────────
    elif el == HONEY:
        drip = (math.sin(tf*0.008+x*0.6+ns)+1)*0.5
        return blend(hx('#804000'), hx('#ffb000'), drip*0.7+0.2)

    # ── SLIME ─────────────────────────────────────────────────────────────────
    elif el == SLIME:
        pulse = (math.sin(tf*0.02+x*0.4+y*0.3+ns*2)+1)*0.5
        return blend(hx('#184818'), hx('#50d050'), pulse*0.6+0.2)

    # ── TAR ──────────────────────────────────────────────────────────────────
    elif el == TAR:
        if temp_g[x][y] > 50:
            shine = (math.sin(tf*0.03+x+ns*3)+1)*0.5*0.2
            return blend(hx('#0c0800'), hx('#302010'), shine)
        return hx('#0c0800')

    # ── GRAVEL / BASALT ──────────────────────────────────────────────────────
    elif el == GRAVEL:
        v = int(ns*22)
        return cc(0x60+v, 0x58+v, 0x52+v)

    elif el == BASALT:
        v = int(ns*10)
        return cc(0x28+v, 0x22+v, 0x2c+v)

    # ── GENERIC fallback — stable noise variation ─────────────────────────────
    else:
        v = int(ns*14)
        return cc(base[0]+v, base[1]+v//2, base[2]+v//3)

# ── Animal sprite overlay (drawn on screen in screen-space after blit) ────────
def draw_animal_sprites():
    """Pixel-art detail overlays for each animal cell (drawn over scaled grid)."""
    C  = int(CELL * zoom_level)
    if C < 1: C = 1
    H  = max(1, C // 2)
    g  = np.asarray(grid, dtype=np.intp)

    for etype in ANIMAL_TYPES:
        positions = np.argwhere(g == etype)
        if len(positions) == 0:
            continue
        for cx, cy in positions:
            sx = int(cx * CELL * zoom_level) + cam_offset_x
            sy = int(cy * CELL * zoom_level) + cam_offset_y
            d  = life[cx][cy]   # -1 (left) or 1 (right)

            if etype == BIRD:
                # White wing row, orange beak pixel on facing side, dark eye
                wc = (255, 248, 210) if (frame_t // 7) % 2 == 0 else (210, 195, 140)
                pygame.draw.rect(screen, wc, (sx, sy, C, H))            # wing flash top
                beak_x = sx + (C - 1) if d >= 0 else sx
                pygame.draw.rect(screen, (255, 110, 20), (beak_x, sy + H, 1, 1))  # beak
                pygame.draw.rect(screen, (15, 10, 5),   (sx + H, sy + H, 1, 1))   # eye

            elif etype == FISH:
                tail_x = sx if d >= 0 else sx + C - 1
                pygame.draw.rect(screen, (20, 55, 130),  (tail_x, sy, 1, C))        # tail fin
                pygame.draw.rect(screen, (130, 200, 255),(sx + H, sy, 1, H))        # dorsal fin
                eye_x = sx + (C - 2) if d >= 0 else sx + 1
                pygame.draw.rect(screen, (5, 5, 5),      (eye_x, sy + H, 1, 1))    # eye

            elif etype == HUMAN:
                # Draw human at 2× cell size, extending 1 cell above and to sides
                S  = C * 2          # sprite size
                ox = sx - C // 2    # center horizontally
                oy = sy - C         # extend one cell up
                hw = max(2, S // 3) # head width
                # Head (skin tone)
                pygame.draw.rect(screen, (240, 200, 155), (ox + S // 4, oy, hw, S // 3))
                # Hair
                pygame.draw.rect(screen, (60, 35, 10),   (ox + S // 4, oy, hw, max(1, S // 8)))
                # Torso / shirt
                pygame.draw.rect(screen, (55, 80, 170),  (ox + S // 6, oy + S // 3, S * 2 // 3, S // 3))
                # Legs — alternate pixels up/down for walk animation
                anim = (frame_t // 5) % 2
                lw   = max(1, S // 5)
                lx   = ox + S // 6
                rx   = ox + S // 6 + S // 3
                pygame.draw.rect(screen, (40, 55, 90), (lx, oy + S * 2 // 3, lw, S // 4 + anim))
                pygame.draw.rect(screen, (40, 55, 90), (rx, oy + S * 2 // 3, lw, S // 4 + (1 - anim)))
                # Feet
                pygame.draw.rect(screen, (40, 30, 20), (lx,      oy + S * 2 // 3 + S // 4 + anim,     lw + 1, max(1, S // 8)))
                pygame.draw.rect(screen, (40, 30, 20), (rx,      oy + S * 2 // 3 + S // 4 + (1-anim), lw + 1, max(1, S // 8)))
                # Eye
                eye_x = ox + S // 4 + hw - max(1, S // 8) - 1 if d >= 0 else ox + S // 4 + 1
                pygame.draw.rect(screen, (10, 10, 10), (eye_x, oy + S // 3 - max(1, S // 7), max(1, S // 8), max(1, S // 8)))
                # ── Dialogue bubble (only when zoomed in enough) ──────────────
                if C >= 6 and gene[cx][cy] is not None:
                    g2   = gene[cx][cy]
                    goal = g2.get('goal','idle')
                    hun  = g2.get('hunger',0)
                    thr  = g2.get('thirst',0)
                    kn   = g2.get('knowledge',0)
                    blk  = g2.get('blocks',0)
                    hp   = g2.get('health',100)
                    tls  = g2.get('tools',{})
                    inv2 = g2.get('inv',{})
                    wealth = sum(inv2.get(k,0) for k in ('gold','copper','crystal'))
                    _GOAL_LABELS = {
                        'flee':     ('!!!',        (255,  50,  30)),
                        'drink':    ('thirsty',    (100, 180, 255)),
                        'forage':   ('hungry',     (255, 200,  60)),
                        'hunt':     ('hunting',    (220,  80,  40)),
                        'social':   ('trading' if wealth>0 else 'social', (160, 230, 120)),
                        'build':    ('building',   (200, 160,  60)),
                        'prospect': ('prospecting',(200, 200,  80)),
                        'idle':     ('',           (180, 190, 210)),
                    }
                    label, tcol = _GOAL_LABELS.get(goal, ('', (180,190,210)))
                    if not label and hun > 700: label, tcol = 'starving!', (255, 40, 40)
                    elif not label and thr > 400: label, tcol = 'dehydrated!', (60, 120, 255)
                    elif not label and hp < 40: label, tcol = 'wounded!', (255, 100, 40)
                    elif not label and blk >= 5: label, tcol = 'building', (200, 160, 60)
                    # Tool badge suffix
                    tool_badge = ''
                    if tls.get('spear',0) > 0: tool_badge = ' [S]'
                    elif tls.get('axe',0)  > 0: tool_badge = ' [A]'
                    elif tls.get('pick',0) > 0: tool_badge = ' [P]'
                    elif tls.get('knife',0)> 0: tool_badge = ' [K]'
                    if C >= 8 and (label or tool_badge or wealth > 0):
                        display = (label or ('$'+str(wealth) if wealth>0 else 'idle')) + tool_badge
                        bt = sfont.render(display, True, tcol)
                        bx2 = ox + S//2 - bt.get_width()//2
                        by2 = oy - bt.get_height() - 2
                        br  = pygame.Rect(bx2-3, by2-1, bt.get_width()+6, bt.get_height()+2)
                        pygame.draw.rect(screen, (8,8,18), br, border_radius=3)
                        pygame.draw.rect(screen, tcol, br, width=1, border_radius=3)
                        screen.blit(bt, (bx2, by2))
                    if C >= 10:
                        bar_w = S; bar_x = ox; bar_y = oy + S + 2
                        # Knowledge bar (green)
                        pygame.draw.rect(screen,(25,30,40),(bar_x,bar_y,bar_w,3))
                        pygame.draw.rect(screen,(80,200,120),(bar_x,bar_y,int(bar_w*kn/1000),3))
                        # Health bar (red, only if damaged)
                        if hp < 100:
                            pygame.draw.rect(screen,(40,10,10),(bar_x,bar_y+4,bar_w,2))
                            pygame.draw.rect(screen,(220,60,40),(bar_x,bar_y+4,int(bar_w*hp/100),2))

            elif etype == PREDATOR:
                pygame.draw.rect(screen, (55, 20, 5),    (sx,     sy, 1, H))       # left ear
                pygame.draw.rect(screen, (55, 20, 5),    (sx+C-1, sy, 1, H))       # right ear
                pygame.draw.rect(screen, (255, 200, 0),  (sx+H-1, sy+H, 2, 1))    # yellow eyes

            elif etype == TIGER:
                # Black vertical stripes over orange body
                pygame.draw.rect(screen, (25, 12, 0), (sx + 1, sy, 1, C))          # stripe
                pygame.draw.rect(screen, (25, 12, 0), (sx + 3, sy, 1, C))          # stripe
                pygame.draw.rect(screen, (255, 200, 0),(sx + H, sy + H, 1, 1))     # eye

            elif etype == LION:
                # Dark-gold mane border, lighter face center
                mc = (165, 105, 10)
                pygame.draw.rect(screen, mc, (sx,     sy,     C, 1))  # top mane
                pygame.draw.rect(screen, mc, (sx,     sy+C-1, C, 1))  # bottom mane
                pygame.draw.rect(screen, mc, (sx,     sy,     1, C))  # left mane
                pygame.draw.rect(screen, mc, (sx+C-1, sy,     1, C))  # right mane
                pygame.draw.rect(screen, (240, 210, 100), (sx+1, sy+1, H, H))      # face
                pygame.draw.rect(screen, (35, 15, 0),     (sx+H+1, sy+H, 1, 1))   # eye

            elif etype == WHALE:
                pygame.draw.rect(screen, (190, 215, 240),(sx, sy+C-2, C, 2))       # white belly
                pygame.draw.rect(screen, (15, 30, 70),   (sx+H-1, sy, H, 1))       # tail notch
                pygame.draw.rect(screen, (200, 220, 240),(sx+H, sy+1, 1, 1))       # eye gleam

            elif etype == DOLPHIN:
                pygame.draw.rect(screen, (60, 100, 165),(sx+H, sy-1, 2, 2))        # dorsal fin
                pygame.draw.rect(screen, (195, 225, 240),(sx+1, sy+H, C-2, H))     # white belly
                eye_x = sx + (H + 1) if d >= 0 else sx + (H - 2)
                pygame.draw.rect(screen, (10, 10, 10),  (eye_x, sy+H-1, 1, 1))     # eye

            elif etype == ANIMAL:
                # Generic critter: green outline
                pygame.draw.rect(screen, (40, 210, 80), (sx, sy, C, 1))
                pygame.draw.rect(screen, (40, 210, 80), (sx, sy+C-1, C, 1))

# ── Rendering ─────────────────────────────────────────────────────────────────
def render_grid():
    """Fast numpy-based renderer: LUT + per-type animations → surfarray blit."""
    g  = np.asarray(grid, dtype=np.intp)          # (COLS, ROWS)
    tf = frame_t

    # Base colours from LUT + stable per-cell noise
    r  = _clr_lut[g, 0].astype(np.int16) + _noise_r
    gn = _clr_lut[g, 1].astype(np.int16) + _noise_g
    b  = _clr_lut[g, 2].astype(np.int16) + _noise_b

    # ── FIRE — hot white-yellow core, orange tips, red fade ──────────────────
    fm = (g == FIRE)
    if fm.any():
        fl = np.random.randint(0, 90, g.shape, dtype=np.int16)
        r[fm] = np.clip(fl[fm] * 2 + 140, 180, 255)
        gn[fm] = np.clip(fl[fm]          ,   0, 200)
        b[fm]  = np.clip(fl[fm] // 4     ,   0,  60)

    # ── EMBER — pulsing orange glow ───────────────────────────────────────────
    em = (g == EMBER)
    if em.any():
        gl = int(45 * abs(math.sin(tf * 0.15)))
        r[em]  = np.clip(r[em].astype(np.int16)  + gl,      0, 255)
        gn[em] = np.clip(gn[em].astype(np.int16) + gl // 3, 0, 255)

    # ── LAVA — pulse with cracked-crust noise ─────────────────────────────────
    lm = (g == LAVA)
    if lm.any():
        p  = int(35 * abs(math.sin(tf * 0.018)))
        r[lm]  = np.clip(r[lm].astype(np.int16)  + p,      0, 255)
        gn[lm] = np.clip(gn[lm].astype(np.int16) + p // 4, 0, 255)
        b[lm]  = 0

    # ── MAGMA — deeper red pulse ──────────────────────────────────────────────
    mm = (g == MAGMA)
    if mm.any():
        p = int(22 * abs(math.sin(tf * 0.012)))
        r[mm]  = np.clip(r[mm].astype(np.int16) + p, 0, 255)

    # ── WATER — x-pos ripple shimmer ─────────────────────────────────────────
    wm = (g == WATER)
    if wm.any():
        wave = (np.sin(_X_ARR * 0.4 + tf * 0.025) * 22).astype(np.int16)
        b[wm]  = np.clip(b[wm].astype(np.int16)  + wave[wm], 0, 255)
        r[wm]  = np.clip(r[wm].astype(np.int16)  - wave[wm] // 4, 0, 255)

    # ── ICE — cold facet shimmer ──────────────────────────────────────────────
    im = (g == ICE)
    if im.any():
        fac = (np.cos(_X_ARR * 0.8) * np.sin(_Y_ARR * 0.8) * 25).astype(np.int16)
        r[im]  = np.clip(r[im].astype(np.int16)  + fac[im], 0, 255)
        gn[im] = np.clip(gn[im].astype(np.int16) + fac[im], 0, 255)
        b[im]  = np.clip(b[im].astype(np.int16)  + fac[im], 0, 255)

    # ── PLASMA — electric arc flicker ────────────────────────────────────────
    plm = (g == PLASMA)
    if plm.any():
        arc = np.random.randint(0, 80, g.shape, dtype=np.int16)
        b[plm] = np.clip(b[plm].astype(np.int16)  + arc[plm],      0, 255)
        r[plm] = np.clip(r[plm].astype(np.int16)  + arc[plm] // 4, 0, 255)
        gn[plm] = np.clip(gn[plm].astype(np.int16)+ arc[plm] // 2, 0, 255)

    # ── NEON — cycling hue ───────────────────────────────────────────────────
    nm = (g == NEON)
    if nm.any():
        ph = (tf // 6) % 3
        if ph == 0:   r[nm]=200; gn[nm]=  0; b[nm]=255
        elif ph == 1: r[nm]=  0; gn[nm]=220; b[nm]=200
        else:         r[nm]=255; gn[nm]=  0; b[nm]=160

    # ── LIGHTNING — white flash ───────────────────────────────────────────────
    lnm = (g == LIGHTNING)
    if lnm.any():
        v = np.int16(255 if tf % 2 == 0 else 200)
        r[lnm] = gn[lnm] = b[lnm] = v

    # ── GOLD — metallic shimmer ───────────────────────────────────────────────
    gom = (g == GOLD)
    if gom.any():
        sh = int(28 * abs(math.sin(tf * 0.01)))
        r[gom]  = np.clip(r[gom].astype(np.int16)  + sh,      0, 255)
        gn[gom] = np.clip(gn[gom].astype(np.int16) + sh // 2, 0, 255)

    # ── MERCURY — liquid mirror ───────────────────────────────────────────────
    merm = (g == MERCURY)
    if merm.any():
        ref = int(30 * abs(math.sin(tf * 0.02)))
        r[merm]  = np.clip(r[merm].astype(np.int16)  + ref, 0, 255)
        gn[merm] = np.clip(gn[merm].astype(np.int16) + ref, 0, 255)
        b[merm]  = np.clip(b[merm].astype(np.int16)  + ref, 0, 255)

    # ── CRYSTAL — prismatic shimmer ───────────────────────────────────────────
    crm = (g == CRYSTAL)
    if crm.any():
        sh = int(32 * abs(math.sin(tf * 0.005)))
        r[crm]  = np.clip(r[crm].astype(np.int16)  + sh, 0, 255)
        gn[crm] = np.clip(gn[crm].astype(np.int16) + sh, 0, 255)
        b[crm]  = np.clip(b[crm].astype(np.int16)  + sh, 0, 255)

    # ── ACID — bubbling green ─────────────────────────────────────────────────
    acm = (g == ACID)
    if acm.any():
        bub = (np.sin(_X_ARR * 0.7 + tf * 0.05) * 30 + 30).astype(np.int16)
        gn[acm] = np.clip(gn[acm].astype(np.int16) + bub[acm], 0, 255)

    # ── URANIUM — radioactive green glow ─────────────────────────────────────
    um = (g == URANIUM)
    if um.any():
        gl = int(55 * abs(math.sin(tf * 0.04)))
        gn[um] = np.clip(gn[um].astype(np.int16) + gl,      0, 255)
        r[um]  = np.clip(r[um].astype(np.int16)  - gl // 3, 0, 255)
        b[um]  = np.clip(b[um].astype(np.int16)  - gl // 4, 0, 255)

    # ── VOID — dark pulsing purple edge ──────────────────────────────────────
    vm = (g == VOID)
    if vm.any():
        pl = int(18 * abs(math.sin(tf * 0.03)))
        r[vm]  = 0
        gn[vm] = 0
        b[vm]  = pl

    # ── METHANE — faint translucent shimmer ───────────────────────────────────
    mthm = (g == METHANE)
    if mthm.any():
        fl2 = np.random.randint(0, 25, g.shape, dtype=np.int16)
        gn[mthm] = np.clip(gn[mthm].astype(np.int16) + fl2[mthm], 0, 255)
        b[mthm]  = np.clip(b[mthm].astype(np.int16)  + fl2[mthm] // 2, 0, 255)

    # ── STEEL — blue-grey glint ───────────────────────────────────────────────
    stm = (g == STEEL)
    if stm.any():
        gl2 = (np.cos(_X_ARR * 0.5 + _Y_ARR * 0.3) * 15 + 15).astype(np.int16)
        r[stm]  = np.clip(r[stm].astype(np.int16)  + gl2[stm], 0, 255)
        gn[stm] = np.clip(gn[stm].astype(np.int16) + gl2[stm], 0, 255)
        b[stm]  = np.clip(b[stm].astype(np.int16)  + gl2[stm], 0, 255)

    # ── BIRD — wing-beat brightness flash ────────────────────────────────────
    brm = (g == BIRD)
    if brm.any():
        wb = int(35 * abs(math.sin(tf * 0.22)))
        r[brm]  = np.clip(r[brm].astype(np.int16)  + wb, 0, 255)
        gn[brm] = np.clip(gn[brm].astype(np.int16) + wb, 0, 255)

    # ── FISH — blue shimmering scales ─────────────────────────────────────────
    fsm = (g == FISH)
    if fsm.any():
        fsh = (np.sin(_X_ARR * 0.9 + tf * 0.12) * 20 + 20).astype(np.int16)
        b[fsm]  = np.clip(b[fsm].astype(np.int16)  + fsh[fsm], 0, 255)
        gn[fsm] = np.clip(gn[fsm].astype(np.int16) + fsh[fsm] // 3, 0, 255)

    # ── HUMAN — warm breathing pulse ──────────────────────────────────────────
    hum = (g == HUMAN)
    if hum.any():
        pulse = int(18 * abs(math.sin(tf * 0.035)))
        r[hum] = np.clip(r[hum].astype(np.int16) + pulse, 0, 255)

    # ── PREDATOR / TIGER / LION — amber eye gleam ─────────────────────────────
    big_cat = (g == PREDATOR) | (g == TIGER) | (g == LION)
    if big_cat.any():
        eye = int(28 * abs(math.sin(tf * 0.055)))
        r[big_cat] = np.clip(r[big_cat].astype(np.int16) + eye, 0, 255)
        gn[big_cat] = np.clip(gn[big_cat].astype(np.int16) + eye // 2, 0, 255)

    # ── WHALE — slow deep-sea pulse ────────────────────────────────────────────
    whm = (g == WHALE)
    if whm.any():
        dp = int(15 * abs(math.sin(tf * 0.018)))
        b[whm]  = np.clip(b[whm].astype(np.int16)  + dp, 0, 255)
        gn[whm] = np.clip(gn[whm].astype(np.int16) + dp // 3, 0, 255)

    # ── DOLPHIN — playful shimmer ──────────────────────────────────────────────
    dlm = (g == DOLPHIN)
    if dlm.any():
        ds = int(22 * abs(math.sin(tf * 0.09)))
        b[dlm]  = np.clip(b[dlm].astype(np.int16)  + ds, 0, 255)
        gn[dlm] = np.clip(gn[dlm].astype(np.int16) + ds // 2, 0, 255)

    # ── Write to render buffer ────────────────────────────────────────────────
    global _scale_surf
    np.clip(r,  0, 255, out=r)
    np.clip(gn, 0, 255, out=gn)
    np.clip(b,  0, 255, out=b)
    _render_buf[:, :, 0] = r.astype(np.uint8)
    _render_buf[:, :, 1] = gn.astype(np.uint8)
    _render_buf[:, :, 2] = b.astype(np.uint8)
    pygame.surfarray.blit_array(pixel_surf, _render_buf)
    
    scaled_w = int(COLS * CELL * zoom_level)
    scaled_h = int(ROWS * CELL * zoom_level)
    if _scale_surf.get_size() != (scaled_w, scaled_h):
        _scale_surf = pygame.transform.scale(pixel_surf, (scaled_w, scaled_h))
    else:
        pygame.transform.scale(pixel_surf, (scaled_w, scaled_h), _scale_surf)
    screen.blit(_scale_surf, (cam_offset_x, cam_offset_y))

def draw_tornado_overlay():
    if not tornado_on: return
    t = frame_t
    Z = zoom_level
    for i in range(0, min(60, ROWS), 2):
        offset = int(math.sin(t*0.012 + i*0.35) * (i//2 + 1))
        radius = max(2, tornado_str*2 - i//8)
        alpha  = max(60, 200 - i*3)
        v = min(255, 140 + i*2)
        col = (v, v, min(255, v+20))
        px = int((tornado_x * CELL + offset) * Z) + cam_offset_x
        py = int((ROWS - 1 - i) * CELL * Z) + cam_offset_y
        rad = max(1, int(radius * CELL * Z // 2))
        pygame.draw.circle(screen, col, (px, py), rad)

def draw_sky_bg():
    """Gradient sky that blends day/night/weather."""
    sun_factor = (math.sin(sun_ang) + 1) / 2
    if is_day:
        top    = blend(hx('#000820'), hx('#2878d8'), sun_factor)
        bottom = blend(hx('#102040'), hx('#78c0f8'), sun_factor)
    else:
        top    = hx('#000408')
        bottom = hx('#080c18')
    if fog_on:
        fb = min(1.0, fog_t/500.0) * 0.55
        top    = blend(top,    hx('#9098a8'), fb)
        bottom = blend(bottom, hx('#a0a8b8'), fb)
    if heatwave:
        top    = blend(top,    hx('#ff4000'), 0.12)
        bottom = blend(bottom, hx('#ff8000'), 0.15)
    if acid_rain:
        top    = blend(top,    hx('#208000'), 0.18)
        bottom = blend(bottom, hx('#40c020'), 0.12)
    # Vertical gradient
    for sy in range(HEIGHT):
        t = sy / HEIGHT
        c = blend(top, bottom, t)
        pygame.draw.line(screen, c, (0, sy), (WIDTH, sy))

# ── UI rendering ──────────────────────────────────────────────────────────────
def draw_ui():
    # Semi-transparent panel
    panel = pygame.Surface((510, 200), pygame.SRCALPHA)
    pygame.draw.rect(panel, (8, 8, 20, 210), panel.get_rect(), border_radius=12)
    pygame.draw.rect(panel, (80, 80, 120, 180), panel.get_rect(), width=2, border_radius=12)
    pygame.draw.line(panel, (140,140,200,100), (12,2), (498,2), 1)
    screen.blit(panel, (6, 6))

    temp_col = hx('#ff6432') if temperature>30 else hx('#64b4ff') if temperature<0 else hx('#d8d8e0')
    ws = "Clear"
    if storming: ws="Storm"
    elif blizzard: ws="Blizzard"
    elif heatwave: ws="Heatwave"
    elif acid_rain: ws="Acid Rain"
    elif fog_on:   ws="Fog"
    elif raining:  ws="Rain"
    elif snowing:  ws="Snow"
    if tornado_on: ws += "+Tornado"

    info = [
        (f"Brush:{brush}  {'PAUSED' if paused else 'Running'}", hx('#e8e8f8')),
        (f"Weather: {ws:<22s}  {'Day' if is_day else 'Night'}", hx('#90b8f0')),
        (f"Wind: {abs(wind_x):.1f}{'>' if wind_x>0 else '<' if wind_x<0 else '-'}  "
         f"Temp:{temperature:+.0f}C  Hum:{int(global_hum*100)}%", temp_col),
        ("C=Clear  P=Pause  R=Rain  S=Snow  T=Storm  N=Tornado  ESC=Menu", hx('#787888')),
    ]
    for i,(txt,col) in enumerate(info):
        screen.blit(font.render(txt, True, col), (18, 14 + i*20))

    for btn in buttons:
        if btn.lbl=="Rain":     btn.col=hx('#309820') if raining      else hx('#1e4eb0')
        elif btn.lbl=="Snow":   btn.col=hx('#309890') if snowing      else hx('#4898b8')
        elif btn.lbl=="Pause":  btn.col=hx('#903030') if paused       else hx('#404040')
        elif btn.lbl=="Elements": btn.col=hx('#284880') if sidebar_open else hx('#183860')
        btn.draw(screen)

    # Current element swatch + name next to Elements button
    sx = 220; sy = R3 + 1
    el_col = COLORS.get(cur_el, hx('#808080'))
    pygame.draw.rect(screen, el_col, pygame.Rect(sx, sy, 20, 20), border_radius=3)
    pygame.draw.rect(screen, hx('#606080'), pygame.Rect(sx, sy, 20, 20), width=1, border_radius=3)
    ntxt = font.render(NAMES.get(cur_el, '?'), True, hx('#e8e8f8'))
    screen.blit(ntxt, (sx + 26, sy + 3))

    # Brush preview circle near cursor
    mp = pygame.mouse.get_pos()
    in_ui  = mp[0] < 514 and mp[1] < 206
    in_sb  = sidebar_open and mp[0] >= WIDTH - SIDEBAR_W
    if not in_ui and not in_sb:
        col = COLORS.get(cur_el, hx('#ffffff'))
        rad = max(2, int(brush * CELL * zoom_level))
        pygame.draw.circle(screen, col, mp, rad, 2)
        pygame.draw.circle(screen, hx('#ffffff'), mp, rad + 1, 1)

_sidebar_filtered = []   # shared between draw_sidebar and click handler

def draw_sidebar():
    global sidebar_scroll, _sidebar_filtered
    sb_x = WIDTH - SIDEBAR_W
    # Background
    pygame.draw.rect(screen, hx('#060810'), pygame.Rect(sb_x - 2, 0, SIDEBAR_W + 2, HEIGHT))
    pygame.draw.line(screen, hx('#3040a0'), (sb_x - 2, 0), (sb_x - 2, HEIGHT), 2)
    # Header
    if sidebar_animal_mode:
        pygame.draw.rect(screen, hx('#141808'), pygame.Rect(sb_x, 0, SIDEBAR_W, 38))
        htxt = font.render("ANIMALS", True, hx('#80e050'))
    else:
        pygame.draw.rect(screen, hx('#0c1428'), pygame.Rect(sb_x, 0, SIDEBAR_W, 38))
        htxt = font.render("ELEMENTS", True, hx('#ffd060'))
    screen.blit(htxt, (sb_x + SIDEBAR_W // 2 - htxt.get_width() // 2, 11))
    # Close button
    close_rect = pygame.Rect(sb_x + SIDEBAR_W - 28, 8, 20, 20)
    pygame.draw.rect(screen, hx('#502020'), close_rect, border_radius=3)
    cx_t = font.render("x", True, hx('#ff8080'))
    screen.blit(cx_t, cx_t.get_rect(center=close_rect.center))
    # Animal-mode toggle chip
    anim_chip = pygame.Rect(sb_x + 6, 42, 76, 18)
    pygame.draw.rect(screen, hx('#1a3a10') if sidebar_animal_mode else hx('#0e1820'), anim_chip, border_radius=3)
    pygame.draw.rect(screen, hx('#50a030') if sidebar_animal_mode else hx('#284060'), anim_chip, width=1, border_radius=3)
    act = font.render("< All" if sidebar_animal_mode else "Animals >", True,
                      hx('#70d040') if sidebar_animal_mode else hx('#4080a0'))
    screen.blit(act, (anim_chip.x + 4, anim_chip.y + 3))
    # Search box (shifted right of animal chip)
    search_rect = pygame.Rect(sb_x + 88, 42, SIDEBAR_W - 94, 18)
    scol = hx('#182258') if sidebar_search_active else hx('#101830')
    pygame.draw.rect(screen, scol, search_rect, border_radius=4)
    pygame.draw.rect(screen, hx('#3858c0') if sidebar_search_active else hx('#202848'), search_rect, width=1, border_radius=4)
    caret = "|" if sidebar_search_active and (frame_t // 20) % 2 == 0 else ""
    if sidebar_search:
        stxt = font.render(sidebar_search + caret, True, hx('#d8e4ff'))
    elif sidebar_search_active:
        ph = font.render("Search...", True, hx('#2a3050'))
        screen.blit(ph, (search_rect.x + 4, search_rect.y + 2))
        stxt = font.render(caret, True, hx('#d8e4ff'))
    else:
        stxt = font.render("Search...", True, hx('#2a3050'))
    screen.blit(stxt, (search_rect.x + 4, search_rect.y + 2))
    # ── Filter + sort alphabetically ─────────────────────────────────────────
    query = sidebar_search.lower()
    if sidebar_animal_mode:
        base_list = [ANIMAL, BIRD, FISH, PREDATOR, HUMAN, TIGER, LION, WHALE, DOLPHIN]
    else:
        base_list = ELEMENT_LIST
    filtered = sorted([el for el in base_list if query in NAMES.get(el, '').lower()],
                      key=lambda eid: NAMES.get(eid, ''))
    _sidebar_filtered[:] = filtered   # share with click handler
    # List dimensions
    LIST_Y = 68; item_h = 36; list_h = HEIGHT - LIST_Y - 4
    max_scroll = max(0, len(filtered) * item_h - list_h)
    sidebar_scroll = max(0, min(sidebar_scroll, max_scroll))
    old_clip = screen.get_clip()
    screen.set_clip(pygame.Rect(sb_x, LIST_Y, SIDEBAR_W, list_h))
    mp = pygame.mouse.get_pos()
    for i, el in enumerate(filtered):
        iy = LIST_Y + i * item_h - sidebar_scroll
        if iy + item_h < LIST_Y or iy > HEIGHT: continue
        item_rect = pygame.Rect(sb_x + 3, iy + 2, SIDEBAR_W - 11, item_h - 4)
        if el == cur_el:
            pygame.draw.rect(screen, hx('#1a3870'), item_rect, border_radius=4)
            pygame.draw.rect(screen, hx('#3868d0'), item_rect, width=1, border_radius=4)
        elif item_rect.collidepoint(mp):
            pygame.draw.rect(screen, hx('#10182e'), item_rect, border_radius=4)
        swatch = pygame.Rect(sb_x + 9, iy + 10, 16, 16)
        pygame.draw.rect(screen, COLORS.get(el, hx('#808080')), swatch, border_radius=2)
        pygame.draw.rect(screen, hx('#404870'), swatch, width=1, border_radius=2)
        tcol = hx('#ffffff') if el == cur_el else hx('#a8b8d8')
        nt = font.render(NAMES.get(el, '?'), True, tcol)
        screen.blit(nt, (sb_x + 32, iy + 11))
    screen.set_clip(old_clip)
    # Scrollbar
    if max_scroll > 0:
        track = pygame.Rect(WIDTH - 7, LIST_Y, 5, list_h)
        pygame.draw.rect(screen, hx('#151a30'), track)
        knob_h = max(20, int(list_h * list_h / max(1, len(filtered) * item_h)))
        knob_y = LIST_Y + int((sidebar_scroll / max_scroll) * (list_h - knob_h))
        pygame.draw.rect(screen, hx('#3858b0'), pygame.Rect(WIDTH - 7, knob_y, 5, knob_h), border_radius=2)

# ── World generation helpers ───────────────────────────────────────────────────
def _place_crystal_veins(h, count=6, min_depth=8, max_depth=30, cluster=3):
    """Scatter crystal clusters underground across the world."""
    for _ in range(count):
        cx = random.randint(4, COLS-5)
        gh = h[cx]
        cy = random.randint(gh + min_depth, min(ROWS-3, gh + max_depth))
        # Only place in stone
        if not (inb(cx,cy) and grid[cx][cy] == STONE): continue
        for ox in range(-cluster, cluster+1):
            for oy in range(-cluster, cluster+1):
                if ox*ox+oy*oy <= cluster*cluster:
                    if inb(cx+ox,cy+oy) and grid[cx+ox][cy+oy]==STONE:
                        if random.random() < 0.4: grid[cx+ox][cy+oy] = CRYSTAL

def _gen_heights(base_frac, amp_frac, freq, seed=0):
    h = []
    for x in range(COLS):
        v  = math.sin(x * freq        + seed) * 0.50
        v += math.sin(x * freq * 2.3  + seed + 1.7) * 0.25
        v += math.sin(x * freq * 5.1  + seed + 3.3) * 0.15
        v += math.sin(x * freq * 11.0 + seed + 0.9) * 0.10
        h.append(max(3, min(ROWS-3, int((base_frac + v * amp_frac) * ROWS))))
    return h

def _sp(x, y, el, kn=720):
    """Spawn element with correct initialisation."""
    if not inb(x, y): return
    grid[x][y]=el; life[x][y]=0; data[x][y]=0; gene[x][y]=None
    temp_g[x][y]=temperature; oxy[x][y]=1.0; pressure[x][y]=0.0
    if el in ANIMAL_TYPES:
        g=make_genes(); g['knowledge']=kn; g['blocks']=5; g['mine_cd']=0
        gene[x][y]=g; life[x][y]=random.choice([-1,1])
    elif el==FIRE: life[x][y]=random.randint(80,180); temp_g[x][y]=500.0

def _clear_world():
    for x in range(COLS):
        for y in range(ROWS):
            grid[x][y]=EMPTY; life[x][y]=0; data[x][y]=0
            gene[x][y]=None; temp_g[x][y]=temperature
            oxy[x][y]=1.0; pressure[x][y]=0.0

def gen_desert():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.62,0.10,0.04,s)
    for x in range(COLS):
        for y in range(h[x],ROWS):
            grid[x][y] = SAND if y<h[x]+3 else SANDSTONE if y<h[x]+10 else STONE
    # Oases
    for _ in range(random.randint(2,4)):
        ox=random.randint(10,COLS-10)
        for py in range(h[ox],h[ox]+2):
            for px in range(ox-4,ox+5):
                if inb(px,py): grid[px][py]=WATER
        for px in range(ox-6,ox+7):
            if inb(px,h[ox]-1): grid[px][h[ox]-1]=PLANT
        if inb(ox,h[ox]-2): grid[ox][h[ox]-2]=SAPLING
    # Cacti (wood pillars)
    for _ in range(COLS//8):
        cx=random.randint(2,COLS-3); ht=random.randint(3,5)
        for py in range(h[cx]-ht,h[cx]):
            if inb(cx,py): grid[cx][py]=WOOD
    # Ore and crystal veins underground
    _place_crystal_veins(h, count=5, min_depth=10)
    for _ in range(8):
        vx=random.randint(4,COLS-5); vy=random.randint(h[vx]+8,min(ROWS-3,h[vx]+25))
        if inb(vx,vy) and grid[vx][vy]==STONE:
            mat=random.choice([GOLD,COPPER,COAL,COPPER]); grid[vx][vy]=mat
    # Animals
    for _ in range(5): _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,SNAKE)
    for _ in range(8): _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,RABBIT)
    if random.random()<0.5:   # nomadic humans
        hxc=random.randint(15,COLS-15)
        for i in range(random.randint(2,5)):
            _sp(hxc+i-2,h[hxc]-1,HUMAN,kn=random.randint(600,800))

def gen_plains():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.60,0.06,0.025,s)
    for x in range(COLS):
        for y in range(h[x],ROWS):
            grid[x][y] = WETDIRT if y==h[x] else DIRT if y<h[x]+6 else STONE
    for x in range(0,COLS,3):
        r=random.random(); gh=h[x]
        if r<0.22 and inb(x,gh-1): grid[x][gh-1]=PLANT
        elif r<0.32 and inb(x,gh-1): grid[x][gh-1]=WHEAT
        elif r<0.38 and inb(x,gh-1): grid[x][gh-1]=BERRY
        elif r<0.43 and inb(x,gh-1): grid[x][gh-1]=APPLE
    for _ in range(COLS//12):
        tx=random.randint(2,COLS-3); th=random.randint(6,10); gh=h[tx]
        for py in range(gh-th,gh):
            if inb(tx,py): grid[tx][py]=WOOD
        for lx in range(tx-2,tx+3):
            for ly in range(gh-th-3,gh-th+2):
                if inb(lx,ly) and grid[lx][ly]==EMPTY: grid[lx][ly]=LEAF
    for _ in range(random.randint(1,3)):
        sx=random.randint(5,COLS-5)
        for px in range(sx-2,sx+3):
            if inb(px,h[sx]): grid[px][h[sx]]=WATER
    # Ore and crystal underground
    _place_crystal_veins(h, count=6, min_depth=8)
    for _ in range(10):
        vx=random.randint(4,COLS-5); vy=random.randint(h[vx]+7,min(ROWS-3,h[vx]+20))
        if inb(vx,vy) and grid[vx][vy]==STONE:
            grid[vx][vy]=random.choice([COPPER,COAL,GOLD,COPPER,COAL])
    for _ in range(10): _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,RABBIT)
    for _ in range(6):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BIRD)
    for _ in range(3):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,ANIMAL)
    if random.random()<0.6:   # human village
        vx=random.randint(20,COLS-20); gh=h[vx]
        n=random.randint(3,8)
        for i in range(n): _sp(vx+i*2-n,gh-1,HUMAN,kn=random.randint(700,900))
        wx=vx+8; gh2=h[wx]
        for py in range(gh2-5,gh2):
            if inb(wx-3,py): grid[wx-3][py]=WOOD
            if inb(wx+3,py): grid[wx+3][py]=WOOD
        for px in range(wx-3,wx+4):
            if inb(px,gh2-5): grid[px][gh2-5]=WOOD
        for fx in range(vx-4,vx+5):
            if inb(fx,gh-1) and grid[fx][gh-1]==EMPTY: grid[fx][gh-1]=WHEAT

def gen_forest():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.58,0.07,0.03,s)
    for x in range(COLS):
        for y in range(h[x],ROWS):
            grid[x][y] = DIRT if y<h[x]+5 else STONE
    x=0
    while x<COLS:
        tx=x+random.randint(0,3)
        if tx>=COLS: break
        th=random.randint(7,14); gh=h[tx]
        for py in range(gh-th,gh):
            if inb(tx,py): grid[tx][py]=WOOD
        for lx in range(tx-3,tx+4):
            for ly in range(gh-th-4,gh-th+3):
                if inb(lx,ly) and grid[lx][ly]==EMPTY:
                    grid[lx][ly]=LEAF if random.random()<0.8 else VINE
        x+=random.randint(3,6)
    for x in range(0,COLS,2):
        r=random.random(); gh=h[x]
        if r<0.3  and inb(x,gh-1) and grid[x][gh-1]==EMPTY: grid[x][gh-1]=MOSS
        elif r<0.4 and inb(x,gh-1) and grid[x][gh-1]==EMPTY: grid[x][gh-1]=FUNGUS
        elif r<0.45 and inb(x,gh-1) and grid[x][gh-1]==EMPTY: grid[x][gh-1]=MUSHROOM
    # Deep crystal veins (forest has rich underground)
    _place_crystal_veins(h, count=8, min_depth=6, cluster=4)
    for _ in range(12):
        vx=random.randint(4,COLS-5); vy=random.randint(h[vx]+6,min(ROWS-3,h[vx]+18))
        if inb(vx,vy) and grid[vx][vy]==STONE:
            grid[vx][vy]=random.choice([COPPER,COAL,COAL,GOLD])
    for _ in range(5):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BEAR)
    for _ in range(12): _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,RABBIT)
    for _ in range(8):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BIRD)
    for _ in range(4):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,FROG)
    for _ in range(4):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,SNAKE)

def gen_ocean():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.82,0.05,0.03,s)
    wl=int(ROWS*0.55)
    for x in range(COLS):
        for y in range(h[x],ROWS):
            grid[x][y]=SAND if y<h[x]+3 else STONE
        for y in range(wl,h[x]):
            if inb(x,y): grid[x][y]=WATER
    # Seabed decor
    for x in range(8,COLS-8,4):
        r=random.random()
        if r<0.3  and inb(x,h[x]-1) and grid[x][h[x]-1]==EMPTY: grid[x][h[x]-1]=SEAWEED
        elif r<0.5 and inb(x,h[x]-1) and grid[x][h[x]-1]==EMPTY: grid[x][h[x]-1]=CORAL
    for _ in range(random.randint(2,4)):  # islands
        ix=random.randint(12,COLS-12); isle_top=wl-random.randint(4,8)
        for px in range(ix-6,ix+7):
            for py in range(isle_top,wl+1):
                if inb(px,py) and abs(px-ix)<=(6-(py-isle_top)//2):
                    grid[px][py]=SAND
        if inb(ix,isle_top-1): grid[ix][isle_top-1]=SAPLING
        if inb(ix-1,isle_top-1) and grid[ix-1][isle_top-1]==EMPTY: grid[ix-1][isle_top-1]=PLANT
        if random.random()<0.45: _sp(ix,isle_top-1,HUMAN,kn=random.randint(600,760))
    # Crystals in underwater rock (rare, valuable)
    _place_crystal_veins(h, count=4, min_depth=4, max_depth=18, cluster=2)
    for _ in range(6):
        vx=random.randint(4,COLS-5); vy=random.randint(h[vx]+4,min(ROWS-3,h[vx]+14))
        if inb(vx,vy) and grid[vx][vy]==STONE:
            grid[vx][vy]=random.choice([COPPER,GOLD,COAL])
    for _ in range(10): _sp(random.randint(5,COLS-5),random.randint(wl+4,ROWS-4),FISH)
    for _ in range(4):  _sp(random.randint(5,COLS-5),random.randint(wl+2,wl+12),DOLPHIN)
    for _ in range(2):  _sp(random.randint(5,COLS-5),random.randint(wl+5,wl+18),WHALE)
    for _ in range(6):  _sp(random.randint(5,COLS-5),random.randint(wl+3,ROWS-5),JELLYFISH)

def gen_mountains():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.45,0.30,0.03,s)
    snow_line=int(ROWS*0.30)
    for x in range(COLS):
        gh=h[x]
        for y in range(gh,ROWS):
            grid[x][y]=GRAVEL if y<gh+4 else STONE
        for y in range(gh,gh+3):
            if gh<=snow_line and inb(x,y): grid[x][y]=SNOW
        if random.random()<0.14:
            vy=random.randint(gh+5,min(ROWS-3,gh+22))
            mat=random.choice([COAL,COAL,COPPER,GOLD,COPPER,CRYSTAL])
            for px in range(x-1,x+2):
                if inb(px,vy): grid[px][vy]=mat
    for _ in range(8):
        ix=random.randint(5,COLS-5); iy=random.randint(int(ROWS*0.28),int(ROWS*0.48))
        if inb(ix,iy) and grid[ix][iy]==STONE:
            for ox,oy in [(-1,0),(1,0),(0,-1),(0,1)]:
                if inb(ix+ox,iy+oy) and grid[ix+ox][iy+oy]==STONE: grid[ix+ox][iy+oy]=ICE
    # Extra crystal clusters in mountains (best biome for crystal)
    _place_crystal_veins(h, count=12, min_depth=5, max_depth=35, cluster=5)
    for _ in range(5):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BEAR)
    for _ in range(8):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BIRD)
    for _ in range(4):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,RABBIT)
    if random.random()<0.55:
        mc=random.randint(20,COLS-20); gh=h[mc]
        for i in range(random.randint(2,4)):
            _sp(mc+i-1,gh-1,HUMAN,kn=random.randint(700,860))
        if inb(mc-4,gh-1): grid[mc-4][gh-1]=FIRE; life[mc-4][gh-1]=120; temp_g[mc-4][gh-1]=500.0

def gen_swamp():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.65,0.04,0.05,s)
    wl=int(ROWS*0.68)
    for x in range(COLS):
        gh=h[x]
        for y in range(gh,ROWS):
            grid[x][y]=MUD if y<gh+4 else WETDIRT if y<gh+8 else DIRT
        for y in range(wl,gh):
            if inb(x,y): grid[x][y]=WATER
    for x in range(0,COLS,2):
        r=random.random(); gh=h[x]
        if r<0.25 and inb(x,gh-1) and grid[x][gh-1]==EMPTY: grid[x][gh-1]=VINE
        elif r<0.40 and inb(x,gh-1) and grid[x][gh-1]==EMPTY: grid[x][gh-1]=MOSS
        elif r<0.50 and inb(x,gh-1) and grid[x][gh-1]==EMPTY: grid[x][gh-1]=FUNGUS
    for _ in range(COLS//10):
        tx=random.randint(2,COLS-3); gh=h[tx]
        for py in range(gh-random.randint(5,9),gh):
            if inb(tx,py): grid[tx][py]=WOOD
    # Crystal pockets deep in swamp mud/stone
    _place_crystal_veins(h, count=4, min_depth=10, cluster=2)
    for _ in range(6):
        vx=random.randint(4,COLS-5); vy=random.randint(h[vx]+8,min(ROWS-3,h[vx]+20))
        if inb(vx,vy) and grid[vx][vy] in (STONE,DIRT):
            grid[vx][vy]=random.choice([COPPER,COAL,COAL])
    for _ in range(8):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,FROG)
    for _ in range(6):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,SNAKE)
    for _ in range(4):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,SPIDER)
    for _ in range(6):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BIRD)

def gen_civilization():
    _clear_world()
    s=random.uniform(0,10); h=_gen_heights(0.60,0.04,0.02,s)
    for x in range(COLS):
        for y in range(h[x],ROWS):
            grid[x][y]=WETDIRT if y==h[x] else DIRT if y<h[x]+5 else STONE
    # Crops
    for x in range(5,COLS-5,5):
        crop=random.choice([WHEAT,CORN,CARROT,WHEAT])
        for px in range(x,min(COLS-1,x+3)):
            if inb(px,h[x]-1) and grid[px][h[x]-1]==EMPTY: grid[px][h[x]-1]=crop
    # Buildings
    for _ in range(random.randint(5,9)):
        bx=random.randint(8,COLS-12); gh=h[bx]
        w=random.randint(6,10); ht=random.randint(4,7)
        for px in range(bx,bx+w):
            if inb(px,gh): grid[px][gh]=STONE
        for py in range(gh-ht,gh):
            if inb(bx,py):    grid[bx][py]=STONE
            if inb(bx+w-1,py): grid[bx+w-1][py]=STONE
        for px in range(bx-1,bx+w+1):
            if inb(px,gh-ht): grid[px][gh-ht]=WOOD
        fi=bx+w//2
        if inb(fi,gh-1): grid[fi][gh-1]=FIRE; life[fi][gh-1]=200; temp_g[fi][gh-1]=500.0
    # Lots of advanced humans
    n=random.randint(12,22)
    for _ in range(n):
        hxr=random.randint(5,COLS-5)
        _sp(hxr,h[hxr]-1,HUMAN,kn=random.randint(800,1000))
    # Crystal veins + precious ore for the civilization to mine
    _place_crystal_veins(h, count=8, min_depth=7, cluster=4)
    for _ in range(14):
        vx=random.randint(4,COLS-5); vy=random.randint(h[vx]+6,min(ROWS-3,h[vx]+22))
        if inb(vx,vy) and grid[vx][vy]==STONE:
            grid[vx][vy]=random.choice([GOLD,COPPER,COAL,COPPER,GOLD,STEEL])
    for _ in range(6):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,RABBIT)
    for _ in range(4):  _sp(random.randint(5,COLS-5),h[random.randint(5,COLS-5)]-1,BIRD)

# ── Preset card data ───────────────────────────────────────────────────────────
_PRESETS = [
    ("Desert",       hx('#c8a040'), "Sand dunes, oases, snakes & rabbits.\nMaybe nomadic humans.",          gen_desert),
    ("Plains",       hx('#60c040'), "Rolling hills, plants, animals.\nOften a small human village.",        gen_plains),
    ("Forest",       hx('#208030'), "Dense trees, bears, rabbits, frogs.\nNo humans.",                      gen_forest),
    ("Ocean",        hx('#1868c8'), "Deep water, coral, fish, dolphins.\nSmall islands with survivors.",    gen_ocean),
    ("Mountains",    hx('#a0a8b8'), "Rocky peaks, snow, coal & gold.\nSometimes a mining camp.",            gen_mountains),
    ("Swamp",        hx('#507040'), "Mud, water pools, fungus, vines.\nFrogs, snakes & spiders.",           gen_swamp),
    ("Civilization", hx('#e0a020'), "Humans with high knowledge, crops,\nstone buildings & fire.",          gen_civilization),
    ("Blank",        hx('#303844'), "Empty world — build from scratch.",                                    None),
]
_preset_rects = []   # filled by draw_home

def draw_home():
    global _preset_rects
    screen.fill(hx('#030609'))
    # Starfield (seeded per frame to be stable)
    rng = random.Random(42)
    for _ in range(200):
        sx=rng.randint(0,WIDTH); sy=rng.randint(0,HEIGHT)
        sv=rng.randint(80,240)
        pygame.draw.circle(screen,(sv,sv,sv),(sx,sy),rng.choice([1,1,1,2]))

    pulse=(math.sin(frame_t*0.04)+1)*0.5
    glow_col=cc(0xff,int(0xb0+0x40*pulse),int(0x10+0x30*pulse))
    title=tfont.render("ELEMENTAL SANDBOX",True,glow_col)
    sub  =sfont.render("Choose a world to begin",True,hx('#8090b0'))
    screen.blit(title,(WIDTH//2-title.get_width()//2, 18))
    screen.blit(sub,  (WIDTH//2-sub.get_width()//2,   66))

    # 4×2 grid of preset cards
    CARD_W=210; CARD_H=148; COLS_N=4; ROWS_N=2
    gap_x=(WIDTH - COLS_N*CARD_W)//(COLS_N+1)
    gap_y=18; top_y=96
    mp=pygame.mouse.get_pos()
    _preset_rects.clear()
    for i,(name,col,desc,fn) in enumerate(_PRESETS):
        col_i=i%COLS_N; row_i=i//COLS_N
        cx=gap_x + col_i*(CARD_W+gap_x)
        cy=top_y + row_i*(CARD_H+gap_y)
        rect=pygame.Rect(cx,cy,CARD_W,CARD_H)
        _preset_rects.append((rect,fn))
        hover=rect.collidepoint(mp)
        bg=hx('#1a2030') if not hover else hx('#253050')
        border=col if hover else hx('#303848')
        pygame.draw.rect(screen,bg,rect,border_radius=10)
        pygame.draw.rect(screen,border,rect,width=2,border_radius=10)
        # Colour swatch
        sw=pygame.Rect(cx+12,cy+12,32,32)
        pygame.draw.rect(screen,col,sw,border_radius=5)
        # Name
        nt=font.render(name,True,hx('#ffffff') if hover else hx('#d0ddf0'))
        screen.blit(nt,(cx+52,cy+14))
        # Description lines
        for li,dline in enumerate(desc.split('\n')):
            dt=sfont.render(dline,True,hx('#8090a8'))
            screen.blit(dt,(cx+12,cy+54+li*20))
    # Controls hint at bottom
    hint=sfont.render("Left Click = Draw  |  Right Click = Erase  |  R=Rain  T=Storm  P=Pause  C=Clear",
                      True,hx('#404858'))
    screen.blit(hint,(WIDTH//2-hint.get_width()//2,HEIGHT-24))

# ── Placement ─────────────────────────────────────────────────────────────────
def place(nx, ny):
    grid[nx][ny]  = cur_el
    life[nx][ny]  = 0
    data[nx][ny]  = 0
    gene[nx][ny]  = None
    temp_g[nx][ny]= temperature
    oxy[nx][ny]   = 1.0
    pressure[nx][ny] = 0.0
    if cur_el == FIRE:    life[nx][ny]=random.randint(80,180);  temp_g[nx][ny]=500.0
    elif cur_el == LAVA:  temp_g[nx][ny]=900.0
    elif cur_el == MAGMA: temp_g[nx][ny]=1100.0
    elif cur_el == ICE:   temp_g[nx][ny]=-5.0
    elif cur_el == ANIMAL:gene[nx][ny]=make_genes(); life[nx][ny]=random.choice([-1,1])
    elif cur_el in (SMOKE,STEAM,CLOUD): life[nx][ny]=random.randint(60,150)
    elif cur_el == ACID:  life[nx][ny]=random.randint(150,300)
    elif cur_el == PLASMA:life[nx][ny]=random.randint(40,100); temp_g[nx][ny]=2000.0
    elif cur_el == NEON:  life[nx][ny]=random.randint(200,400)
    elif cur_el == BUBBLE:  life[nx][ny]=random.randint(30,80)
    elif cur_el == METHANE:  life[nx][ny]=random.randint(200,600)
    elif cur_el == NITRO:    temp_g[nx][ny]=temperature
    elif cur_el == URANIUM:  temp_g[nx][ny]=temperature+20.0
    elif cur_el == HYDROGEN: life[nx][ny]=random.randint(150,400)
    elif cur_el == HELIUM:   life[nx][ny]=random.randint(200,500)
    elif cur_el in (BIRD,FISH,PREDATOR,HUMAN,TIGER,LION,WHALE,DOLPHIN):
        gene[nx][ny]=make_genes(); life[nx][ny]=random.choice([-1,1]); data[nx][ny]=0
        if cur_el==WHALE: life[nx][ny]=200  # start with full breath

# ── Main loop ─────────────────────────────────────────────────────────────────
running=True; drawing=False; erase=False; home=True
UI_W=514; UI_H=206

while running:
    frame_t += 1
    mp = pygame.mouse.get_pos()
    if not home:
        for btn in buttons: btn.check(mp)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running=False
        if home:
            if ev.type==pygame.KEYDOWN and ev.key==pygame.K_SPACE:
                home=False  # blank start
            elif ev.type==pygame.MOUSEBUTTONDOWN and ev.button==1:
                for rect,fn in _preset_rects:
                    if rect.collidepoint(ev.pos):
                        if fn is not None: fn()  # generate world
                        home=False; break
            continue
        consumed=False
        for btn in buttons:
            if btn.event(ev): consumed=True; break
        if consumed: continue
        if ev.type==pygame.MOUSEBUTTONDOWN:
            # ── Sidebar interactions ───────────────────────────────────────
            if sidebar_open:
                sb_x = WIDTH - SIDEBAR_W
                close_rect = pygame.Rect(sb_x + SIDEBAR_W - 28, 8, 20, 20)
                anim_chip_r = pygame.Rect(sb_x + 6, 42, 76, 18)
                search_rect = pygame.Rect(sb_x + 88, 42, SIDEBAR_W - 94, 18)
                if close_rect.collidepoint(ev.pos):
                    toggle_sidebar(); continue
                if anim_chip_r.collidepoint(ev.pos):
                    sidebar_animal_mode = not sidebar_animal_mode
                    sidebar_scroll = 0; continue
                if search_rect.collidepoint(ev.pos):
                    sidebar_search_active = True; continue
                if ev.pos[0] >= sb_x:
                    sidebar_search_active = False
                    if ev.button == 1:
                        # Use the same list draw_sidebar already built
                        LIST_Y=68; item_h=36
                        for i, el in enumerate(_sidebar_filtered):
                            iy = LIST_Y + i*item_h - sidebar_scroll
                            ir = pygame.Rect(sb_x+3, iy+2, SIDEBAR_W-11, item_h-4)
                            if ir.collidepoint(ev.pos):
                                cur_el = el; break
                    elif ev.button == 4:
                        sidebar_scroll = max(0, sidebar_scroll - 36)
                    elif ev.button == 5:
                        sidebar_scroll += 36
                    continue
            # ── Normal controls ────────────────────────────────────────────
            if ev.button==1:   drawing=True;  erase=False; _placed_animal=False
            elif ev.button==3: drawing=True;  erase=True;  _placed_animal=False
            elif ev.button==4: brush=min(30,brush+1)
            elif ev.button==5: brush=max(1,brush-1)
        elif ev.type==pygame.MOUSEBUTTONUP:
            if ev.button in (1,3): drawing=False
        elif ev.type==pygame.MOUSEWHEEL:
            mpos = pygame.mouse.get_pos()
            if sidebar_open and mpos[0] >= WIDTH - SIDEBAR_W:
                sidebar_scroll = max(0, sidebar_scroll - ev.y * 36)
            else:
                # Zoom toward mouse cursor
                if ev.y > 0: zoom_in(mpos[0], mpos[1])
                elif ev.y < 0: zoom_out(mpos[0], mpos[1])
        elif ev.type==pygame.KEYDOWN:
            # ── Sidebar search input takes priority ────────────────────────
            if sidebar_open and sidebar_search_active:
                if ev.key == pygame.K_ESCAPE:
                    sidebar_search_active = False
                elif ev.key == pygame.K_BACKSPACE:
                    sidebar_search = sidebar_search[:-1]
                elif ev.key == pygame.K_RETURN:
                    sidebar_search_active = False
                elif ev.unicode and ev.unicode.isprintable():
                    sidebar_search += ev.unicode
                continue
            if   ev.key==pygame.K_ESCAPE: home=True
            elif ev.key in (pygame.K_EQUALS, pygame.K_KP_PLUS): zoom_in()
            elif ev.key in (pygame.K_MINUS, pygame.K_KP_MINUS): zoom_out()
            elif ev.key==pygame.K_LEFT: pan_left()
            elif ev.key==pygame.K_RIGHT: pan_right()
            elif ev.key==pygame.K_UP: pan_up()
            elif ev.key==pygame.K_DOWN: pan_down()
            elif ev.key==pygame.K_c: clear_grid()
            elif ev.key==pygame.K_r: toggle_rain()
            elif ev.key==pygame.K_s: toggle_snow()
            elif ev.key==pygame.K_t: trigger_storm()
            elif ev.key==pygame.K_n: trigger_tornado()
            elif ev.key==pygame.K_b: trigger_blizzard()
            elif ev.key==pygame.K_f: trigger_fog()
            elif ev.key==pygame.K_h: trigger_heatwave()
            elif ev.key==pygame.K_a: trigger_acid_rain()
            elif ev.key==pygame.K_w: clear_weather()
            elif ev.key==pygame.K_p: toggle_pause()

    if home:
        draw_home(); pygame.display.flip(); clock.tick(FPS); continue

    # Drawing
    if drawing and not(mp[0]<UI_W and mp[1]<UI_H) and not(sidebar_open and mp[0]>=WIDTH-SIDEBAR_W):
        smx = (mp[0] - cam_offset_x) / (CELL * zoom_level)
        smy = (mp[1] - cam_offset_y) / (CELL * zoom_level)
        gx=int(smx); gy=int(smy)
        # Scale brush by zoom so it covers the same screen area regardless of zoom
        eff_brush = max(1, round(brush / max(0.3, zoom_level)))
        if not erase and cur_el in ANIMAL_TYPES:
            # Animals spawn one per click — place only at cursor centre
            if not _placed_animal and inb(gx,gy) and (grid[gx][gy] in (EMPTY,AIR) or grid[gx][gy] in LIQUIDS):
                place(gx,gy); _placed_animal=True
        else:
            for dx in range(-eff_brush,eff_brush+1):
                for dy in range(-eff_brush,eff_brush+1):
                    if dx*dx+dy*dy<=eff_brush*eff_brush:
                        nx,ny=gx+dx,gy+dy
                        if inb(nx,ny):
                            if erase: grid[nx][ny]=EMPTY; life[nx][ny]=0; data[nx][ny]=0; gene[nx][ny]=None
                            elif (grid[nx][ny] in (EMPTY,AIR)
                                  or grid[nx][ny] in LIQUIDS
                                  or cur_el in (STONE,WOOD,GLASS,CONCRETE)):
                                place(nx,ny)

    if not paused: update_grid()

    day_timer=(day_timer+1)%DAY_LEN
    sun_ang=(day_timer/DAY_LEN)*2*math.pi
    is_day=math.sin(sun_ang)>0

    # Render
    draw_sky_bg()
    render_grid()
    draw_animal_sprites()
    draw_tornado_overlay()
    draw_ui()
    if sidebar_open: draw_sidebar()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()