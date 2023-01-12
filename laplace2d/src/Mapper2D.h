#ifndef MAPPER_2D_H
#define MAPPER_2D_H

#include <cstddef>

#ifndef __host__
#define __host__
#endif
#ifndef __device__
#define __device__
#endif

class Mapper2D
{
public:
    constexpr Mapper2D(size_t x, size_t y)
     : _nx(x), _ny(y), _size(x * y) 
    {

    }

    constexpr size_t size() const 
    { 
        return _size; 
    }

    constexpr __host__ __device__ size_t pos(size_t x, size_t y) const 
    {
         return _nx * y + x; 
    }

    constexpr __host__ __device__ size_t xForPos(size_t pos) const 
    {
         return pos % _nx;
    }

    constexpr __host__ __device__ size_t yForPos(size_t pos) const 
    {
         return pos / _nx; 
    }

    constexpr __host__ __device__ size_t nx() const
    {
        return _nx;
    }

    constexpr __host__ __device__ size_t ny() const
    {
        return _ny;
    }
    
private:
    size_t _nx;
    size_t _ny;
    size_t _size;

};


#endif
