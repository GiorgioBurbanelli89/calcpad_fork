#include "stdafx.h"

LRESULT cppdiv( cmplx & result, const cmplx & a, const cmplx & b )
{
    if ( b.cmplx() == 0. ) return mathcad::error( ERROR_DIV_BY_ZERO, 2 );
   
    return ( result = a.cmplx() / b.cmplx(), mathcad::noerror );
}

definfo( cppdiv, "a,b", "returns a / b.", ISCALAR2 );
