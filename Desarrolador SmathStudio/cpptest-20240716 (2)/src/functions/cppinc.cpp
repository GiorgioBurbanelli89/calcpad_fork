#include "stdafx.h"

LRESULT cppinc( cmplx & result, const cmplx & x )
{
    return ( result = x + 1., mathcad::noerror );
}

definfo( cppinc, "x", "returns x + 1.", ISCALAR );
