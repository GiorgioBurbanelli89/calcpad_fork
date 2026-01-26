#pragma once 

#ifndef _MCADINCL_H_
#define _MCADINCL_H_

#include <windows.h>
#include <complex>
                    
// complex scalar type
typedef struct tagCOMPLEXSCALAR
{
    double real;
    double imag;

    struct tagCOMPLEXSCALAR & operator=( const std::complex<double> & cmplx );
    struct tagCOMPLEXSCALAR & operator=( std::complex<double> & cmplx );

    std::complex<double> cmplx() const;

} COMPLEXSCALAR;
 
typedef COMPLEXSCALAR cmplx;

const cmplx operator+( const cmplx & left, const cmplx & right );
const cmplx operator-( const cmplx & left, const cmplx & right );

const cmplx operator+( const cmplx & left, const double & right );
const cmplx operator-( const cmplx & left, const double & right );

// this is the complex scalar type received from mathcad
typedef const COMPLEXSCALAR * const LPCCOMPLEXSCALAR; 

// this is the complex scalar type that should be returned to mathcad
typedef COMPLEXSCALAR * const LPCOMPLEXSCALAR; 

// complex array type
typedef struct tagCOMPLEXARRAY
{
    unsigned int rows;
    unsigned int cols;
    double **hReal; // hReal[cols][rows],  == NULL when the real part is zero 
    double **hImag; // hImag[cols][rows],  == NULL when the imaginary part is zero

} COMPLEXARRAY;
    
// this is the complex array type received from mathcad
typedef const COMPLEXARRAY * const LPCCOMPLEXARRAY;    

// this is the complex array type that should be returned to mathcad
typedef COMPLEXARRAY * const LPCOMPLEXARRAY;

typedef struct tagMCSTRING
{
	char * str;

    size_t len() const { return strlen( str ); }

    bool equals( const char * text ) const { return !strcmp( ( const char * ) str, text ); }

} MCSTRING;

typedef const MCSTRING * const LPCMCSTRING;
typedef MCSTRING * const LPMCSTRING;

typedef MCSTRING mcstr;

// types to be used in declaration of the function's
// arguments and of the return value
#define COMPLEX_SCALAR  1
#define COMPLEX_ARRAY   2
#define STRING			8


// File name variables. These are passed as const char *pointers
// if the string doesn't look like it has a path in it then 
// the current working directory will be prepended to the string 
// before it is passed to the user function.

// your function will be passed a const char * pointer
#define INFILE			13
// an OUTFILE is like an INFILE except it allows you
// to put your function on the left side of a := like
// the WRITEPRN() builtin
#define OUTFILE			14

// use this structure to create a function
#define MAX_ARGS        10

typedef LRESULT ( * LPCFUNCTION )( void * const, const void * const, ... );    

typedef struct tagFUNCTIONINFO
{
    char * lpstrName;
    char * lpstrParameters; 
    char * lpstrDescription;
    LPCFUNCTION lpfnMyCFunction;
    long unsigned int returnType;
    unsigned int nArgs;
    long unsigned int argType[ MAX_ARGS ];

} FUNCTIONINFO;

extern const void * ( * CreateUserFunction )( HINSTANCE, FUNCTIONINFO * );

extern BOOL ( * CreateUserErrorMessageTable )( HINSTANCE, unsigned nErrorMessages, const char * ErrorMessageTable[] );

// Memory management routines.
extern char * ( * MathcadAllocate )( unsigned size );

extern void ( * MathcadFree )( char * address );

// Array allocation -- should be used to allocate return array.
extern BOOL ( * MathcadArrayAllocate )( COMPLEXARRAY * const, unsigned rows, unsigned cols, BOOL allocateReal, BOOL allocateImag );

// should be used to free ( in case of an error ) Mathcad allocated return array
extern void ( * MathcadArrayFree )( COMPLEXARRAY * const );

// this routine can be used to find out whether the user has attempted to interrupt
// Mathcad this routine slows down the execution -- so use judiciously
extern BOOL ( * isUserInterrupted )( void );

class mathcad
{
public:
    // Return MAKELRESULT( NOERROR, NULL ).
    static LRESULT noerror;

    static bool attach();

    // CreateUserFunction is called when the DLL is attaching to the address space of 
    // the current process in order to register the user function.
    static bool create( FUNCTIONINFO * info );

    // CreateUserErrorMessageTable is called when the DLL is attaching to the address space of the 
    // current process in order to register the user error message table.
    static bool create( const char * errors[], unsigned size );

    // Allocates memory for a COMPLEXARRAY of cols columns and rows rows. Sets the hReal, 
    // hImag, rows and cols members of the argument array. 
    static bool alloc( COMPLEXARRAY & cmplxarray, unsigned rows, unsigned cols, BOOL allocreal, BOOL allocimag );

    // Should be used to allocate memory inside the user function. Allocates a memory block 
    // of a given size (in bytes) of memory.
    static bool alloc( mcstr & text, unsigned size );

    // Frees memory that was allocated by the MathcadArrayAllocate function to the 
    // hReal and hImag members of the argument array.
    static void free( COMPLEXARRAY & cmplxarray );

    // Should be used to free memory allocated with MathcadAllocate. The argument 
    // address points to the memory previously allocated with MathcadAllocate. A NULL 
    // pointer argument is ignored.
    static void free( mcstr & text );    

    // errid - the number of the entry, in the array of error messages, to return as the error message.
    static LRESULT error( unsigned errid );

    // errid - the number of the entry, in the array of error messages, to return as the error message;
    // argindx - the index of the argument around which a red circle must be placed.
    // Note: If the argindx is zero the error message box (red circle) is placed under the function itself.
    static LRESULT error( unsigned errid, unsigned argindx );
};

#endif
