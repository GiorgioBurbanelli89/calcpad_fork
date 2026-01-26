#include "stdafx.h"

LRESULT cppsquare( COMPLEXARRAY & result, const cmplx & x, const cmplx & m )
{
    std::complex<double> xx = x.cmplx() * x.cmplx();

    // Return vector (row) 1x4.
    if ( m.cmplx() == 0. )
    {
        int rows = 1;
        int cols = 4;

        if ( !MathcadArrayAllocate( & result, rows, cols, TRUE, FALSE ) )
        {
            return mathcad::error( ERROR_CANT_CREATE_ARRAY, 0 );
        }

        for ( int n = 0; n < cols; n++ ) result.hReal[n][0] = xx.real();
    }

    // Return vector (col) 4x1.
    else if ( m.cmplx() == 1. )
    {
        int rows = 4;
        int cols = 1;

        if ( !MathcadArrayAllocate( & result, rows, cols, TRUE, FALSE ) )
        {
            return mathcad::error( ERROR_CANT_CREATE_ARRAY, 0 );
        }

        for ( int n = 0; n < rows; n++ ) result.hReal[0][n] = xx.real();
    }

    // Return matrix 4x4.
    else if ( m.cmplx() == 2. )
    {
        int rows = 4;
        int cols = 4;

        if ( !MathcadArrayAllocate( & result, rows, cols, TRUE, FALSE ) )
        {
            return mathcad::error( ERROR_CANT_CREATE_ARRAY, 0 );
        }

        for ( int n = 0; n < rows; n++ ) result.hReal[n][n] = xx.real();
    }

    else mathcad::error( ERROR_WRONG_TYPE_OF_RESULT, 2 );

    return mathcad::noerror;
}

definfo( cppsquare, "x,m", "returns x*x as row, col or matrix.", OARRAY_ISCALAR2 );