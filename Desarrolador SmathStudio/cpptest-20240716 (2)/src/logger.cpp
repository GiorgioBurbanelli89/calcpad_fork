#include "stdafx.h"

static char buf[ 4 * 1024 ];

bool iswritable( const char * file_path )
{
    FILE * file_handle;
    errno_t file_open_error;

    if ( ( file_open_error = fopen_s( & file_handle, file_path, "a" ) ) != 0 )
    {
        return false;
    }

    fclose( file_handle );

    return true;
}

void log( const char * format, ... )
{
    if ( g_Instance == NULL ) return;

    try
    {
        //TODO: differ paths for mathcad and smath
        //dwSize = ::ExpandEnvironmentStrings(str, NULL, 0);
        //if ( dwSize == 0 ) return;
        //pBuff=CString::GetBuffer()
        //::ExpandEnvironmentStrings(str, pBuff, dwSize)
        GetModuleFileName( g_Instance, buf, sizeof( buf ) );

        PathRemoveExtension( buf );

        std::string fname( buf );

        fname.append( ".log" );

        if ( !iswritable( fname.c_str() ) ) return;

        // TODO: Узнать, создаётся ли файл с атрибутом 'a+'.
        auto fp = fopen( fname.c_str(), ( static_cast<bool>( std::ifstream( fname.c_str() ) ) ? "a+" : "w" ) );

        if ( fp == NULL ) return;

        auto t = time( NULL );

        auto nowtm = localtime( & t );

        strftime( buf, sizeof( buf ), "%Y-%m-%d %H:%M:%S", nowtm );

        fprintf( fp, "%s ", buf );

        va_list args;

        va_start( args, format );
        vsnprintf( buf, sizeof( buf ) - 1, format, args );
        va_end( args );

        buf[ sizeof( buf ) - 1 ] = '\0';

        fprintf( fp, "%s ", buf );

        fputc( '\n', fp );

        fclose( fp );
    }
    catch (...) {}
}
