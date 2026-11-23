# Visualizador de algoritmo de Tarjan (SCC)

GUI interactiva para la construcción de grafos y la visualización paso a paso del algoritmo de Tarjan.

Se combina una estructura programada en C++ (expuesta mediante `pybind11`) y la interfaz desarrollada en Python por medio de `PySide6`.


# Requisitos Previos
* Python: Versión 3.8 o superior.
* Compilador C++: Compatible con C++11 o superior (por ejemplo, MinGW-w64 en Windows, GCC en Linux o Clang en macOS).
* CMake: Versión 4.0 (según lo especificado en `CMakeLists.txt`; puede ajustarse si utilizas una versión anterior).
* Librerías de Python:
  * `pybind11`
  * `PySide6`
  * `networkx`
  * `matplotlib`
 
# Instalación y Compilación
1. Instalar dependencias de Python
```
pip install pybind11 PySide6 networkx matplotlib

```
2. Compilar el módulo de C++ (`graph_anim`)
El archivo `CMakeLists.txt` está configurado para colocar la librería compilada (`.pyd` en Windows o `.so` en Linux/macOS) directamente en el directorio raíz del proyecto:
```
cmake -B build
cmake --build build --config Release
```

  Nota para MinGW:  El archivo `animate_graph.py` incluye la línea `os.add_dll_directory(r"C:\msys64\mingw64\bin")` para localizar las DLL de tiempo de ejecución. Se debe actualizar o comentar dicha línea según corresponda en caso de usar Linux, macOS o tener otra ruta para MinGW.
