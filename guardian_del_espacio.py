import random
import pygame
import sys

VELOCIDAD_JUGADOR = 5
VELOCIDAD_BALA = 10
ANCHO, ALTO = 800, 600


pygame.init()
pantalla = pygame.display.set_mode((ANCHO, ALTO))
pygame.display.set_caption("Guardian del espacio")
reloj = pygame.time.Clock()


BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
fuente = pygame.font.Font(None, 74)
fuente_pequena = pygame.font.Font(None, 36)

class Jugador(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 50))
        self.image.fill((0, 128, 255))
        self.rect = self.image.get_rect(center=(ANCHO // 2, ALTO - 50))  
        self.velocidad = VELOCIDAD_JUGADOR
        self.balas = pygame.sprite.Group()

    def update(self, teclas):
        if teclas[pygame.K_w]: self.rect.y -= self.velocidad
        if teclas[pygame.K_s]: self.rect.y += self.velocidad
        if teclas[pygame.K_a]: self.rect.x -= self.velocidad
        if teclas[pygame.K_d]: self.rect.x += self.velocidad
        self.rect.clamp_ip(pantalla.get_rect())

    def disparar(self):
        bala = Bala(self.rect.centerx, self.rect.top)
        self.balas.add(bala)

class Enemigo(pygame.sprite.Sprite):
    def __init__(self, velocidad):
        super().__init__()
        self.image = pygame.Surface((40, 40))
        self.image.fill((255, 0, 0))
        self.rect = self.image.get_rect(center=(random.randint(0, ANCHO), -40))
        self.velocidad = velocidad

    def update(self):
        self.rect.y += self.velocidad
        if self.rect.top > ALTO:
            self.rect.y = random.randint(-50, -10)
            self.rect.x = random.randint(0, ANCHO)

class Jefe(pygame.sprite.Sprite):
    def __init__(self, nivel, jugador):
        super().__init__()
        self.image = pygame.Surface((100, 100))
        self.image.fill((255, 165, 0)) 
        self.rect = self.image.get_rect(center=(ANCHO // 2, 100))
        self.salud = 10 * nivel
        self.velocidad = 3
        self.balas = pygame.sprite.Group()
        self.retraso_disparo = 0
        self.retraso_maximo = 100
        self.direccion = 1
        self.jugador = jugador

    def update(self):
        self.rect.x += self.velocidad * self.direccion
        if self.rect.right >= ANCHO or self.rect.left <= 0:
            self.direccion *= -1

        if self.retraso_disparo <= 0:
            self.disparar()
            self.retraso_disparo = self.retraso_maximo
        else:
            self.retraso_disparo -= 1

        for bala in self.jugador.balas:
            if self.rect.colliderect(bala.rect):
                self.salud -= 1
                bala.kill()

    def disparar(self):
        bala = Bala(self.rect.centerx, self.rect.bottom, es_enemigo=True)  
        self.balas.add(bala)

class Bala(pygame.sprite.Sprite):
    def __init__(self, x, y, es_enemigo=False):
        super().__init__()
        self.image = pygame.Surface((5, 15))  
        self.image.fill((255, 0, 0) if es_enemigo else (0, 255, 0)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.velocidad = 5
        self.es_enemigo = es_enemigo 

    def update(self):
        if self.es_enemigo:
            self.rect.y += self.velocidad
        else: 
            self.rect.y -= self.velocidad

        if self.rect.top > ALTO or self.rect.bottom < 0:
            self.kill()

def menu_principal():
    while True:
        pantalla.fill(NEGRO)
        titulo_texto = fuente.render("Guardian del espacio", True, BLANCO)
        jugar_texto = fuente_pequena.render("1. Jugar", True, BLANCO)
        instrucciones_texto = fuente_pequena.render("2. Instrucciones", True, BLANCO)
        salir_texto = fuente_pequena.render("3. Salir", True, BLANCO)

        pantalla.blit(titulo_texto, (ANCHO // 2 - 150, ALTO // 4))
        pantalla.blit(jugar_texto, (ANCHO // 2 - 100, ALTO // 2))
        pantalla.blit(instrucciones_texto, (ANCHO // 2 - 100, ALTO // 2 + 50))
        pantalla.blit(salir_texto, (ANCHO // 2 - 100, ALTO // 2 + 100))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_1:
                    ciclo_juego(1)
                elif evento.key == pygame.K_2:
                    pantalla_instrucciones()
                elif evento.key == pygame.K_3:
                    pygame.quit()
                    sys.exit()

def pantalla_instrucciones():
    while True:
        pantalla.fill(NEGRO)
        instrucciones = [
            "INSTRUCCIONES\n",
            "Usa W, A, S, D para moverte.\n",
            "Presiona ESPACIO para disparar.",
            "Objetivo: elimina a los enemigos",
            "pero evita el contacto con ellos.\n",
            "Presiona M para volver al menú."
        ]

        for i, linea in enumerate(instrucciones):
            texto = fuente_pequena.render(linea, True, BLANCO)
            pantalla.blit(texto, (ANCHO // 2 - 200, ALTO // 4 + i * 40))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_m:
                    menu_principal()

def ciclo_juego(nivel):
    jugador = Jugador()
    todos_los_sprites = pygame.sprite.Group(jugador)
    enemigos = pygame.sprite.Group()
    velocidad_enemigos = 2 + nivel 
    num_enemigos = 5 + nivel * 2  

    for _ in range(num_enemigos):
        enemigo = Enemigo(velocidad_enemigos)
        enemigos.add(enemigo)
        todos_los_sprites.add(enemigo)

    juego_terminado = False
    nivel_completo = False
    jefe = None

    while True:
        pantalla.fill((0, 0, 0))

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    jugador.disparar()

        teclas = pygame.key.get_pressed()
        jugador.update(teclas)
        jugador.balas.update()
        enemigos.update()

        for bala in jugador.balas:
            enemigo_hit = pygame.sprite.spritecollide(bala, enemigos, True)
            if enemigo_hit:
                bala.kill()

        if pygame.sprite.spritecollideany(jugador, enemigos):
            juego_terminado = True

        if not enemigos and not jefe:
            jefe = Jefe(nivel,jugador)
            todos_los_sprites.add(jefe)
            nivel_completo = True

        if jefe:
            jefe.update()
            jefe.balas.update()

            for bala in jefe.balas:
                if jugador.rect.colliderect(bala.rect):
                    juego_terminado = True  

        todos_los_sprites.draw(pantalla)
        jugador.balas.draw(pantalla)
        if jefe:
            jefe.balas.draw(pantalla)

        if juego_terminado:
            pantalla_game_over()
            pygame.display.flip()
            pygame.time.delay(2000) 
            break
        elif nivel_completo and jefe.salud <= 0:  
            pantalla_nivel_completo(nivel)
            pygame.display.flip()
            pygame.time.delay(2000)
            ciclo_juego(nivel + 1)
            break

        pygame.display.flip()
        reloj.tick(60)

def pantalla_nivel_completo(nivel):
    pantalla.fill(NEGRO)
    texto = fuente.render(f"Nivel {nivel} Completo", True, BLANCO)
    pantalla.blit(texto, (ANCHO // 2 - 150, ALTO // 2))
    pygame.display.flip()
    pygame.time.delay(2000)

def pantalla_game_over():
    while True:
        pantalla.fill(NEGRO)
        game_over_texto = fuente.render("GAME OVER", True, (255, 0, 0))
        reiniciar_texto = fuente_pequena.render("Presiona R para reiniciar", True, BLANCO)
        menu_texto = fuente_pequena.render("Presiona M para ir al menú", True, BLANCO)

        pantalla.blit(game_over_texto, (ANCHO // 2 - 150, ALTO // 4))
        pantalla.blit(reiniciar_texto, (ANCHO // 2 - 150, ALTO // 2))
        pantalla.blit(menu_texto, (ANCHO // 2 - 150, ALTO // 2 + 50))

        pygame.display.flip()

        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    ciclo_juego(1)
                elif evento.key == pygame.K_m:
                    menu_principal()

menu_principal()
