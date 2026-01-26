#include "stdafx.h"

// Добавление описания функции.
const void * ( * CreateUserFunction )( HINSTANCE, FUNCTIONINFO * );

// Добавление таблицы сообщений об ошибках.
BOOL ( * CreateUserErrorMessageTable )( HINSTANCE, unsigned nErrorMessages, const char * ErrorMessageTable[] );

// Выделение памяти.
char * ( * MathcadAllocate )( unsigned size );

// Освобождение памяти.
void ( * MathcadFree )( char * address );

// Выделение памяти для массива при возвращении результата из библиотеки.
BOOL ( * MathcadArrayAllocate )( COMPLEXARRAY * const, unsigned rows, unsigned cols, BOOL allocateReal, BOOL allocateImag );

// Используется при освобождении выделенной памяти для возвращаемого массива в случае ошибки.
void ( * MathcadArrayFree )( COMPLEXARRAY * const );

// Вызывается для определения состояния прерывания вычислений пользователем.
// Может замедлить вычисления при частом вызове.
BOOL ( * isUserInterrupted )( void );

LRESULT mathcad::noerror = mathcad::error( NOERROR );


cmplx & cmplx::operator=( const std::complex<double> & cmplx )
{
    this->real = cmplx.real();
    this->imag = cmplx.imag();

    return * this;
}


cmplx & cmplx::operator=( std::complex<double> & cmplx )
{
    this->real = cmplx.real();
    this->imag = cmplx.imag();

    return * this;
}


std::complex<double> cmplx::cmplx() const
{
    return std::complex<double>( real, imag );
}


const cmplx operator+( const cmplx & left, const cmplx & right )
{
    cmplx tmp = left;

    tmp.real += right.real;
    tmp.imag += right.imag;

    return tmp;
}


const cmplx operator-( const cmplx & left, const cmplx & right )
{
    cmplx tmp = left;

    tmp.real -= right.real;
    tmp.imag -= right.imag;

    return tmp;
}


const cmplx operator+( const cmplx & left, const double & right )
{
    cmplx tmp = left;

    tmp.real += right;
    tmp.imag += 0;

    return tmp;
}


const cmplx operator-( const cmplx & left, const double & right )
{
    cmplx tmp = left;

    tmp.real -= right;
    tmp.imag -= 0;

    return tmp;
}


// Выполняет привязку с использованием интерфейса Mathcad User EFI.
bool mathcad::attach()
{
    // Загрузка пользовательской библиотеки Mathcad.
    auto hLib = LoadLibrary( "mcaduser.dll" );

    if ( hLib == NULL ) return false;

    // Динамическая привязка к функциям интерфейса Mathcad User EFI.
    CreateUserFunction = ( const void * (*)( HINSTANCE, FUNCTIONINFO * ) ) GetProcAddress( hLib, "CreateUserFunction" );
    CreateUserErrorMessageTable = ( BOOL (*)( HINSTANCE, unsigned, const char * * ) ) GetProcAddress( hLib, "CreateUserErrorMessageTable" );
    MathcadAllocate = ( char * (*)( unsigned ) ) GetProcAddress( hLib, "MathcadAllocate" );
    MathcadFree = ( void (*)( char * ) ) GetProcAddress( hLib, "MathcadFree" );
    MathcadArrayAllocate = ( BOOL(*)( COMPLEXARRAY * const, unsigned, unsigned, BOOL, BOOL ) ) GetProcAddress( hLib, "MathcadArrayAllocate" );
    MathcadArrayFree = ( void (*)( COMPLEXARRAY * const ) ) GetProcAddress( hLib, "MathcadArrayFree" );
    isUserInterrupted = ( BOOL (*)( void ) ) GetProcAddress( hLib, "isUserInterrupted" );

    return CreateUserFunction != NULL && CreateUserErrorMessageTable != NULL &&
        MathcadAllocate != NULL && MathcadFree != NULL &&
        MathcadArrayAllocate != NULL && MathcadArrayFree != NULL && isUserInterrupted != NULL;
}


// CreateUserFunction is called when the DLL is attaching to the address space of 
// the current process in order to register the user function.
bool mathcad::create( FUNCTIONINFO * info )
{
    return CreateUserFunction != nullptr && CreateUserFunction( g_Instance, info ) != nullptr;
}


// CreateUserErrorMessageTable is called when the DLL is attaching to the address space of the 
// current process in order to register the user error message table.
bool mathcad::create( const char * errors[], unsigned size )
{
    return CreateUserErrorMessageTable != nullptr && CreateUserErrorMessageTable( g_Instance, size, errors );
}


// Allocates memory for a COMPLEXARRAY of cols columns and rows rows. Sets the hReal, 
// hImag, rows and cols members of the argument array. 
bool mathcad::alloc( COMPLEXARRAY & cmplxarray, unsigned rows, unsigned cols, BOOL allocreal, BOOL allocimag )
{
    return MathcadAllocate != nullptr && MathcadArrayAllocate( & cmplxarray, rows, cols, allocreal, allocimag );
}


// Should be used to allocate memory inside the user function. Allocates a memory block 
// of a given size (in bytes) of memory.
bool mathcad::alloc( mcstr & text, unsigned size )
{
    return MathcadAllocate != nullptr && ( text.str = MathcadAllocate( size ), text.str != nullptr );
}


// Frees memory that was allocated by the MathcadArrayAllocate function to the 
// hReal and hImag members of the argument array.
void mathcad::free( COMPLEXARRAY & cmplxarray )
{
    MathcadArrayFree( & cmplxarray );
}


// Should be used to free memory allocated with MathcadAllocate. The argument 
// address points to the memory previously allocated with MathcadAllocate. A NULL 
// pointer argument is ignored.
void mathcad::free( mcstr & text )
{
    MathcadFree( text.str );
}


// errid - the number of the entry, in the array of error messages, to return as the error message.
LRESULT mathcad::error( unsigned errid )
{
    return error( errid, 0 );
}


// errid - the number of the entry, in the array of error messages, to return as the error message;
// argindx - the index of the argument around which a red circle must be placed.
// Note: If the argindx is zero the error message box (red circle) is placed under the function itself.
LRESULT mathcad::error( unsigned errid, unsigned argindx )
{
    return MAKELRESULT( errid, argindx );
}
