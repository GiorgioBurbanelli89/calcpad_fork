#include "stdafx.h"

LRESULT cppsub( cmplx & result, const cmplx & a, const cmplx & b )
{
    return ( result = a - b, mathcad::noerror );
}

definfo( cppsub, "a,b", "returns a - b.", ISCALAR2 );
