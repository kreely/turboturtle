/********************************************/
/* Turbo Turtle CList Wrapper Class         */
/*                                          */
/*  Copyright (c) 2009 by Richard Goedeken  */
/*     Richard@fascinationsoftware.com      */
/********************************************/

//   This program is free software: you can redistribute it and/or modify
//   it under the terms of the GNU General Public License as published by
//   the Free Software Foundation, version 3.

//   This program is distributed in the hope that it will be useful,
//   but WITHOUT ANY WARRANTY; without even the implied warranty of
//   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//   GNU General Public License for more details.

//   You should have received a copy of the GNU General Public License
//   along with this program.  If not, see <http://www.gnu.org/licenses/>.

#include <stdlib.h>
#include <stdarg.h>
#include <memory.h>

// this must be at least 4
#define INTERNAL_SIZE 4

template <typename T>
class CList
{
  public:
    // default constuctor for an empty list
    CList() : pExternal(NULL), iListSize(0) { }
    // destructor
    ~CList() { if (pExternal != NULL) delete [] this->pExternal; }
    // copy constructor
    CList(const CList<T> &ref)
    {
      if (ref.pExternal == NULL)
      {
        this->pExternal = NULL;
        this->iListSize = ref.iListSize;
        memcpy(this->aInternal, ref.aInternal, ref.iListSize * sizeof(T));
      }
      else
      {
        this->pExternal = new T[ref.iListSize];
        this->iListSize = ref.iListSize;
        memcpy(this->pExternal, ref.pExternal, ref.iListSize * sizeof(T));
      }
    }
    // assignment operator
    CList<T> & operator=(const CList<T> &ref)
    {
      // check for initializing from self
      if (this == &ref)
        return *this;
      // otherwise free any memory I may be holding on to
      if (this->pExternal)
      {
        delete [] this->pExternal;
        this->pExternal = NULL;
      }
      // then construct myself from the input object
      if (ref.pExternal == NULL)
      {
        this->pExternal = NULL;
        this->iListSize = ref.iListSize;
        memcpy(this->aInternal, ref.aInternal, ref.iListSize * sizeof(T));
      }
      else
      {
        this->pExternal = new T[ref.iListSize];
        this->iListSize = ref.iListSize;
        memcpy(this->pExternal, ref.pExternal, ref.iListSize * sizeof(T));
      }
      return *this;
    }

    // special constructors for LIST instruction
    CList(T num1)
    {
      this->pExternal = NULL;
      this->iListSize = 1;
      this->aInternal[0] = num1;
    }
    CList(T num1, T num2)
    {
      this->pExternal = NULL;
      this->iListSize = 2;
      this->aInternal[0] = num1;
      this->aInternal[1] = num2;
    }
    CList(T num1, T num2, T num3)
    {
      this->pExternal = NULL;
      this->iListSize = 3;
      this->aInternal[0] = num1;
      this->aInternal[1] = num2;
      this->aInternal[2] = num3;
    }
    CList(T num1, T num2, T num3, T num4)
    {
      this->pExternal = NULL;
      this->iListSize = 4;
      this->aInternal[0] = num1;
      this->aInternal[1] = num2;
      this->aInternal[2] = num3;
      this->aInternal[3] = num4;
    }
    CList(int iSize, double num1, double num2, double num3, double num4, ...)
    {
      va_list arguments;
      
      this->iListSize = iSize;
      if (iSize <= INTERNAL_SIZE)
      {
        this->pExternal = NULL;
        this->aInternal[0] = (T) num1;
        this->aInternal[1] = (T) num2;
        this->aInternal[2] = (T) num3;
        this->aInternal[3] = (T) num4;
        va_start(arguments, num4);
        for (int i = 4; i < iSize; i++)
          this->aInternal[i] = (T) va_arg(arguments, double);
        va_end(arguments);
      }
      else
      {
        this->pExternal = new T[iSize];
        this->pExternal[0] = num1;
        this->pExternal[1] = num2;
        this->pExternal[2] = num3;
        this->pExternal[3] = num4;
        va_start(arguments, num4);
        for (int i = 4; i < iSize; i++)
          this->pExternal[i] = (T) va_arg(arguments, double);
        va_end(arguments);
      }
    }

