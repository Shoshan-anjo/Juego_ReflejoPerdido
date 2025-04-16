import pygame
import sys

# Configuración
ANCHO, ALTO = 800, 600
FILAS, COLUMNAS = 6, 12
TAM_CASILLA = 60
MARGEN = 30

COLOR_BG = (245, 240, 230)
COLOR_LINEA = (0, 0, 0)
COLOR_FIGURA = (102, 0, 204)
COLOR_OBJETIVO = (0, 0, 0)
COLOR_BLOQUEO = (100, 100, 100)
COLOR_ESPEJO = (0, 200, 200)
COLOR_TEXTO = (30, 30, 30)
COLOR_PANEL = (220, 220, 220)

pygame.init()
ventana = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Reflejo Perdido")
fuente = pygame.font.SysFont("Arial", 24)
reloj = pygame.time.Clock()

niveles = [
    {"figura_base": [(0, 0), (1, 0), (0, 1)], "jugador_pos": [1, 1], "objetivo_pos": [1, 1], "bloqueos": [], "reflejos": 3, "movimientos": 3},
    {"figura_base": [(0, 0), (1, 0), (1, 1)], "jugador_pos": [0, 2], "objetivo_pos": [2, 1], "bloqueos": [("pared", 1, 3)], "reflejos": 2, "movimientos": 6},
    {"figura_base": [(0, 0), (0, 1), (0, 2)], "jugador_pos": [0, 0], "objetivo_pos": [2, 2], "bloqueos": [("espejo", 1, 1)], "reflejos": 1, "movimientos": 4},
    {"figura_base": [(0, 0), (1, 0), (2, 0)], "jugador_pos": [0, 5], "objetivo_pos": [2, 1], "bloqueos": [("pared", 1, 5), ("espejo", 2, 4)], "reflejos": 2, "movimientos": 5},
    {"figura_base": [(0, 0), (1, 0), (0, 1), (1, 1)], "jugador_pos": [1, 4], "objetivo_pos": [1, 0], "bloqueos": [("pared", 2, 3), ("espejo", 0, 3)], "reflejos": 2, "movimientos": 6},
    {"figura_base": [(0, 0), (1, 0), (2, 0), (1, 1)], "jugador_pos": [0, 4], "objetivo_pos": [1, 0], "bloqueos": [("pared", 2, 2), ("espejo", 0, 2)], "reflejos": 2, "movimientos": 6},
    {"figura_base": [(0, 0), (0, 1), (1, 1), (2, 1)], "jugador_pos": [1, 4], "objetivo_pos": [0, 1], "bloqueos": [("espejo", 2, 3)], "reflejos": 3, "movimientos": 7},
    {
    "figura_base": [(0, 0), (1, 0), (1, 1), (1, 2), (2, 2)],
    "jugador_pos": [0, 3],
    "objetivo_pos": [0, 0],
    "bloqueos": [("pared", 2, 1), ("espejo", 1, 3), ("espejo", 0, 1)],
    "reflejos": 2,
    "movimientos": 10
},

# Nivel 12: Maestro
{
    "figura_base": [(0, 0), (0, 1), (1, 0), (2, 0), (2, 1)],
    "jugador_pos": [1, 4],
    "objetivo_pos": [1, 0],
    "bloqueos": [("pared", 2, 3), ("espejo", 0, 2)],
    "reflejos": 1,
    "movimientos": 9
},

# Nivel 14: Gran Maestro
{
    "figura_base": [(0, 0), (1, 0), (1, 1), (2, 0), (3, 0)],
    "jugador_pos": [0, 2],
    "objetivo_pos": [2, 1],
    "bloqueos": [("pared", 2, 1), ("pared", 1, 2), ("espejo", 1, 1), ("espejo", 3, 1)],
    "reflejos": 3,
    "movimientos": 12
},

# Nivel 15: Leyenda
{
    "figura_base": [(0, 0), (1, 0), (2, 0), (2, 1), (3, 1), (3, 2)],
    "jugador_pos": [0, 4],
    "objetivo_pos": [1, 0],
    "bloqueos": [("pared", 2, 2), ("espejo", 0, 3), ("espejo", 1, 2)],
    "reflejos": 2,
    "movimientos": 13
}
    ]

nivel_actual = 0
mensaje = ""
reflejada = False

def cargar_nivel(n):
    global figura_base, jugador_pos, jugador_figura, reflejada
    global objetivo_pos, objetivo_figura, bloqueos
    global reflejos_restantes, movimientos_restantes
    datos = niveles[n]
    figura_base = datos["figura_base"]
    jugador_pos = list(datos["jugador_pos"])
    jugador_figura = list(figura_base)
    objetivo_pos = datos["objetivo_pos"]
    objetivo_figura = [(-x, y) for (x, y) in figura_base]
    bloqueos = datos.get("bloqueos", [])
    reflejos_restantes = datos.get("reflejos", 3)
    movimientos_restantes = datos.get("movimientos", 30)
    reflejada = False

def figura_dentro_limites(figura, base_pos, limite_x):
    for dx, dy in figura:
        x = base_pos[0] + dx
        y = base_pos[1] + dy
        if x < 0 or x >= limite_x or y < 0 or y >= FILAS:
            return False
        if reflejada and x >= limite_x // 2:
            return False
        for tipo, bx, by in bloqueos:
            if tipo == "pared" and x == bx and y == by:
                return False
    return True

