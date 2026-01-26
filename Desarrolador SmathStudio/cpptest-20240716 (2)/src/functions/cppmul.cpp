#include "stdafx.h"

LRESULT cppmul( cmplx & result, const cmplx & a, const cmplx & b )
{
    return ( result = a.cmplx() * b.cmplx(), mathcad::noerror );
}

definfo( cppmul, "a,b", "returns a * b.", ISCALAR2 );
