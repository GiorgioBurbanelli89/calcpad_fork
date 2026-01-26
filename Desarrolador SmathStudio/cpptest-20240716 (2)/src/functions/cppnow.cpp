#include "stdafx.h"

LRESULT cppnow( mcstr & result, const cmplx & dummy )
{
    std::ostringstream ss;

    auto t = time( NULL );

    ss << std::put_time( std::localtime( & t ), "%d-%m-%Y %H:%M:%S" );

    auto s = ss.str();

    mathcad::alloc( result, ( unsigned ) s.length() + 1 );

    ::strcpy_s( result.str, s.length() + 1, s.c_str() );

    return mathcad::noerror;
}

definfo( cppnow, "-", "returns local date and time.", OSTRING_ISCALAR );
