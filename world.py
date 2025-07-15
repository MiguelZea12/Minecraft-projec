from settings import *
from world_objects.chunk import Chunk
from voxel_handler import VoxelHandler


class World:
    def __init__(self, app):
        self.app = app
        self.chunks = [None for _ in range(WORLD_VOL)]
        self.voxels = np.empty([WORLD_VOL, CHUNK_VOL], dtype='uint8')
        self.build_chunks()
        self.build_chunk_mesh()
        self.voxel_handler = VoxelHandler(self)
        
        # Colocar al jugador en la superficie después de generar el terreno
        self.spawn_player_on_surface(self.app.player)

    def update(self):
        self.voxel_handler.update()

    def get_voxel_id(self, world_pos):
        """
        Obtiene el ID del vóxel en una posición mundial específica.
        Retorna 0 si la posición está vacía o fuera de los límites.
        """
        x, y, z = int(world_pos.x), int(world_pos.y), int(world_pos.z)
        
        # Verificar límites del mundo
        if (x < 0 or x >= WORLD_W * CHUNK_SIZE or 
            y < 0 or y >= WORLD_H * CHUNK_SIZE or 
            z < 0 or z >= WORLD_D * CHUNK_SIZE):
            return 0
        
        # Calcular índices de chunk y vóxel
        chunk_x = x // CHUNK_SIZE
        chunk_y = y // CHUNK_SIZE
        chunk_z = z // CHUNK_SIZE
        
        local_x = x % CHUNK_SIZE
        local_y = y % CHUNK_SIZE
        local_z = z % CHUNK_SIZE
        
        # Calcular índice del chunk
        chunk_index = chunk_x + WORLD_W * chunk_z + WORLD_AREA * chunk_y
        
        if chunk_index < 0 or chunk_index >= len(self.chunks):
            return 0
            
        chunk = self.chunks[chunk_index]
        if chunk is None:
            return 0
        
        # Calcular índice del vóxel local
        voxel_index = local_x + CHUNK_SIZE * local_z + CHUNK_AREA * local_y
        
        if voxel_index < 0 or voxel_index >= len(chunk.voxels):
            return 0
            
        return chunk.voxels[voxel_index]

    def is_voxel_solid(self, world_pos):
        """
        Verifica si hay un vóxel sólido en la posición dada.
        """
        voxel_id = self.get_voxel_id(world_pos)
        return voxel_id != 0  # 0 significa vacío
    
    def check_collision(self, position, size=None, height=None):
        """
        Verifica colisión con vóxeles para una caja de colisión del jugador.
        position: posición de los pies del jugador
        size: radio de la caja de colisión del jugador
        height: altura del jugador
        """
        if size is None:
            size = PLAYER_COLLISION_SIZE
        if height is None:
            height = PLAYER_HEIGHT
            
        half_size = size / 2
        
        # Calcular los límites de la caja de colisión
        min_x = int(position.x - half_size)
        max_x = int(position.x + half_size)
        min_y = int(position.y)
        max_y = int(position.y + height - 0.1)  # Pequeño margen para evitar problemas de precisión
        min_z = int(position.z - half_size)
        max_z = int(position.z + half_size)
        
        # Verificar todos los vóxeles que intersectan con la caja de colisión
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                for z in range(min_z, max_z + 1):
                    if self.is_voxel_solid(glm.vec3(x, y, z)):
                        return True
        return False

    def is_on_ground(self, position, size=None):
        """
        Verifica si el jugador está en el suelo
        """
        if size is None:
            size = PLAYER_COLLISION_SIZE
            
        half_size = size / 2
        
        # Verificar un poco debajo de los pies del jugador
        check_y = int(position.y - 0.1)
        
        min_x = int(position.x - half_size)
        max_x = int(position.x + half_size)
        min_z = int(position.z - half_size)
        max_z = int(position.z + half_size)
        
        for x in range(min_x, max_x + 1):
            for z in range(min_z, max_z + 1):
                if self.is_voxel_solid(glm.vec3(x, check_y, z)):
                    return True
        return False

    def build_chunks(self):
        for x in range(WORLD_W):
            for y in range(WORLD_H):
                for z in range(WORLD_D):
                    chunk = Chunk(self, position=(x, y, z))

                    chunk_index = x + WORLD_W * z + WORLD_AREA * y
                    self.chunks[chunk_index] = chunk

                    # put the chunk voxels in a separate array
                    self.voxels[chunk_index] = chunk.build_voxels()

                    # get pointer to voxels
                    chunk.voxels = self.voxels[chunk_index]

    def build_chunk_mesh(self):
        for chunk in self.chunks:
            chunk.build_mesh()

    def render(self):
        for chunk in self.chunks:
            chunk.render()

    def find_surface_height(self, x, z):
        """
        Encuentra la altura de la superficie en las coordenadas x, z dadas.
        Retorna la altura Y del primer bloque sólido desde arriba.
        """
        max_height = WORLD_H * CHUNK_SIZE - 1
        
        # Buscar desde arriba hacia abajo
        for y in range(max_height, -1, -1):
            if self.is_voxel_solid(glm.vec3(x, y, z)):
                print(f"DEBUG: Found surface at y={y+1} for position ({x}, {z})")
                return y + 1  # Retornar la posición encima del bloque sólido
        
        # Si no se encuentra superficie, retornar nivel del mar o una altura por defecto
        default_height = CHUNK_SIZE // 2
        print(f"DEBUG: No surface found, using default height {default_height}")
        return default_height

    def spawn_player_on_surface(self, player):
        """
        Coloca al jugador en la superficie del terreno en su posición actual.
        """
        x = int(player.feet_position.x)
        z = int(player.feet_position.z)
        
        surface_y = self.find_surface_height(x, z)
        
        print(f"DEBUG: Spawning player at ({x}, {surface_y}, {z})")
        
        # Actualizar posición del jugador
        player.feet_position.y = surface_y
        player.position.y = surface_y + PLAYER_EYE_HEIGHT
        player.velocity.y = 0  # Detener cualquier movimiento vertical
        player.on_ground = True
        player.can_jump = True
        
        # Asegurar que el jugador no esté atascado en el suelo
        # Verificar si hay colisión y ajustar si es necesario
        if self.check_collision(player.feet_position):
            print(f"DEBUG: Player stuck in ground, moving up")
            player.feet_position.y = surface_y + 1
            player.position.y = surface_y + 1 + PLAYER_EYE_HEIGHT
