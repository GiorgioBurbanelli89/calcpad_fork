#include "stdafx.h"

std::vector< FUNCTIONINFO * > g_Functions;

HINSTANCE g_Instance = NULL;

// Таблица сообщений об ошибках.
const char * g_ErrorMessageTable[] =
{
    "division by zero",     // error code: ERROR_DIV_BY_ZERO
    "can't create array",   // error code: ERROR_CANT_CREATE_ARRAY
    "wrong type of result"  // error code: ERROR_WRONG_TYPE_OF_RESULT
};


// Выполняет привязку с использованием интерфейса Mathcad User EFI.
void Attach()
{
    if ( !mathcad::attach() ) return;

#if defined( _WIN64 )
    log( "[INFO ] cpptest 64-bit %u.%u.%u.%u, %s %s", Version.Major, Version.Minor, Version.Build, Version.Revision, __DATE__, __TIME__ );
#else
    log( "[INFO ] cpptest 32-bit %u.%u.%u.%u, %s %s", Version.Major, Version.Minor, Version.Build, Version.Revision, __DATE__, __TIME__ );
#endif

    // Добавляем таблицу сообщений об ошибках.
    mathcad::create( g_ErrorMessageTable, sizeof( g_ErrorMessageTable ) / sizeof( LPCSTR ) );

    // Перебираем список функций и добавляем их в Mathcad.
    for ( auto func : g_Functions )
    {
        if ( !mathcad::create( func ) ) continue;

        log( "[INFO ] %s(%u) %s", func->lpstrName, func->nArgs, func->lpstrDescription );
    }

    log( "[INFO ] Total %u functions.", g_Functions.size() );
}

// Выполняет действия после завершения работы Mathcad.
void Detach()
{
    try
    {
        char buf[ MAX_PATH ];

        GetModuleFileName( g_Instance, buf, sizeof( buf ) );

        PathRemoveExtension( buf );

        std::string fname( buf );

        fname.append( ".log" );

        if ( static_cast<bool>( std::ifstream( fname.c_str() ) ) ) DeleteFile( fname.c_str() );
    }
    catch (...) {}
}


extern "C"
BOOL APIENTRY DllMain( HINSTANCE hDLL, DWORD dwReason, LPVOID lpReserved )
{
    // Выполняем действия в зависимости от причины вызова.
    switch( dwReason )
    {
        // Выполняем инициализацию для каждого процесса.
        case DLL_PROCESS_ATTACH: g_Instance = hDLL; Attach(); break;

        // Выполняем необходимую очистку.
        case DLL_PROCESS_DETACH: Detach(); break;
    }

    // Всегда завершаем успешно.
    return TRUE;
}
