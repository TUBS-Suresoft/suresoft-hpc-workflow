#include <catch2/catch_test_macros.hpp>

#include "Mapper2D.h"


TEST_CASE( "Mapper with zero dimensions - Should have zero size.", "[Mapper2DTest]" )
{
    Mapper2D sut(0,0);

    REQUIRE( sut.size() == 0 );
}

TEST_CASE( "Mapper with different dimensions - Should have proper size.", "[Mapper2DTest]" )
{
    constexpr Mapper2D sut(2, 3);

    REQUIRE( sut.size() == 6 );
}

TEST_CASE( "Mapper2D - Should return dimensions.", "[Mapper2DTest]" )
{
    constexpr Mapper2D sut(2, 3);

    REQUIRE( sut.nx() == 2 );
    REQUIRE( sut.ny() == 3 );
}

TEST_CASE( "Mapper with (nx = 2) - Should return x indices in scheme of (0 1 , 0 1 ,  ...)", "[Mapper2DTest]" )
{
    constexpr Mapper2D sut(2, 3);

    REQUIRE( sut.xForPos(0) == 0 );
    REQUIRE( sut.xForPos(1) == 1 );
    REQUIRE( sut.xForPos(2) == 0 );
    REQUIRE( sut.xForPos(3) == 1 );
}

TEST_CASE( "Mapper with (nx = 2) - Should return y indices in scheme of (0 0, 1 1, ...)", "[Mapper2DTest]" )
{
    constexpr Mapper2D sut(2, 3);

    REQUIRE( sut.yForPos(0) == 0 );
    REQUIRE( sut.yForPos(1) == 0 );
    REQUIRE( sut.yForPos(2) == 1 );
    REQUIRE( sut.yForPos(3) == 1 );
}

TEST_CASE( "1D Index from 2D Indices - Should show x as the fast index", "[Mapper2DTest]" )
{
    constexpr Mapper2D sut(2, 3);

    REQUIRE( sut.pos(0, 0) == 0 );
    REQUIRE( sut.pos(1, 0) == 1 );
    REQUIRE( sut.pos(0, 1) == 2 );
    REQUIRE( sut.pos(1, 1) == 3 );
    REQUIRE( sut.pos(0, 2) == 4 );
    REQUIRE( sut.pos(1, 2) == 5 );
}