def dibujar_grid():
    for x in range(COLUMNAS + 1):
        pygame.draw.line(ventana, COLOR_LINEA, (MARGEN + x * TAM_CASILLA, MARGEN), (MARGEN + x * TAM_CASILLA, MARGEN + FILAS * TAM_CASILLA), 2)
    for y in range(FILAS + 1):
        pygame.draw.line(ventana, COLOR_LINEA, (MARGEN, MARGEN + y * TAM_CASILLA), (MARGEN + COLUMNAS * TAM_CASILLA, MARGEN + y * TAM_CASILLA), 2)

def dibujar_figura(figura, base_pos, color):
    for dx, dy in figura:
        x = base_pos[0] + dx
        y = base_pos[1] + dy
        pygame.draw.rect(ventana, color, (MARGEN + x * TAM_CASILLA + 2, MARGEN + y * TAM_CASILLA + 2, TAM_CASILLA - 4, TAM_CASILLA - 4), border_radius=8)

def dibujar_bloqueos():
    for tipo, x, y in bloqueos:
        color = COLOR_BLOQUEO if tipo == "pared" else COLOR_ESPEJO
        pygame.draw.rect(ventana, color, (MARGEN + x * TAM_CASILLA + 2, MARGEN + y * TAM_CASILLA + 2, TAM_CASILLA - 4, TAM_CASILLA - 4), border_radius=8)

def figuras_coinciden():
    jugador_real = [(jugador_pos[0] + dx, jugador_pos[1] + dy) for dx, dy in jugador_figura]
    objetivo_real = [(COLUMNAS // 2 + objetivo_pos[0] + dx, objetivo_pos[1] + dy) for dx, dy in objetivo_figura]
    jugador_real_trasladado = [(x + COLUMNAS // 2, y) for x, y in jugador_real]
    return set(jugador_real_trasladado) == set(objetivo_real)

cargar_nivel(nivel_actual)

while True:
    ventana.fill(COLOR_BG)
    pygame.draw.rect(ventana, COLOR_PANEL, (MARGEN, 0, 200, 100), border_radius=8)
    texto_reflejos = fuente.render(f"Reflejos: {reflejos_restantes}", True, COLOR_TEXTO)
    ventana.blit(texto_reflejos, (MARGEN + 10, 10))
    texto_movimientos = fuente.render(f"Movimientos: {movimientos_restantes}", True, COLOR_TEXTO)
    ventana.blit(texto_movimientos, (MARGEN + 10, 40))

    dibujar_grid()
    dibujar_bloqueos()

    pygame.draw.line(ventana, COLOR_LINEA, (MARGEN + (COLUMNAS // 2) * TAM_CASILLA, MARGEN), (MARGEN + (COLUMNAS // 2) * TAM_CASILLA, MARGEN + FILAS * TAM_CASILLA), 4)
    dibujar_figura(jugador_figura, jugador_pos, COLOR_FIGURA)
    dibujar_figura(objetivo_figura, [COLUMNAS // 2 + objetivo_pos[0], objetivo_pos[1]], COLOR_OBJETIVO)

    texto = fuente.render(f"Nivel {nivel_actual + 1} | R reflejar | E rotar | Espacio verificar | F reiniciar", True, COLOR_TEXTO)
    ventana.blit(texto, (MARGEN, ALTO - 40))

    if mensaje:
        resultado = fuente.render(mensaje, True, (0, 150, 0) if mensaje == "¡Correcto!" else (200, 0, 0))
        ventana.blit(resultado, (MARGEN, 100))

    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif evento.type == pygame.KEYDOWN:
            if evento.key == pygame.K_SPACE:
                if figuras_coinciden():
                    mensaje = "¡Correcto!"
                    pygame.display.update()
                    pygame.time.delay(1000)
                    nivel_actual = (nivel_actual + 1) % len(niveles)
                    cargar_nivel(nivel_actual)
                else:
                    mensaje = "¡Incorrecto!"
            elif evento.key == pygame.K_f:
                cargar_nivel(nivel_actual)
                mensaje = ""
            elif evento.key == pygame.K_r and reflejos_restantes > 0:
                reflejada = not reflejada
                jugador_figura = [(-x, y) for (x, y) in jugador_figura]
                reflejos_restantes -= 1
            elif evento.key == pygame.K_e:
                rotada = [(-dy, dx) for dx, dy in jugador_figura]
                if figura_dentro_limites(rotada, jugador_pos, COLUMNAS):
                    jugador_figura = rotada
                    movimientos_restantes -= 1
            else:
                nueva_pos = jugador_pos[:]
                if evento.key == pygame.K_LEFT:
                    nueva_pos[0] -= 1
                elif evento.key == pygame.K_RIGHT:
                    nueva_pos[0] += 1
                elif evento.key == pygame.K_UP:
                    nueva_pos[1] -= 1
                elif evento.key == pygame.K_DOWN:
                    nueva_pos[1] += 1
                if figura_dentro_limites(jugador_figura, nueva_pos, COLUMNAS):
                    jugador_pos = nueva_pos
                    movimientos_restantes -= 1

    pygame.display.flip()
    
