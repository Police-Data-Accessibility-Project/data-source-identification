cmake_minimum_required( VERSION 3.24.2 )
project( linklabel
         VERSION 0.0.1
         DESCRIPTION "Fast tool to label URLs according to a library of regexes."
         LANGUAGES CXX )

add_subdirectory( submodules/json )

add_executable( linklabel
    src/main.cpp
)

target_link_libraries( linklabel
    PRIVATE
        nlohmann_json::nlohmann_json )

set_target_properties( linklabel
    PROPERTIES    
        CXX_STANDARD 17
        CXX_STANDARD_REQUIRED ON )
