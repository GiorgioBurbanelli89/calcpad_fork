#pragma once

#ifndef _VERSION_H_
#define _VERSION_H_

#include <cstdint>

// Hours.
#define HOURHI      ( __TIME__[0] == ' ' ? 0 : __TIME__[0] - '0' )
#define HOURLO      ( __TIME__[1] == ' ' ? 0 : __TIME__[1] - '0' )
#define HOUR        ( HOURHI * 10u + HOURLO )

// Minutes.
#define MINHI       ( __TIME__[3] == ' ' ? 0 : __TIME__[3] - '0' )
#define MINLO       ( __TIME__[4] == ' ' ? 0 : __TIME__[4] - '0' )
#define MIN         ( MINHI * 10u + MINLO )

// Seconds.
#define SECHI       ( __TIME__[6] == ' ' ? 0 : __TIME__[6] - '0' )
#define SECLO       ( __TIME__[7] == ' ' ? 0 : __TIME__[7] - '0' )
#define SEC         ( SECHI * 10u + SECLO )

// Day.
#define DAYHI       ( __DATE__[4] == ' ' ? 0 : __DATE__[4] - '0' )
#define DAYLO       ( __DATE__[5] - '0' )
#define DAY         ( DAYHI * 10u + DAYLO )

// Month.
#define MON (\
      __DATE__ [2] == 'n' ? (__DATE__ [1] == 'a' ? 1u : 6u) \
    : __DATE__ [2] == 'b' ? 2u \
    : __DATE__ [2] == 'r' ? (__DATE__ [0] == 'M' ? 3u : 4u) \
    : __DATE__ [2] == 'y' ? 5u \
    : __DATE__ [2] == 'l' ? 7u \
    : __DATE__ [2] == 'g' ? 8u \
    : __DATE__ [2] == 'p' ? 9u \
    : __DATE__ [2] == 't' ? 10u \
    : __DATE__ [2] == 'v' ? 11u \
    : 12u)

// Year.
#define YEARHI      ( ( ( __DATE__[7] - '0' ) * 10u ) + ( __DATE__[8] - '0' ) )
#define YEARLO      ( ( ( __DATE__[9] - '0' ) * 10u ) + ( __DATE__[10] - '0' ) )
#define YEAR        ( YEARHI * 100u + YEARLO )

#define MAJOR       (0)
#define MINOR       (1)

using namespace date;
using namespace std::chrono;

// Microsoft .Net style.
constexpr struct _VERSION
{
    uint8_t Major;
    uint8_t Minor;
    uint16_t Build;
    uint16_t Revision;

} Version =
{
    MAJOR, MINOR,
    ( sys_days( date::year_month_day( date::year{ YEAR } / MON / DAY ) ) - sys_days( date::year_month_day( date::year{ 2000 } / 1 / 1 ) ) ).count(),
    ( uint16_t ) ( hours( HOUR ) + minutes( MIN ) + seconds( SEC ) ).count() / 2u
};

#endif