    // special constructor for FPUT instruction
    CList(T num1, const CList<T> &ref)
    {
      if (ref.iListSize + 1 <= INTERNAL_SIZE)
      {
        this->pExternal = NULL;
        this->iListSize = ref.iListSize + 1;
        this->aInternal[0] = num1;
        memcpy((this->aInternal+1), ref.aInternal, ref.iListSize * sizeof(T));
      }
      else
      {
        this->iListSize = ref.iListSize + 1;
        this->pExternal = new T[this->iListSize];
        this->pExternal[0] = num1;
        if (ref.pExternal != NULL)
          memcpy((this->pExternal+1), ref.pExternal, ref.iListSize * sizeof(T));
        else
          memcpy((this->pExternal+1), ref.aInternal, ref.iListSize * sizeof(T));
      }
    }
    // special constructor for LPUT instruction
    CList(const CList<T> &ref, T num1)
    {
      if (ref.iListSize + 1 <= INTERNAL_SIZE)
      {
        this->pExternal = NULL;
        this->iListSize = ref.iListSize + 1;
        this->aInternal[ref.iListSize] = num1;
        memcpy(this->aInternal, ref.aInternal, ref.iListSize * sizeof(T));
      }
      else
      {
        this->iListSize = ref.iListSize + 1;
        this->pExternal = new T[this->iListSize];
        this->pExternal[ref.iListSize] = num1;
        if (ref.pExternal != NULL)
          memcpy(this->pExternal, ref.pExternal, ref.iListSize * sizeof(T));
        else
          memcpy(this->pExternal, ref.aInternal, ref.iListSize * sizeof(T));
      }
    }

    // function for BUTFIRST instruction
    CList<T> ButFirst(void) const
    {
      CList<T> local;
      if (this->iListSize < 1)
        return local;
      if (this->iListSize - 1 <= INTERNAL_SIZE)
      {
        local.iListSize = this->iListSize - 1;
        if (this->pExternal == NULL)
          memcpy(local.aInternal, (this->aInternal+1), local.iListSize * sizeof(T));
        else
          memcpy(local.aInternal, (this->pExternal+1), local.iListSize * sizeof(T));
      }
      else
      {
        local.iListSize = this->iListSize - 1;
        local.pExternal = new T[local.iListSize];
        memcpy(local.pExternal, (this->pExternal+1), local.iListSize * sizeof(T));
      }
      return local;
    }
    
    // function for BUTLAST instruction
    CList<T> ButLast(void) const
    {
      CList<T> local;
      if (this->iListSize < 1)
        return local;
      if (this->iListSize - 1 <= INTERNAL_SIZE)
      {
        local.iListSize = this->iListSize - 1;
        if (this->pExternal == NULL)
          memcpy(local.aInternal, this->aInternal, local.iListSize * sizeof(T));
        else
          memcpy(local.aInternal, this->pExternal, local.iListSize * sizeof(T));
      }
      else
      {
        local.iListSize = this->iListSize - 1;
        local.pExternal = new T[local.iListSize];
        memcpy(local.pExternal, this->pExternal, local.iListSize * sizeof(T));
      }
      return local;
    }
    
    // function for REVERSE instruction
    CList<T> Reverse(void) const
    {
      CList<T> local;
      local.iListSize = this->iListSize;
      if (this->pExternal != NULL)
      {
        local.pExternal = new T[this->iListSize];
        for (int i = 0; i < this->iListSize; i++)
          local.pExternal[i] = this->pExternal[this->iListSize - i - 1];
      }
      else
      {
        for (int i = 0; i < this->iListSize; i++)
          local.aInternal[i] = this->aInternal[this->iListSize - i - 1];
      }
      return local;
    }

    // function for indexing operator, for FIRST and ITEM instructions
    T operator[](int index) const
    {
      if (index < 0 || index >= this->iListSize)
        return 0;
      if (this->pExternal == NULL)
        return this->aInternal[index];
      else
        return this->pExternal[index];
    }
    
    // function for LAST instruction
    T Last(void) const
    {
      if (this->iListSize <= 0)
        return 0;
      if (this->pExternal == NULL)
        return this->aInternal[this->iListSize - 1];
      else
        return this->pExternal[this->iListSize - 1];
    }
    
    // function for PICK instruction
    T Pick(void) const
    {
      if (this->iListSize <= 0)
        return 0;
      int idx = ((long long) this->iListSize * rand() / ((long long) RAND_MAX + 1));
      if (this->pExternal == NULL)
        return this->aInternal[idx];
      else
        return this->pExternal[idx];
    }
    
    // function for COUNT and EMPTYP instructions
    int Length(void) const
    {
      return iListSize;
    }
    
  private:
    T    aInternal[INTERNAL_SIZE];
    T   *pExternal;
    int  iListSize;
};


