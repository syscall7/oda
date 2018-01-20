A Display Unit represents a contiguous sequence of bytes that can be uniformly displayed.  The Display Unit can be
commented and labeled.

class DisplayUnit
  prop vma             // absolute virtual memory address
  prop rawBytes        // the sequence of raw bytes that make up the display unit
  prop section         // name of the section in which it is found
  prop comment         // user comment (or NULL)
  prop label           // user label (or NULL)

class InstrDisplayUnit : inherits DisplayUnit
  prop opcode          // instruction mnemonic
  prop operands        // instruction operands
  prop funcStart       // TRUE if this instruction begins a function
  prop funcEnd         // TRUE if this instruction ends a function
  prop branchLines     // HTML formatted representation of the branching

class FuncDisplayUnit : inherits InstrDisplayUnit
  prop name            // function name
  prop ret             // return type
  prop args            // array of argument types and names
  prop xrefs           // list of cross references that call this function
  prop size            // number of bytes that this function covers

class DataDisplayUnit : inherits DisplayUnit
  prop type            // type of data
  prop len             // number of elements (if greater than 1, than this is an array of the given type)
