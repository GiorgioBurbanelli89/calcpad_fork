#include "stdafx.h"

LRESULT cpptest( mcstr & result, const mcstr & text )
{    
    std::string s( "help: list, info, author, email, logfile" );

    if ( text.equals( "list" ) )
    {
        s.clear();

        for ( unsigned n = 0; n < g_Functions.size(); n++ )
        {
            auto info = g_Functions[n];

            s.append( info->lpstrName );

            if ( n < g_Functions.size() - 1 ) s.append( ", " );
        }
    }
    else if ( text.equals( "info" ) )
    {
        auto ver = std::to_string( Version.Major ) + "." + std::to_string( Version.Minor ) +
            "." + std::to_string( Version.Build ) + "." + std::to_string( Version.Revision );

        s.assign( "cpptest: " + ver + ", " __DATE__ " " __TIME__ );
    }
    else if ( text.equals( "author" ) )
    {
        s.assign( "Viacheslav N. Mezentsev" );
    }
    else if ( text.equals( "email" ) )
    {
        s.assign( "viacheslavmezentsev@ya.ru" );
    }
    else if ( text.equals( "logfile" ) )
    {
        char fname[ MAX_PATH ];

        GetModuleFileNameA( g_Instance, fname, MAX_PATH );

        PathRemoveExtensionA( fname );

        s.assign( fname );

        s.append( ".log" );
    }

    auto len = ::strlen( s.c_str() ) + 1u;

    mathcad::alloc( result, ( unsigned ) len );

    ::strcpy_s( result.str, len, s.c_str() );

    return mathcad::noerror;
}

definfo( cpptest, "cmd", "return info.", OSTRING_ISTRING );
