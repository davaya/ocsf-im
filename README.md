# Understanding the OCSF Information Model

This document describes an Information Model (IM) for the Open Cybersecurity Schema Framework (OCSF) and
integration of information modeling into OCSF's Taxonomy/Ontology-based design approach.
OCSF's goal is to be "agnostic to storage format, data collection and ETL processes",
and information modeling is a formal method to achieve that goal.
Framework files are translated into an IM, a static schema that defines types used to implement
the framework in a running system. The purpose of using the IM is to support multiple data formats
("flavors") of serialized data and to enable lossless conversion of data instances across formats.

### What is an Information Model

**Information**: the attribute inherent in and communicated by one of two or more alternative sequences
or arrangements of something (such as nucleotides in DNA or binary digits in a computer program)
that produce specific effects. [^1]

Information modeling defines the desired meaning or behavior of information used in a process independently
of the data used to communicate that meaning. It thus provides the basis for defining "agnostic":
two data instances (byte sequences) are equivalent if they correspond to the same information instance
(value of a program variable).

**Serialization**: converting an information instance into a data instance in a specific data format.

**Data Format**: 

For example, a Boolean information instance has the effect of being either true or false.
A process is agnostic if, for example, it treats data values of 0 (an integer), false (a JSON literal),
"False" (a five-character string), "" (an empty string), etc., as being false.

### Why define an Information Model

* Separate business logic from data formats
  * Data 

### Examples

[^1]:
      Merriam-Webster: https://www.merriam-webster.com/dictionary/information