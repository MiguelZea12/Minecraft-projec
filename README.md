# 🎮 Minecraft Clone - Motor de Vóxeles 3D

Un motor de vóxeles inspirado en **Minecraft**, desarrollado desde cero usando **Python** y **OpenGL**. Este proyecto recrea la experiencia de construcción y exploración en un mundo de bloques proceduralmente generado.


## 🌟 Características Actuales

- ✅ **Generación procedural de terreno** con ruido Perlin
- ✅ **Sistema de física realista** con gravedad y colisiones
- ✅ **Modo Supervivencia y Creativo** intercambiables
- ✅ **Destrucción de bloques** (construcción temporalmente deshabilitada)
- ✅ **Sistema de salto** con altura balanceada (~1.25 bloques)
- ✅ **Sprint/Correr** para movimiento rápido
- ✅ **Respawn automático** al caer al vacío
- ✅ **HUD informativo** con FPS, modo, altura y estadísticas
- ✅ **Optimización de chunks** para rendimiento fluido
- ✅ **Sistema de cámara** con rotación libre

## 🎯 Inspiración

Este proyecto está inspirado en el legendario **Minecraft** de Mojang Studios, recreando la sensación de libertad y creatividad en un mundo de bloques infinito. Nuestro objetivo es entender y implementar los sistemas fundamentales que hacen que los juegos de vóxeles sean tan adictivos.

## 🎮 Controles

### Movimiento Básico
- **W, A, S, D** - Movimiento horizontal
- **Espacio** - Saltar (Supervivencia) / Volar hacia arriba (Creativo)
- **Shift Izq.** - Volar hacia abajo (solo Modo Creativo)
- **Ctrl Izq.** - Sprint/Correr (aumenta velocidad)

### Interacción con Bloques
- **Clic Izquierdo** - Destruir bloque
- **Clic Derecho** - ~~Cambiar modo~~ (temporalmente deshabilitado)

### Modos y Comandos
- **F** - Alternar entre Modo Supervivencia y Creativo
- **R** - Respawn en la superficie
- **Q, E** - Subir/Bajar (comandos de desarrollo)
- **Mouse** - Rotar cámara

### Modos de Juego
- **🏃 Supervivencia**: Gravedad activa, salto limitado, colisiones completas
- **✈️ Creativo**: Vuelo libre, sin gravedad, movimiento rápido

## 👥 Equipo de Desarrollo

Este proyecto ha sido desarrollado con mucho esfuerzo y dedicación por:

- **🔧 Alejandro Zea** - Desarrollador Principal
- **🎨 Juan Daza** - Desarrollador y Diseño
- **⚡ Aldair Toala** - Desarrollador y Optimización

## 🚀 Estado del Proyecto

> **¡Esto es solo el comienzo!** 
> 
> Actualmente tenemos una base sólida con física, generación de terreno y destrucción de bloques. Estamos trabajando en implementar muchas más características emocionantes.

### 🔜 Próximas Características

- 🏗️ Sistema de construcción completo
- 🎨 Texturas y materiales diversos
- 🌊 Agua y líquidos
- 🌤️ Sistema de clima y cielo dinámico
- 🎵 Audio y efectos de sonido
- 📦 HUB
- ⚔️ Sistema de herramientas

## 🛠️ Tecnologías Utilizadas

- **Python 3.10+** - Lenguaje principal
- **OpenGL** - Renderizado 3D
- **Pygame** - Gestión de ventanas y input
- **NumPy** - Cálculos matemáticos optimizados
- **PyGLM** - Matemáticas 3D y matrices
- **ModernGL** - Wrapper moderno de OpenGL

## 📋 Requisitos

```bash
pip install -r requirements.txt
```

## 🚀 Cómo Ejecutar

```bash
cd Minecraft-projec
python main.py
```

---

*Desarrollado con ❤️ por estudiantes apasionados por los gráficos 3D y la programación de videojuegos.*