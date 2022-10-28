import jadn
import json
import os

"""
Convert MITRE ATT&CK Tactics and Techniques to OCSF enum definitions
"""

ATTACK_DIR = '../cti-ATT-CK-v12.0'

"""
JADN schema for the minimum subset of STIX needed to validate the MITRE ATT&CK definitions
"""
STIX_schema = """
package "http://mitre.org/attack/v12.0

Bundle = Record
    1 id String
    2 type STIX-Type
    3 objects STIX-Object {1..*}

STIX-Type = Enumerated
    1 bundle

STIX-Object = Record
    1 id String
    2 type STIX-Object-Type
    3 name String
    4 created DateTime
    5 modified DateTime
    6 created_by_ref String
    7 description String
    8 spec_version STIX-Version
    9 object_marking_refs String {0..*}
    10 external_references STIX-External-Reference {0..*}

STIX-Object-Type = Enumeration
    1 attack-pattern
"""