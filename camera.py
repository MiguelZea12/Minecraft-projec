from settings import *
from frustum import Frustum


class Camera:
    def __init__(self, position, yaw, pitch):
        self.position = glm.vec3(position)
        self.yaw = glm.radians(yaw)
        self.pitch = glm.radians(pitch)

        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.forward = glm.vec3(0, 0, -1)

        self.m_proj = glm.perspective(V_FOV, ASPECT_RATIO, NEAR, FAR)
        self.m_view = glm.mat4()

        self.frustum = Frustum(self)

    def update(self):
        self.update_vectors()
        self.update_view_matrix()

    def update_view_matrix(self):
        self.m_view = glm.lookAt(self.position, self.position + self.forward, self.up)

    def update_vectors(self):
        self.forward.x = glm.cos(self.yaw) * glm.cos(self.pitch)
        self.forward.y = glm.sin(self.pitch)
        self.forward.z = glm.sin(self.yaw) * glm.cos(self.pitch)

        self.forward = glm.normalize(self.forward)
        self.right = glm.normalize(glm.cross(self.forward, glm.vec3(0, 1, 0)))
        self.up = glm.normalize(glm.cross(self.right, self.forward))

    def rotate_pitch(self, delta_y):
        self.pitch -= delta_y
        self.pitch = glm.clamp(self.pitch, -PITCH_MAX, PITCH_MAX)

    def rotate_yaw(self, delta_x):
        self.yaw += delta_x

    def move_with_collision(self, direction, velocity, world):
        """
        Mueve la cámara en la dirección especificada con detección de colisiones mejorada.
        """
        movement = direction * velocity
        
        # Intentar movimiento completo primero
        new_position = self.position + movement
        if not world.check_collision(new_position):
            self.position = new_position
            return
        
        # Si hay colisión, intentar movimiento por cada eje por separado
        # Esto permite "deslizarse" a lo largo de las paredes
        
        # Movimiento en X
        test_pos = glm.vec3(self.position.x + movement.x, self.position.y, self.position.z)
        if not world.check_collision(test_pos):
            self.position.x = test_pos.x
        
        # Movimiento en Y
        test_pos = glm.vec3(self.position.x, self.position.y + movement.y, self.position.z)
        if not world.check_collision(test_pos):
            self.position.y = test_pos.y
        
        # Movimiento en Z
        test_pos = glm.vec3(self.position.x, self.position.y, self.position.z + movement.z)
        if not world.check_collision(test_pos):
            self.position.z = test_pos.z

    def move_left(self, velocity):
        self.position -= self.right * velocity

    def move_right(self, velocity):
        self.position += self.right * velocity

    def move_up(self, velocity):
        self.position += self.up * velocity

    def move_down(self, velocity):
        self.position -= self.up * velocity

    def move_forward(self, velocity):
        self.position += self.forward * velocity

    def move_back(self, velocity):
        self.position -= self.forward * velocity

    # Métodos con colisiones
    def move_left_with_collision(self, velocity, world):
        self.move_with_collision(-self.right, velocity, world)

    def move_right_with_collision(self, velocity, world):
        self.move_with_collision(self.right, velocity, world)

    def move_up_with_collision(self, velocity, world):
        self.move_with_collision(self.up, velocity, world)

    def move_down_with_collision(self, velocity, world):
        self.move_with_collision(-self.up, velocity, world)

    def move_forward_with_collision(self, velocity, world):
        self.move_with_collision(self.forward, velocity, world)

    def move_back_with_collision(self, velocity, world):
        self.move_with_collision(-self.forward, velocity, world)
