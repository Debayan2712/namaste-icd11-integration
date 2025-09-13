"""
FHIR R4 Models for NAMASTE-ICD11 Integration
Implements FHIR-compliant data structures for terminology services
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


class PublicationStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RETIRED = "retired"
    UNKNOWN = "unknown"


class CodeSystemProperty(BaseModel):
    """FHIR CodeSystem Property"""
    code: str
    uri: Optional[str] = None
    description: Optional[str] = None
    type: str = "string"  # code | Coding | string | integer | boolean | dateTime | decimal


class CodeSystemConcept(BaseModel):
    """FHIR CodeSystem Concept"""
    code: str
    display: Optional[str] = None
    definition: Optional[str] = None
    designation: Optional[List[Dict[str, Any]]] = []
    property: Optional[List[Dict[str, Any]]] = []
    concept: Optional[List["CodeSystemConcept"]] = []


class FHIRCodeSystem(BaseModel):
    """FHIR R4 CodeSystem Resource"""
    resourceType: str = "CodeSystem"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicitRules: Optional[str] = None
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = []
    extension: Optional[List[Dict[str, Any]]] = []
    modifierExtension: Optional[List[Dict[str, Any]]] = []
    
    # CodeSystem specific fields
    url: Optional[str] = None
    identifier: Optional[List[Dict[str, Any]]] = []
    version: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    status: PublicationStatus
    experimental: Optional[bool] = False
    date: Optional[datetime] = None
    publisher: Optional[str] = None
    contact: Optional[List[Dict[str, Any]]] = []
    description: Optional[str] = None
    useContext: Optional[List[Dict[str, Any]]] = []
    jurisdiction: Optional[List[Dict[str, Any]]] = []
    purpose: Optional[str] = None
    copyright: Optional[str] = None
    caseSensitive: Optional[bool] = True
    valueSet: Optional[str] = None
    hierarchyMeaning: Optional[str] = "is-a"
    compositional: Optional[bool] = False
    versionNeeded: Optional[bool] = False
    content: str = "complete"  # not-present | example | fragment | complete | supplement
    supplements: Optional[str] = None
    count: Optional[int] = None
    filter: Optional[List[Dict[str, Any]]] = []
    property: Optional[List[CodeSystemProperty]] = []
    concept: Optional[List[CodeSystemConcept]] = []
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ConceptMapGroup(BaseModel):
    """FHIR ConceptMap Group"""
    source: Optional[str] = None
    sourceVersion: Optional[str] = None
    target: Optional[str] = None
    targetVersion: Optional[str] = None
    element: List[Dict[str, Any]] = []


class FHIRConceptMap(BaseModel):
    """FHIR R4 ConceptMap Resource"""
    resourceType: str = "ConceptMap"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicitRules: Optional[str] = None
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = []
    extension: Optional[List[Dict[str, Any]]] = []
    modifierExtension: Optional[List[Dict[str, Any]]] = []
    
    # ConceptMap specific fields
    url: Optional[str] = None
    identifier: Optional[List[Dict[str, Any]]] = []
    version: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    status: PublicationStatus
    experimental: Optional[bool] = False
    date: Optional[datetime] = None
    publisher: Optional[str] = None
    contact: Optional[List[Dict[str, Any]]] = []
    description: Optional[str] = None
    useContext: Optional[List[Dict[str, Any]]] = []
    jurisdiction: Optional[List[Dict[str, Any]]] = []
    purpose: Optional[str] = None
    copyright: Optional[str] = None
    sourceUri: Optional[str] = None
    sourceCanonical: Optional[str] = None
    targetUri: Optional[str] = None
    targetCanonical: Optional[str] = None
    group: Optional[List[ConceptMapGroup]] = []
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ValueSetCompose(BaseModel):
    """FHIR ValueSet Compose"""
    lockedDate: Optional[datetime] = None
    inactive: Optional[bool] = False
    include: List[Dict[str, Any]] = []
    exclude: Optional[List[Dict[str, Any]]] = []


class FHIRValueSet(BaseModel):
    """FHIR R4 ValueSet Resource"""
    resourceType: str = "ValueSet"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicitRules: Optional[str] = None
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = []
    extension: Optional[List[Dict[str, Any]]] = []
    modifierExtension: Optional[List[Dict[str, Any]]] = []
    
    # ValueSet specific fields
    url: Optional[str] = None
    identifier: Optional[List[Dict[str, Any]]] = []
    version: Optional[str] = None
    name: Optional[str] = None
    title: Optional[str] = None
    status: PublicationStatus
    experimental: Optional[bool] = False
    date: Optional[datetime] = None
    publisher: Optional[str] = None
    contact: Optional[List[Dict[str, Any]]] = []
    description: Optional[str] = None
    useContext: Optional[List[Dict[str, Any]]] = []
    jurisdiction: Optional[List[Dict[str, Any]]] = []
    immutable: Optional[bool] = False
    purpose: Optional[str] = None
    copyright: Optional[str] = None
    compose: Optional[ValueSetCompose] = None
    expansion: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class BundleEntry(BaseModel):
    """FHIR Bundle Entry"""
    fullUrl: Optional[str] = None
    resource: Optional[Dict[str, Any]] = None
    search: Optional[Dict[str, Any]] = None
    request: Optional[Dict[str, Any]] = None
    response: Optional[Dict[str, Any]] = None


class FHIRBundle(BaseModel):
    """FHIR R4 Bundle Resource"""
    resourceType: str = "Bundle"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicitRules: Optional[str] = None
    language: Optional[str] = None
    
    # Bundle specific fields
    identifier: Optional[Dict[str, Any]] = None
    type: str  # document | message | transaction | transaction-response | batch | batch-response | history | searchset | collection
    timestamp: Optional[datetime] = None
    total: Optional[int] = None
    link: Optional[List[Dict[str, Any]]] = []
    entry: Optional[List[BundleEntry]] = []
    signature: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class Coding(BaseModel):
    """FHIR Coding datatype"""
    system: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None
    userSelected: Optional[bool] = None


class CodeableConcept(BaseModel):
    """FHIR CodeableConcept datatype"""
    coding: Optional[List[Coding]] = []
    text: Optional[str] = None


class FHIRCondition(BaseModel):
    """FHIR R4 Condition Resource for Problem List"""
    resourceType: str = "Condition"
    id: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    implicitRules: Optional[str] = None
    language: Optional[str] = None
    text: Optional[Dict[str, Any]] = None
    contained: Optional[List[Dict[str, Any]]] = []
    extension: Optional[List[Dict[str, Any]]] = []
    modifierExtension: Optional[List[Dict[str, Any]]] = []
    
    # Condition specific fields
    identifier: Optional[List[Dict[str, Any]]] = []
    clinicalStatus: Optional[CodeableConcept] = None
    verificationStatus: Optional[CodeableConcept] = None
    category: Optional[List[CodeableConcept]] = []
    severity: Optional[CodeableConcept] = None
    code: Optional[CodeableConcept] = None
    bodySite: Optional[List[CodeableConcept]] = []
    subject: Dict[str, Any]  # Required reference to Patient
    encounter: Optional[Dict[str, Any]] = None
    onsetDateTime: Optional[datetime] = None
    onsetAge: Optional[Dict[str, Any]] = None
    onsetPeriod: Optional[Dict[str, Any]] = None
    onsetRange: Optional[Dict[str, Any]] = None
    onsetString: Optional[str] = None
    abatementDateTime: Optional[datetime] = None
    abatementAge: Optional[Dict[str, Any]] = None
    abatementPeriod: Optional[Dict[str, Any]] = None
    abatementRange: Optional[Dict[str, Any]] = None
    abatementString: Optional[str] = None
    abatementBoolean: Optional[bool] = None
    recordedDate: Optional[datetime] = None
    recorder: Optional[Dict[str, Any]] = None
    asserter: Optional[Dict[str, Any]] = None
    stage: Optional[List[Dict[str, Any]]] = []
    evidence: Optional[List[Dict[str, Any]]] = []
    note: Optional[List[Dict[str, Any]]] = []
    
    class Config:
        use_enum_values = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# Update forward references
CodeSystemConcept.model_rebuild()
