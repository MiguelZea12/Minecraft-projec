import pygame as pg
from camera import Camera
from settings import *


class Player(Camera):
    def __init__(self, app, position=PLAYER_POS, yaw=-90, pitch=0):
        self.app = app
        
        # Variables de física
        self.velocity = glm.vec3(0.0)  # Velocidad actual del jugador
        self.on_ground = True  # Iniciar como si estuviera en el suelo
        self.can_jump = True   # Si el jugador puede saltar
        self.creative_mode = False  # Iniciar en modo supervivencia
        self.jump_key_held = False  # Para controlar saltos repetidos
        self.max_jump_height = 0.0  # Para medir altura máxima de salto (debug)
        
        # Posición de los pies del jugador (para colisiones)
        self.feet_position = glm.vec3(position)
        
        # Ajustar la posición inicial para que los ojos estén a la altura correcta
        eye_position = glm.vec3(position.x, position.y + PLAYER_EYE_HEIGHT, position.z)
        super().__init__(eye_position, yaw, pitch)
        
        print(f"DEBUG: Player initialized at feet_pos: {self.feet_position}, eye_pos: {self.position}")

    def update(self):
        self.apply_physics()
        self.keyboard_control()
        self.mouse_control()
        super().update()

    def apply_physics(self):
        """Aplica gravedad y otras físicas de Minecraft"""
        world = self.app.scene.world
        
        # No aplicar física en modo creativo
        if self.creative_mode:
            return
        
        # Debug: Verificar estado inicial
        # if hasattr(self, '_debug_count') and self._debug_count < 5:
        #     print(f"DEBUG: Physics - on_ground: {self.on_ground}, velocity.y: {self.velocity.y}, feet_pos.y: {self.feet_position.y}")
        #     self._debug_count += 1
        # elif not hasattr(self, '_debug_count'):
        #     self._debug_count = 0
        
        # Protección contra caída infinita - teletransportar a la superficie si cae muy abajo
        if self.feet_position.y < -50:  # Si cae muy abajo
            world.spawn_player_on_surface(self)
            return
        
        # Aplicar gravedad con curva más natural (como Minecraft)
        if not self.on_ground:
            # Gravedad progresiva: más suave al principio, más fuerte después
            gravity_multiplier = 1.0
            
            if self.velocity.y > 0.015:  # Subiendo muy rápido
                gravity_multiplier = 0.7  # Gravedad reducida para subida más suave
            elif self.velocity.y > 0:  # Subiendo lentamente
                gravity_multiplier = 0.85  # Gravedad ligeramente reducida
            elif self.velocity.y < -0.02:  # Cayendo rápido
                gravity_multiplier = 1.0  # Gravedad aumentada para aceleración natural
            
            self.velocity.y -= GRAVITY * gravity_multiplier * self.app.delta_time
            
            # Limitar velocidad de caída (velocidad terminal)
            if self.velocity.y < -TERMINAL_VELOCITY:
                self.velocity.y = -TERMINAL_VELOCITY
        
        # Actualizar posición de los pies basada en la posición de los ojos
        self.feet_position = glm.vec3(self.position.x, self.position.y - PLAYER_EYE_HEIGHT, self.position.z)
        
        # Aplicar movimiento vertical (gravedad/salto)
        if self.velocity.y != 0:
            new_feet_pos = glm.vec3(self.feet_position.x, self.feet_position.y + self.velocity.y * self.app.delta_time, self.feet_position.z)
            
            if not world.check_collision(new_feet_pos):
                self.feet_position.y = new_feet_pos.y
                self.position.y = self.feet_position.y + PLAYER_EYE_HEIGHT
                self.on_ground = False
                
                # Tracking de altura máxima de salto
                if hasattr(self, 'jump_start_y'):
                    current_height = self.feet_position.y - self.jump_start_y
                    if current_height > self.max_jump_height:
                        self.max_jump_height = current_height
            else:
                # Colisión vertical
                if self.velocity.y < 0:  # Cayendo
                    self.on_ground = True
                    self.can_jump = True
                elif self.velocity.y > 0:  # Golpeando el techo
                    # Reducir velocidad cuando golpea el techo
                    self.velocity.y = 0
                self.velocity.y = 0
        
        # Verificar si sigue en el suelo
        ground_check_pos = glm.vec3(self.feet_position.x, self.feet_position.y - 0.05, self.feet_position.z)
        if not world.check_collision(ground_check_pos):
            # Solo cambiar a no en suelo si no está ya cayendo
            if self.velocity.y <= 0.001:  # Pequeña tolerancia para evitar problemas de precisión
                self.on_ground = False

    def jump(self):
        """Hacer que el jugador salte"""
        if self.on_ground and self.can_jump:
            self.velocity.y = JUMP_STRENGTH
            self.on_ground = False
            self.can_jump = False
            # Impulso muy suave hacia arriba para separar del suelo
            self.feet_position.y += 0.03
            self.position.y = self.feet_position.y + PLAYER_EYE_HEIGHT
            # Registrar posición inicial para medir altura (ajustada por el impulso)
            self.jump_start_y = self.feet_position.y - 0.03
            self.max_jump_height = 0.0

    def move_horizontally(self, direction, speed):
        """Mover al jugador horizontalmente con colisiones"""
        world = self.app.scene.world
        
        # Crear vector de movimiento horizontal (sin Y)
        movement = glm.vec3(direction.x, 0, direction.z) * speed * self.app.delta_time
        
        # Probar movimiento completo primero
        new_feet_position = self.feet_position + movement
        if not world.check_collision(new_feet_position):
            self.feet_position = new_feet_position
            self.position.x = self.feet_position.x
            self.position.z = self.feet_position.z
            return
        
        # Si hay colisión, intentar movimiento por eje separado para permitir deslizamiento
        
        # Intentar movimiento en X solamente
        new_pos_x = glm.vec3(self.feet_position.x + movement.x, self.feet_position.y, self.feet_position.z)
        if not world.check_collision(new_pos_x):
            self.feet_position.x = new_pos_x.x
            self.position.x = self.feet_position.x
        
        # Intentar movimiento en Z solamente
        new_pos_z = glm.vec3(self.feet_position.x, self.feet_position.y, self.feet_position.z + movement.z)
        if not world.check_collision(new_pos_z):
            self.feet_position.z = new_pos_z.z
            self.position.z = self.feet_position.z

    def handle_event(self, event):
        # adding and removing voxels with clicks
        if event.type == pg.MOUSEBUTTONDOWN:
            voxel_handler = self.app.scene.world.voxel_handler
            if event.button == 1:
                voxel_handler.set_voxel()
            if event.button == 3:
                voxel_handler.switch_mode()
        
        # Alternar modo creativo con F
        if event.type == pg.KEYDOWN and event.key == pg.K_f:
            self.creative_mode = not self.creative_mode
            if self.creative_mode:
                self.velocity.y = 0  # Detener caída al activar modo creativo
        
        # Respawn en la superficie con R
        if event.type == pg.KEYDOWN and event.key == pg.K_r:
            self.app.scene.world.spawn_player_on_surface(self)

    def mouse_control(self):
        mouse_dx, mouse_dy = pg.mouse.get_rel()
        if mouse_dx:
            self.rotate_yaw(delta_x=mouse_dx * MOUSE_SENSITIVITY)
        if mouse_dy:
            self.rotate_pitch(delta_y=mouse_dy * MOUSE_SENSITIVITY)

    def keyboard_control(self):
        key_state = pg.key.get_pressed()
        
        # Determinar velocidad según el modo y si está corriendo
        if self.creative_mode:
            speed = PLAYER_SPEED_CREATIVE * self.app.delta_time
            if key_state[pg.K_LCTRL]:  # Sprint en creativo para mayor velocidad
                speed *= 2
        else:
            # Modo supervivencia: velocidad normal o sprint
            if key_state[pg.K_LCTRL]:  # Correr con Ctrl izquierdo
                base_speed = PLAYER_SPEED_SPRINT
            else:
                base_speed = PLAYER_SPEED
            speed = base_speed * self.app.delta_time
        
        # Movimiento horizontal
        movement_vector = glm.vec3(0.0)
        
        if key_state[pg.K_w]:
            movement_vector += glm.vec3(self.forward.x, 0, self.forward.z)
        if key_state[pg.K_s]:
            movement_vector -= glm.vec3(self.forward.x, 0, self.forward.z)
        if key_state[pg.K_d]:
            movement_vector += glm.vec3(self.right.x, 0, self.right.z)
        if key_state[pg.K_a]:
            movement_vector -= glm.vec3(self.right.x, 0, self.right.z)
        
        # Si hay movimiento, aplicarlo
        if glm.length(movement_vector) > 0:
            movement_vector = glm.normalize(movement_vector)
            
            # En modo creativo, mover directamente
            if self.creative_mode:
                self.position += movement_vector * speed
                self.feet_position = glm.vec3(self.position.x, self.position.y - PLAYER_EYE_HEIGHT, self.position.z)
            else:
                # En modo supervivencia, usar la velocidad determinada arriba
                self.move_horizontally(movement_vector, base_speed)
        
        # Salto (o volar hacia arriba en modo creativo)
        if key_state[pg.K_SPACE]:
            if self.creative_mode:
                self.position.y += speed
                self.feet_position.y = self.position.y - PLAYER_EYE_HEIGHT
            else:
                # Solo saltar si no estaba presionado antes (evitar spam de saltos)
                if not self.jump_key_held and self.on_ground:
                    self.jump()
                self.jump_key_held = True
        else:
            self.jump_key_held = False
        
        # Volar hacia abajo en modo creativo
        if key_state[pg.K_LSHIFT] and self.creative_mode:
            self.position.y -= speed
            self.feet_position.y = self.position.y - PLAYER_EYE_HEIGHT
        
        # Comandos de desarrollo (Q/E para subir/bajar) - velocidad reducida
        dev_speed = PLAYER_SPEED * self.app.delta_time
        if key_state[pg.K_q]:
            self.position.y -= dev_speed
            self.feet_position.y = self.position.y - PLAYER_EYE_HEIGHT
        if key_state[pg.K_e]:
            self.position.y += dev_speed
            self.feet_position.y = self.position.y - PLAYER_EYE_HEIGHT

    def move_vertically(self, speed):
        """Movimiento vertical directo (para modo creativo)"""
        world = self.app.scene.world
        vertical_movement = speed * self.app.delta_time
        
        new_pos = glm.vec3(self.feet_position.x, self.feet_position.y + vertical_movement, self.feet_position.z)
        if not world.check_collision(new_pos):
            self.feet_position.y = new_pos.y
            self.position.y = self.feet_position.y + PLAYER_EYE_HEIGHT
