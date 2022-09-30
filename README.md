# Understanding the OCSF Information Model

This document describes an Information Model (IM) for the Open Cybersecurity Schema Framework (OCSF), and
compares Information-based and Taxonomy/Ontology-based design approaches. OCSF's goal is to be "agnostic
to storage format, data collection and ETL processes", and information modeling is a formal approach to
achieving that goal.

### What is Information

**Information**: the attribute inherent in and communicated by one of two or more alternative sequences
or arrangements of something (such as nucleotides in DNA or binary digits in a computer program)
that produce specific effects. [^1]

Information is not the sequence of bytes in a message or document, but the effect of those bytes.
Information modeling thus provides the basis for defining "agnostic": two data instances
(byte sequences) are equivalent if they communicate/represent the same information instance,
where an information instance is defined as the effect to be achieved.
For example, a Boolean information instance has the effect of being either true or false.
An implementation is agnostic if, for example, it treats data values of 0 (an integer),
false (a JSON literal), "False" (a five-character string), "" (an empty string), etc., as producing
the effect of falseness.

### Why define an Information Model

* Separate business logic from data formats
  * Data 

### Examples

[^1]:
      Merriam-Webster: https://www.merriam-webster.com/dictionary/information