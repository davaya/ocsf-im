# Understanding the OCSF Information Model

This document describes an Information Model (IM) for the Open Cybersecurity Schema Framework (OCSF),
including integration of information modeling into OCSF's Taxonomy/Ontology-based design approach.
OCSF's goal is to be "agnostic to storage format, data collection and ETL processes"[^1],
and information modeling is a formal method to achieve that goal.
Framework files are translated into an IM, a static schema that defines types used to implement
the framework in a running system. The purpose of using the IM is to support multiple data formats
("flavors") of serialized data and to ensure information equivalence regardless of data format.
Information equivalence is demonstrated by verifying that data instances can be converted from
any data format to any other and back without loss - a "lossless round trip".

### What is Information

**Information**: the attribute inherent in and communicated by one of two or more alternative sequences
or arrangements of something (such as nucleotides in DNA or binary digits in a computer program)
that produce specific effects.[^2]

Information modeling defines the desired meaning or behavior of information used in a process independently
of the data used to represent and communicate that meaning. It thus provides the basis for defining "agnostic":
two data instances (byte sequences) are equivalent if they correspond to the same information instance
(value of a program variable).

The information content of an instance can be no greater than the smallest data instance for which
lossless round-trip conversion is possible. For example, an IPv4 address is 17 bytes of JSON
string data ("192.168.101.213"), but can be converted to 4 byte RFC 791 format and back
without loss. The information content of an IPv4 address can therefore be no greater than 4 bytes
(32 bits), and the information model defines the IPv4 address type as a byte sequence of length 4.

Even though the JSON literals `true` and `false` are 32 and 40 data bits respectively, they are Boolean
values with an information content of exactly one bit, which means they can be translated losslessly
to and from more concise data formats using one bit per instance, or JSON numbers 0 and 1 using
8 bits per instance.

### What is an Information Model

An information model is a collection of datatypes. As defined by UML[^3], a datatypes is a type whose
instances are distinguished only by their value. Datatypes do not have complex internal structure
such as class methods, inheritance, or relationships, so serializing their values is straightforward.
An information modeling language such as JADN[^4] defines a small number of base types from which
information models are constructed.

### Why define an Information Model

* Separate business logic from data formats
  * Data 

### Examples

[^1]:
    *"Understanding the Open Cybersecurity Schema Framework"*,
https://github.com/ocsf/ocsf-docs/blob/main/Understanding%20OCSF.md

[^2]:
    Merriam-Webster: https://www.merriam-webster.com/dictionary/information

[^3]:
    *"OMG Unified Modeling Language"*, Object Management Group, https://www.omg.org/spec/UML/2.5.1/PDF
