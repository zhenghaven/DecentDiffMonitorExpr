cmake_minimum_required(VERSION 3.1)
project(AttackPossTest)

set(CMAKE_CXX_STANDARD 20)

if (UNIX)
	set(THREADS_PREFER_PTHREAD_FLAG ON)
	find_package(Threads REQUIRED)
endif (UNIX)

add_executable(AttackPossTestDyn AttackPossTestDyn.cpp)
add_executable(AttackPossTestMC  AttackPossTestMC.cpp)

if (UNIX)
	target_link_libraries(AttackPossTestDyn PRIVATE Threads::Threads)
	target_link_libraries(AttackPossTestMC PRIVATE Threads::Threads)
endif (UNIX)
