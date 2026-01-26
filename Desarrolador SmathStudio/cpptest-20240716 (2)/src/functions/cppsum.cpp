#include "stdafx.h"

LRESULT cppsum( cmplx & result, const cmplx & a, const cmplx & b )
{   
    return ( result = a + b, mathcad::noerror );
}

definfo( cppsum, "a,b", "returns a + b.", ISCALAR2 );
