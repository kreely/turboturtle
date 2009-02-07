/********************************************/
/* Turbo Turtle CArray Wrapper Class        */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/********************************************/

#include <stdlib.h>
#include <stdarg.h>
#include <memory.h>

template <typename T, int Dim>
class CArray
{ };

template <typename T>
class CArray<T,1>
{
  public:
    CArray() : pData(NULL), iSize1(0), iStart(0) {}

    // default constuctor for a 0-filled array
    CArray(int size, int start) : iSize1(size), iStart(start)
    {
      this->pData = new T[size];
      for (int i = 0; i < size; i++)
        this->pData[i] = 0.0;
    }

    // destructor
    ~CArray() { delete [] this->pData; }
    // copy constructor
    CArray(const CArray<T,1> &ref) : iSize1(ref.iSize1), iStart(ref.iStart)
    {
      this->pData = new T[this->iSize1];
      memcpy(this->pData, ref.pData, this->iSize1 * sizeof(T));
    }
    // assignment operator
    CArray<T,1> & operator=(const CArray<T,1> &ref)
    {
      // check for initializing from self
      if (this == &ref)
        return *this;
      // otherwise free any memory I may be holding on to
      if (this->pData)
        delete [] this->pData;
      // then construct myself from the input object
      this->iSize1 = ref.iSize1;
      this->iStart = ref.iStart;
      this->pData = new T[this->iSize1];
      memcpy(this->pData, ref.pData, this->iSize1 * sizeof(T));
      return *this;
    }

    T Get(int idx)
    {
      if (idx < this->iStart || idx >= this->iStart + this->iSize1)
        return 0.0;
      return pData[idx - this->iStart];
    }
    void Set(T value, int idx)
    {
      if (idx >= this->iStart && idx < this->iStart + this->iSize1)
        pData[idx - this->iStart] = value;
    }
    
  private:
    T   *pData;
    int  iSize1;
    int  iStart;
};

template <typename T>
class CArray<T,2>
{
  public:
    CArray() : pData(NULL), iSize1(0), iSize2(0) {}

    // default constuctor for a 0-filled array
    CArray(int size1, int size2) : iSize1(size1), iSize2(size2)
    {
      this->pData = new T[size1*size2];
      for (int i = 0; i < size1*size2; i++)
        this->pData[i] = 0.0;
    }

    // destructor
    ~CArray() { delete [] this->pData; }
    // copy constructor
    CArray(const CArray<T,2> &ref) : iSize1(ref.iSize1), iSize2(ref.iSize2)
    {
      this->pData = new T[this->iSize1*this->iSize2];
      memcpy(this->pData, ref.pData, this->iSize1 * this->iSize2 * sizeof(T));
    }
    // assignment operator
    CArray<T,2> & operator=(const CArray<T,2> &ref)
    {
      // check for initializing from self
      if (this == &ref)
        return *this;
      // otherwise free any memory I may be holding on to
      if (this->pData)
        delete [] this->pData;
      // then construct myself from the input object
      this->iSize1 = ref.iSize1;
      this->iSize2 = ref.iSize2;
      this->pData = new T[this->iSize1*this->iSize2];
      memcpy(this->pData, ref.pData, this->iSize1 * this->iSize2 * sizeof(T));
      return *this;
    }

    T Get(int idx1, int idx2)
    {
      if (idx1 < 0 || idx2 < 0 || idx1 >= this->iSize1 || idx2 >= this->iSize2)
        return 0.0;
      return pData[idx1 * this->iSize2 + idx2];
    }
    void Set(T value, int idx1, int idx2)
    {
      if (idx1 >= 0 && idx2 >= 0 && idx1 < this->iSize1 && idx2 < this->iSize2)
        pData[idx1 * this->iSize2 + idx2] = value;
    }
    
  private:
    T   *pData;
    int  iSize1, iSize2;
};

template <typename T>
class CArray<T,3>
{
  public:
    CArray() : pData(NULL), iSize1(0), iSize2(0), iSize3(0) {}

    // default constuctor for a 0-filled array
    CArray(int size1, int size2, int size3) : iSize1(size1), iSize2(size2), iSize3(size3)
    {
      this->pData = new T[size1*size2*size3];
      for (int i = 0; i < size1*size2*size3; i++)
        this->pData[i] = 0.0;
    }

    // destructor
    ~CArray() { delete [] this->pData; }
    // copy constructor
    CArray(const CArray<T,3> &ref) : iSize1(ref.iSize1), iSize2(ref.iSize2), iSize3(ref.iSize3)
    {
      this->pData = new T[this->iSize1*this->iSize2*this->iSize3];
      memcpy(this->pData, ref.pData, this->iSize1 * this->iSize2 * this->iSize3 * sizeof(T));
    }
    // assignment operator
    CArray<T,3> & operator=(const CArray<T,3> &ref)
    {
      // check for initializing from self
      if (this == &ref)
        return *this;
      // otherwise free any memory I may be holding on to
      if (this->pData)
        delete [] this->pData;
      // then construct myself from the input object
      this->iSize1 = ref.iSize1;
      this->iSize2 = ref.iSize2;
      this->iSize3 = ref.iSize3;
      this->pData = new T[this->iSize1*this->iSize2*this->iSize3];
      memcpy(this->pData, ref.pData, this->iSize1 * this->iSize2 * this->iSize3 * sizeof(T));
      return *this;
    }

    T Get(int idx1, int idx2, int idx3)
    {
      if (idx1 < 0 || idx2 < 0 || idx3 < 0 || idx1 >= this->iSize1 || idx2 >= this->iSize2 || idx3 >= this->iSize3)
        return 0.0;
      return pData[idx1 * this->iSize2 * this->iSize3 + idx2 * this->iSize3 + idx3];
    }
    void Set(T value, int idx1, int idx2, int idx3)
    {
      if (idx1 >= 0 && idx2 >= 0 && idx3 >= 0 && idx1 < this->iSize1 && idx2 < this->iSize2 && idx3 < this->iSize3)
        pData[idx1 * this->iSize2 * this->iSize3 + idx2 * this->iSize3 + idx3] = value;
    }
    
  private:
    T   *pData;
    int  iSize1, iSize2, iSize3;
};

