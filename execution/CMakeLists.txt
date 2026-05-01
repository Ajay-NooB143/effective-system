cmake_minimum_required(VERSION 3.14)
project(execution_engine LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# ── nlohmann/json (header-only, fetched at configure time) ──────────────────
include(FetchContent)
FetchContent_Declare(
    nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3
    GIT_SHALLOW    TRUE
)
FetchContent_MakeAvailable(nlohmann_json)

# ── System libraries: libcurl, OpenSSL, libzmq ──────────────────────────────
find_package(CURL    REQUIRED)
find_package(OpenSSL REQUIRED)

find_package(PkgConfig REQUIRED)
pkg_check_modules(ZMQ REQUIRED libzmq)

# ── Executable ───────────────────────────────────────────────────────────────
add_executable(execution_engine execution_engine.cpp)

target_include_directories(execution_engine PRIVATE ${ZMQ_INCLUDE_DIRS})

target_link_libraries(execution_engine PRIVATE
    nlohmann_json::nlohmann_json
    CURL::libcurl
    OpenSSL::Crypto
    ${ZMQ_LIBRARIES}
)
