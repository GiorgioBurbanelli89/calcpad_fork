main.cpp и -lshlwapi должны быть последними в списке опций gcc.
Это связано с неявным подключением функций в модулях (инициализация вектора g_Functions).

Для сборки x32 и x64 версий нужно использовать соответствующее окружение mingw (scoop install mingw -a 32bit|64bit).

g++ -mdll -o cpptest32.dll -DWIN32 cppdiv.cpp cppinc.cpp cppmul.cpp cppnow.cpp cppstrlen.cpp cppsub.cpp cppsum.cpp cpptest.cpp logger.cpp mcadincl.cpp main.cpp -lshlwapi

g++ -mdll -o cpptest64.dll -D_WIN64 cppdiv.cpp cppinc.cpp cppmul.cpp cppnow.cpp cppstrlen.cpp cppsub.cpp cppsum.cpp cpptest.cpp logger.cpp mcadincl.cpp main.cpp -lshlwapi

Для определения разрядности полученного артефакта можно использовать file (scoop install file).
cpptest.dll: PE32 executable (DLL) (console) Intel 80386, for MS Windows, 16 sections
PE32  - x32
PE32+ - x64 

Порядок сборки:

cmake -G "Ninja" -B build
cd build
cmake --build . --target clean
cmake --build .