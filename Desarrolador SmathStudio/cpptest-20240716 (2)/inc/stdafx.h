// stdafx.h : include file for standard system include files,
// or project specific include files that are used frequently, but
// are changed infrequently
#if !defined( _STDAFX_H_ )
#define _STDAFX_H_

#if _MSC_VER > 1000
#pragma once
#endif // _MSC_VER > 1000

// Insert your headers here
#define WIN32_LEAN_AND_MEAN		// Exclude rarely-used stuff from Windows headers

#define NOMINMAX
#define _CRT_SECURE_NO_WARNINGS

#include <windows.h>
#include <shlwapi.h>

// TODO: reference additional headers your program requires here
#include <vector>
#include <string>
#include <complex>
#include <chrono>
#include <ctime>
#include <iomanip>
#include <iostream>
#include <fstream>
#include <cstdio>

#include "date.h"
#include "version.h"
#include "mcadincl.h"

#define COMPLEX     COMPLEX_SCALAR
#define LPCOMPLEX   LPCOMPLEXSCALAR
#define ARRAY       COMPLEX_ARRAY
#define LPARRAY     LPCOMPLEXARRAY

#define ISTRING	    COMPLEX, 1, { STRING }
#define ISCALAR		COMPLEX, 1, { COMPLEX }
#define ISCALAR2    COMPLEX, 2, { COMPLEX, COMPLEX }
#define ISCALAR3    COMPLEX, 3, { COMPLEX, COMPLEX, COMPLEX }
#define ISCALAR4    COMPLEX, 4, { COMPLEX, COMPLEX, COMPLEX, COMPLEX }
#define ISCALAR5    COMPLEX, 5, { COMPLEX, COMPLEX, COMPLEX, COMPLEX, COMPLEX }
#define ISCALAR6    COMPLEX, 6, { COMPLEX, COMPLEX, COMPLEX, COMPLEX, COMPLEX, COMPLEX }
#define ISCALAR7    COMPLEX, 7, { COMPLEX, COMPLEX, COMPLEX, COMPLEX, COMPLEX, COMPLEX, COMPLEX }

#define ISCALAR_STRING      COMPLEX, 2, { COMPLEX, STRING }
#define ISCALAR_SCALAR_STRING_SCALAR      COMPLEX, 4, { COMPLEX, COMPLEX, STRING, COMPLEX }

#define OSTRING_ISTRING	    STRING, 1, { STRING }
#define OSTRING_ISCALAR	    STRING, 1, { COMPLEX }
#define OSTRING_ISCALAR2    STRING, 2, { COMPLEX, COMPLEX }

#define OARRAY_ISCALAR2     ARRAY, 2, { COMPLEX, COMPLEX }

#define ERROR_DIV_BY_ZERO           (1)
#define ERROR_CANT_CREATE_ARRAY     (2)
#define ERROR_WRONG_TYPE_OF_RESULT  (3)

#define definfo( name, params, descr, itypes ) FUNCTIONINFO name##_info = { ( g_Functions.push_back( & name##_info ), ( char * ) #name ), ( char * ) params, ( char * ) descr, ( LPCFUNCTION ) name, itypes }

extern HINSTANCE g_Instance;
extern std::vector< FUNCTIONINFO * > g_Functions;

void log( const char * format, ... );

#endif
