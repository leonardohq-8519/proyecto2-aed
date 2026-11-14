cmake_minimum_required(VERSION 4.0)
project(Proyecto2)

set(Python_FIND_VIRTUALENV FIRST)
find_package(Python COMPONENTS Interpreter Development REQUIRED)

message(STATUS "Python encontrado: ${Python_EXECUTABLE}")

execute_process(
        COMMAND "${Python_EXECUTABLE}" -m pybind11 --cmakedir
        OUTPUT_VARIABLE pybind11_DIR
        OUTPUT_STRIP_TRAILING_WHITESPACE
        RESULT_VARIABLE pybind11_RESULT
)

if(NOT pybind11_RESULT EQUAL 0)
    message(FATAL_ERROR "pybind11 no está instalado en ${Python_EXECUTABLE}. Ejecuta: ${Python_EXECUTABLE} -m pip install pybind11")
endif()

find_package(pybind11 CONFIG REQUIRED)

pybind11_add_module(graph_anim main.cpp)

if(MINGW)
    target_link_options(graph_anim PRIVATE -static-libgcc -static-libstdc++ -Wl,-Bstatic -lwinpthread -Wl,-Bdynamic)
endif()

set_target_properties(graph_anim PROPERTIES
        LIBRARY_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_SOURCE_DIR}"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_SOURCE_DIR}"
)
