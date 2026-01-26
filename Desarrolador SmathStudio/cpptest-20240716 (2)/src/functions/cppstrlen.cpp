#include "stdafx.h"

LRESULT cppstrlen( cmplx & result, const mcstr & text )
{
    return ( result.real = ( double ) text.len(), mathcad::noerror );
}

definfo( cppstrlen, "s", "returns length of string s.", ISTRING );
