"""
Terminology Mapping Service
Handles mapping and translation between NAMASTE and ICD-11 (TM2 & Biomedicine) codes
"""

import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from difflib import SequenceMatcher
import re

from app.models.fhir_models import (
    FHIRConceptMap, ConceptMapGroup, PublicationStatus
)
from app.services.namaste_service import NAMASTEService
from app.services.icd11_service import ICD11Service

logger = logging.getLogger(__name__)


class MappingService:
    """Service for mapping between NAMASTE and ICD-11 terminologies"""
    
    def __init__(self):
        self.namaste_service = NAMASTEService()
        self.icd11_service = ICD11Service()
        self.concept_map_url = "http://terminology.mohayush.gov.in/ConceptMap/namaste-to-icd11"
        
        # Initialize mapping rules and patterns
        self._init_mapping_rules()
    
    def _init_mapping_rules(self):
        """Initialize mapping rules and patterns for automatic mapping"""
        
        # Keyword-based mapping patterns
        self.mapping_patterns = {
            # Digestive disorders
            'digestive': {
                'keywords': ['indigestion', 'dyspepsia', 'ajirna', 'ama', 'agni', 'constipation'],
                'tm2_patterns': ['digestive', 'gastrointestinal', 'stomach'],
                'bio_patterns': ['K59', 'K30', 'dyspepsia', 'constipation']
            },
            
            # Constitutional/Dosha imbalances
            'constitutional': {
                'keywords': ['vata', 'pitta', 'kapha', 'vatham', 'pitham', 'dosha', 'mizaj'],
                'tm2_patterns': ['constitutional', 'pattern', 'temperament'],
                'bio_patterns': ['Z73', 'general', 'constitutional']
            },
            
            # Neurological disorders
            'neurological': {
                'keywords': ['headache', 'shirahshula', 'migraine', 'nervous', 'brain'],
                'tm2_patterns': ['neurological', 'nervous', 'head'],
                'bio_patterns': ['G44', 'G43', 'headache', 'migraine']
            },
            
            # Pain disorders
            'pain': {
                'keywords': ['pain', 'ache', 'shula', 'vedana'],
                'tm2_patterns': ['pain', 'ache'],
                'bio_patterns': ['R52', 'M79', 'pain']
            }
        }
        
        # Predefined mappings for common conditions
        self.predefined_mappings = {
            'NAM001': [  # Ama (Undigested food toxins)
                {'system': 'tm2', 'code': 'TM2.02', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'K30', 'equivalence': 'wider'}
            ],
            'NAM002': [  # Vata Dosha Imbalance
                {'system': 'tm2', 'code': 'TM2.01', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'Z73.3', 'equivalence': 'wider'}
            ],
            'NAM003': [  # Pitta Dosha Imbalance
                {'system': 'tm2', 'code': 'TM2.01', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'Z73.3', 'equivalence': 'wider'}
            ],
            'NAM004': [  # Kapha Dosha Imbalance
                {'system': 'tm2', 'code': 'TM2.01', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'Z73.3', 'equivalence': 'wider'}
            ],
            'NAM005': [  # Ajirna (Indigestion)
                {'system': 'tm2', 'code': 'TM2.02', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'K30', 'equivalence': 'equivalent'}
            ],
            'NAM006': [  # Shirahshula (Headache)
                {'system': 'tm2', 'code': 'TM2.03', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'G44.2', 'equivalence': 'equivalent'}
            ],
            'SID001': [  # Vatham Imbalance
                {'system': 'tm2', 'code': 'TM2.01', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'Z73.3', 'equivalence': 'wider'}
            ],
            'SID002': [  # Pitham Imbalance
                {'system': 'tm2', 'code': 'TM2.01', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'Z73.3', 'equivalence': 'wider'}
            ],
            'UNA001': [  # Su-i-Mizaj (Temperament Disorder)
                {'system': 'tm2', 'code': 'TM2.01', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'Z73.3', 'equivalence': 'wider'}
            ],
            'UNA002': [  # Soo-i-Hazm (Dyspepsia)
                {'system': 'tm2', 'code': 'TM2.02', 'equivalence': 'equivalent'},
                {'system': 'biomedicine', 'code': 'K30', 'equivalence': 'equivalent'}
            ]
        }
    
    def translate_namaste_to_icd11(self, namaste_code: str, target_system: str = "both") -> List[Dict[str, Any]]:
        """
        Translate NAMASTE code to ICD-11 codes
        
        Args:
            namaste_code: NAMASTE code to translate
            target_system: "tm2", "biomedicine", or "both"
            
        Returns:
            List of mapped ICD-11 codes with mapping metadata
        """
        try:
            # Check predefined mappings first
            if namaste_code in self.predefined_mappings:
                predefined = self.predefined_mappings[namaste_code]
                results = []
                
                for mapping in predefined:
                    if target_system == "both" or target_system == mapping['system']:
                        # Get detailed code information
                        if mapping['system'] == 'tm2':
                            icd_results = self.icd11_service.search_icd11_codes(mapping['code'], "tm2", 1)
                        else:
                            icd_results = self.icd11_service.search_icd11_codes(mapping['code'], "biomedicine", 1)
                        
                        if icd_results:
                            result = icd_results[0].copy()
                            result['equivalence'] = mapping['equivalence']
                            result['mappingMethod'] = 'predefined'
                            result['confidence'] = 0.9
                            results.append(result)
                
                return results
            
            # Perform automatic mapping if no predefined mapping exists
            return self._perform_automatic_mapping(namaste_code, target_system)
            
        except Exception as e:
            logger.error(f"Error translating NAMASTE code {namaste_code}: {str(e)}")
            return []
    
    def _perform_automatic_mapping(self, namaste_code: str, target_system: str = "both") -> List[Dict[str, Any]]:
        """
        Perform automatic mapping using similarity matching and keyword analysis
        
        Args:
            namaste_code: NAMASTE code to map
            target_system: Target ICD-11 system
            
        Returns:
            List of potential mappings
        """
        try:
            # Get NAMASTE code details
            sample_data = self.namaste_service.create_sample_namaste_data()
            namaste_details = self.namaste_service.get_namaste_code_details(namaste_code, sample_data)
            
            if not namaste_details:
                return []
            
            results = []
            
            # Extract keywords for matching
            search_terms = self._extract_search_terms(namaste_details)
            
            # Search ICD-11 systems
            for search_term in search_terms:
                if target_system in ["tm2", "both"]:
                    tm2_matches = self.icd11_service.search_icd11_codes(search_term, "tm2", 3)
                    for match in tm2_matches:
                        confidence = self._calculate_similarity(namaste_details, match)
                        if confidence > 0.3:  # Minimum confidence threshold
                            match['equivalence'] = self._determine_equivalence(confidence)
                            match['mappingMethod'] = 'automatic'
                            match['confidence'] = confidence
                            results.append(match)
                
                if target_system in ["biomedicine", "both"]:
                    bio_matches = self.icd11_service.search_icd11_codes(search_term, "biomedicine", 3)
                    for match in bio_matches:
                        confidence = self._calculate_similarity(namaste_details, match)
                        if confidence > 0.3:
                            match['equivalence'] = self._determine_equivalence(confidence)
                            match['mappingMethod'] = 'automatic'
                            match['confidence'] = confidence
                            results.append(match)
            
            # Remove duplicates and sort by confidence
            seen_codes = set()
            unique_results = []
            for result in sorted(results, key=lambda x: x['confidence'], reverse=True):
                key = f"{result['system']}:{result['code']}"
                if key not in seen_codes:
                    seen_codes.add(key)
                    unique_results.append(result)
            
            return unique_results[:5]  # Return top 5 matches
            
        except Exception as e:
            logger.error(f"Error in automatic mapping: {str(e)}")
            return []
    
    def _extract_search_terms(self, namaste_details: Dict[str, Any]) -> List[str]:
        """Extract search terms from NAMASTE code details"""
        terms = []
        
        # Primary terms from display and definition
        display = namaste_details.get('display', '').lower()
        definition = namaste_details.get('definition', '').lower()
        
        # Extract main condition name (before parentheses)
        main_term = re.split(r'[\(\)]', display)[0].strip()
        if main_term:
            terms.append(main_term)
        
        # Extract keywords based on category and body system
        category = namaste_details.get('category', '').lower()
        body_system = namaste_details.get('bodySystem', '').lower()
        
        # Add category-based terms
        if 'digestive' in category:
            terms.extend(['digestion', 'stomach', 'gastric'])
        elif 'constitutional' in category:
            terms.extend(['constitutional', 'temperament', 'pattern'])
        elif 'neurological' in category:
            terms.extend(['neurological', 'nervous', 'brain'])
        
        # Add body system terms
        if 'gastrointestinal' in body_system:
            terms.extend(['gastrointestinal', 'digestive'])
        elif 'nervous' in body_system:
            terms.extend(['nervous', 'neurological'])
        
        # Add specific condition keywords
        if 'headache' in display:
            terms.extend(['headache', 'cephalgia'])
        elif 'indigestion' in display:
            terms.extend(['indigestion', 'dyspepsia'])
        elif 'dosha' in display:
            terms.extend(['constitutional', 'pattern'])
        
        return list(set(terms))  # Remove duplicates
    
    def _calculate_similarity(self, namaste_details: Dict[str, Any], icd_match: Dict[str, Any]) -> float:
        """Calculate similarity score between NAMASTE and ICD-11 codes"""
        try:
            # Text similarity using display names
            namaste_display = namaste_details.get('display', '').lower()
            icd_display = icd_match.get('display', '').lower()
            
            display_similarity = SequenceMatcher(None, namaste_display, icd_display).ratio()
            
            # Definition similarity
            namaste_def = namaste_details.get('definition', '').lower()
            icd_def = icd_match.get('definition', '').lower()
            
            def_similarity = SequenceMatcher(None, namaste_def, icd_def).ratio()
            
            # Keyword matching bonus
            keyword_bonus = self._calculate_keyword_bonus(namaste_details, icd_match)
            
            # Calculate final score
            final_score = (display_similarity * 0.4 + def_similarity * 0.4 + keyword_bonus * 0.2)
            
            return min(final_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating similarity: {str(e)}")
            return 0.0
    
    def _calculate_keyword_bonus(self, namaste_details: Dict[str, Any], icd_match: Dict[str, Any]) -> float:
        """Calculate bonus score based on keyword matching"""
        bonus = 0.0
        
        namaste_text = f"{namaste_details.get('display', '')} {namaste_details.get('definition', '')}".lower()
        icd_text = f"{icd_match.get('display', '')} {icd_match.get('definition', '')}".lower()
        
        # Check for common medical terms
        common_terms = [
            'pain', 'disorder', 'syndrome', 'disease', 'condition',
            'digestive', 'neurological', 'constitutional', 'headache',
            'indigestion', 'imbalance'
        ]
        
        for term in common_terms:
            if term in namaste_text and term in icd_text:
                bonus += 0.1
        
        return min(bonus, 1.0)
    
    def _determine_equivalence(self, confidence: float) -> str:
        """Determine equivalence level based on confidence score"""
        if confidence >= 0.8:
            return 'equivalent'
        elif confidence >= 0.6:
            return 'wider'
        elif confidence >= 0.4:
            return 'narrower'
        else:
            return 'related'
    
    def reverse_translate_icd11_to_namaste(self, icd11_code: str, icd11_system: str) -> List[Dict[str, Any]]:
        """
        Reverse translate ICD-11 code to NAMASTE codes
        
        Args:
            icd11_code: ICD-11 code to translate
            icd11_system: "tm2" or "biomedicine"
            
        Returns:
            List of potential NAMASTE mappings
        """
        try:
            results = []
            sample_data = self.namaste_service.create_sample_namaste_data()
            
            # Search through predefined mappings
            for namaste_code, mappings in self.predefined_mappings.items():
                for mapping in mappings:
                    if mapping['system'] == icd11_system and mapping['code'] == icd11_code:
                        namaste_details = self.namaste_service.get_namaste_code_details(namaste_code, sample_data)
                        if namaste_details:
                            namaste_details['equivalence'] = mapping['equivalence']
                            namaste_details['mappingMethod'] = 'predefined'
                            namaste_details['confidence'] = 0.9
                            results.append(namaste_details)
            
            # If no predefined mapping, attempt automatic reverse mapping
            if not results:
                icd_details = self.icd11_service.get_icd11_code_details(icd11_code)
                if icd_details:
                    # Search NAMASTE codes by keywords from ICD-11 code
                    search_terms = [icd_details.get('display', ''), icd_details.get('definition', '')]
                    
                    for search_term in search_terms:
                        if search_term:
                            namaste_matches = self.namaste_service.search_namaste_codes(search_term, sample_data, 5)
                            for match in namaste_matches:
                                confidence = self._calculate_similarity(match, icd_details)
                                if confidence > 0.3:
                                    match['equivalence'] = self._determine_equivalence(confidence)
                                    match['mappingMethod'] = 'automatic_reverse'
                                    match['confidence'] = confidence
                                    results.append(match)
            
            return sorted(results, key=lambda x: x.get('confidence', 0), reverse=True)
            
        except Exception as e:
            logger.error(f"Error reverse translating ICD-11 code: {str(e)}")
            return []
    
    def generate_concept_map(self, namaste_data: List[Dict[str, Any]]) -> FHIRConceptMap:
        """
        Generate FHIR ConceptMap for NAMASTE to ICD-11 mappings
        
        Args:
            namaste_data: List containing NAMASTE codes
            
        Returns:
            FHIR ConceptMap resource
        """
        try:
            # Create mapping groups for TM2 and Biomedicine
            tm2_group = ConceptMapGroup(
                source=self.namaste_service.code_system_url,
                sourceVersion=self.namaste_service.code_system_version,
                target=self.icd11_service.icd11_tm2_url,
                targetVersion="2023-01",
                element=[]
            )
            
            bio_group = ConceptMapGroup(
                source=self.namaste_service.code_system_url,
                sourceVersion=self.namaste_service.code_system_version,
                target=self.icd11_service.icd11_biomedicine_url,
                targetVersion="2023-01",
                element=[]
            )
            
            # Generate mappings for each NAMASTE code
            for row in namaste_data:
                namaste_code = str(row['code'])
                
                # Get TM2 mappings
                tm2_mappings = self.translate_namaste_to_icd11(namaste_code, "tm2")
                if tm2_mappings:
                    element = {
                        'code': namaste_code,
                        'display': str(row['display']),
                        'target': []
                    }
                    
                    for mapping in tm2_mappings:
                        element['target'].append({
                            'code': mapping['code'],
                            'display': mapping['display'],
                            'equivalence': mapping.get('equivalence', 'wider'),
                            'comment': f"Mapped via {mapping.get('mappingMethod', 'unknown')} method with confidence {mapping.get('confidence', 0):.2f}"
                        })
                    
                    tm2_group.element.append(element)
                
                # Get Biomedicine mappings
                bio_mappings = self.translate_namaste_to_icd11(namaste_code, "biomedicine")
                if bio_mappings:
                    element = {
                        'code': namaste_code,
                        'display': str(row['display']),
                        'target': []
                    }
                    
                    for mapping in bio_mappings:
                        element['target'].append({
                            'code': mapping['code'],
                            'display': mapping['display'],
                            'equivalence': mapping.get('equivalence', 'wider'),
                            'comment': f"Mapped via {mapping.get('mappingMethod', 'unknown')} method with confidence {mapping.get('confidence', 0):.2f}"
                        })
                    
                    bio_group.element.append(element)
            
            # Create ConceptMap
            concept_map = FHIRConceptMap(
                id=f"namaste-icd11-map-{uuid.uuid4().hex[:8]}",
                url=self.concept_map_url,
                version="1.0.0",
                name="NAMASTEToICD11ConceptMap",
                title="NAMASTE to ICD-11 Concept Map",
                status=PublicationStatus.ACTIVE,
                experimental=False,
                date=datetime.now(),
                publisher="Ministry of AYUSH, Government of India",
                description="Mapping from NAMASTE terminology to WHO ICD-11 Traditional Medicine Module 2 and Biomedicine",
                purpose="Enable interoperability between traditional medicine and international classification systems",
                copyright="© Ministry of AYUSH, Government of India",
                sourceCanonical=self.namaste_service.code_system_url,
                group=[tm2_group, bio_group],
                contact=[
                    {
                        "name": "Ministry of AYUSH",
                        "telecom": [
                            {
                                "system": "url",
                                "value": "https://www.ayush.gov.in"
                            }
                        ]
                    }
                ],
                jurisdiction=[
                    {
                        "coding": [
                            {
                                "system": "urn:iso:std:iso:3166",
                                "code": "IN",
                                "display": "India"
                            }
                        ]
                    }
                ]
            )
            
            logger.info(f"Generated ConceptMap with {len(tm2_group.element)} TM2 mappings and {len(bio_group.element)} Biomedicine mappings")
            return concept_map
            
        except Exception as e:
            logger.error(f"Error generating ConceptMap: {str(e)}")
            raise
    
    def validate_mapping(self, namaste_code: str, icd11_code: str, icd11_system: str) -> Dict[str, Any]:
        """
        Validate a proposed mapping between NAMASTE and ICD-11 codes
        
        Args:
            namaste_code: NAMASTE code
            icd11_code: ICD-11 code
            icd11_system: ICD-11 system ("tm2" or "biomedicine")
            
        Returns:
            Validation result with confidence and recommendations
        """
        try:
            # Get code details
            sample_data = self.namaste_service.create_sample_namaste_data()
            namaste_details = self.namaste_service.get_namaste_code_details(namaste_code, sample_data)
            
            if not namaste_details:
                return {'valid': False, 'reason': 'NAMASTE code not found'}
            
            icd_results = self.icd11_service.search_icd11_codes(icd11_code, icd11_system, 1)
            if not icd_results:
                return {'valid': False, 'reason': 'ICD-11 code not found'}
            
            icd_details = icd_results[0]
            
            # Calculate similarity
            confidence = self._calculate_similarity(namaste_details, icd_details)
            equivalence = self._determine_equivalence(confidence)
            
            return {
                'valid': confidence > 0.3,
                'confidence': confidence,
                'equivalence': equivalence,
                'recommendation': 'Accept' if confidence > 0.6 else 'Review' if confidence > 0.3 else 'Reject',
                'namaste_details': namaste_details,
                'icd11_details': icd_details
            }
            
        except Exception as e:
            logger.error(f"Error validating mapping: {str(e)}")
            return {'valid': False, 'reason': f'Validation error: {str(e)}'}
