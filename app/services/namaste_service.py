"""
NAMASTE CSV Ingestion Service
Handles parsing of NAMASTE terminologies and generation of FHIR CodeSystem resources
"""

import csv
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

from app.models.fhir_models import (
    FHIRCodeSystem, CodeSystemConcept, CodeSystemProperty,
    PublicationStatus
)

logger = logging.getLogger(__name__)


class NAMASTEService:
    """Service for handling NAMASTE terminology data"""
    
    def __init__(self):
        self.code_system_url = "http://terminology.mohayush.gov.in/namaste"
        self.code_system_version = "1.0.0"
        
    def parse_namaste_csv(self, csv_file_path: str) -> List[Dict[str, Any]]:
        """
        Parse NAMASTE CSV file and return structured DataFrame
        
        Args:
            csv_file_path: Path to NAMASTE CSV file
            
        Returns:
            Parsed list of dictionaries with NAMASTE codes
        """
        try:
            # Read CSV with multiple encodings support
            encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(csv_file_path, encoding=encoding)
                    logger.info(f"Successfully read CSV with {encoding} encoding")
                    break
                except UnicodeDecodeError:
                    continue
                    
            if df is None:
                raise ValueError("Could not read CSV file with any supported encoding")
            
            # Standardize column names (common NAMASTE CSV structure)
            expected_columns = {
                'code': ['code', 'namaste_code', 'Code', 'NAMASTE_Code'],
                'display': ['display', 'term', 'disorder', 'Display', 'Term', 'Disorder'],
                'definition': ['definition', 'description', 'Definition', 'Description'],
                'system': ['system', 'ayush_system', 'System', 'AYUSH_System'],
                'category': ['category', 'Category'],
                'severity': ['severity', 'Severity'],
                'body_system': ['body_system', 'organ_system', 'Body_System', 'Organ_System']
            }
            
            # Map columns to standard names
            column_mapping = {}
            for std_col, possible_names in expected_columns.items():
                for possible_name in possible_names:
                    if possible_name in df.columns:
                        column_mapping[possible_name] = std_col
                        break
            
            df = df.rename(columns=column_mapping)
            
            # Ensure required columns exist
            required_columns = ['code', 'display']
            for col in required_columns:
                if col not in df.columns:
                    raise ValueError(f"Required column '{col}' not found in CSV")
            
            # Clean and validate data
            df = df.dropna(subset=['code', 'display'])
            df['code'] = df['code'].astype(str).str.strip()
            df['display'] = df['display'].astype(str).str.strip()
            
            # Add default values for missing optional columns
            if 'definition' not in df.columns:
                df['definition'] = df['display']
            if 'system' not in df.columns:
                df['system'] = 'Unknown'
            if 'category' not in df.columns:
                df['category'] = 'General'
                
            logger.info(f"Parsed {len(df)} NAMASTE codes from CSV")
            return df
            
        except Exception as e:
            logger.error(f"Error parsing NAMASTE CSV: {str(e)}")
            raise
    
    def create_sample_namaste_data(self) -> List[Dict[str, Any]]:
        """
        Create sample NAMASTE data for demonstration purposes
        This would be replaced with actual NAMASTE CSV in production
        """
        sample_data = [
            {
                'code': 'NAM001',
                'display': 'Ama (Undigested food toxins)',
                'definition': 'Accumulation of undigested food particles leading to toxicity',
                'system': 'Ayurveda',
                'category': 'Digestive Disorders',
                'body_system': 'Gastrointestinal'
            },
            {
                'code': 'NAM002',
                'display': 'Vata Dosha Imbalance',
                'definition': 'Constitutional imbalance of Vata dosha affecting movement and nervous system',
                'system': 'Ayurveda',
                'category': 'Constitutional Disorders',
                'body_system': 'Nervous System'
            },
            {
                'code': 'NAM003',
                'display': 'Pitta Dosha Imbalance',
                'definition': 'Constitutional imbalance of Pitta dosha affecting metabolism and heat',
                'system': 'Ayurveda',
                'category': 'Constitutional Disorders',
                'body_system': 'Metabolic System'
            },
            {
                'code': 'NAM004',
                'display': 'Kapha Dosha Imbalance',
                'definition': 'Constitutional imbalance of Kapha dosha affecting structure and immunity',
                'system': 'Ayurveda',
                'category': 'Constitutional Disorders',
                'body_system': 'Immune System'
            },
            {
                'code': 'NAM005',
                'display': 'Ajirna (Indigestion)',
                'definition': 'Impaired digestion leading to various gastrointestinal symptoms',
                'system': 'Ayurveda',
                'category': 'Digestive Disorders',
                'body_system': 'Gastrointestinal'
            },
            {
                'code': 'SID001',
                'display': 'Vatham Imbalance',
                'definition': 'Vatham dosha imbalance in Siddha system',
                'system': 'Siddha',
                'category': 'Constitutional Disorders',
                'body_system': 'Nervous System'
            },
            {
                'code': 'SID002',
                'display': 'Pitham Imbalance',
                'definition': 'Pitham dosha imbalance in Siddha system',
                'system': 'Siddha',
                'category': 'Constitutional Disorders',
                'body_system': 'Metabolic System'
            },
            {
                'code': 'UNA001',
                'display': 'Su-i-Mizaj (Temperament Disorder)',
                'definition': 'Imbalance in temperament according to Unani medicine',
                'system': 'Unani',
                'category': 'Temperament Disorders',
                'body_system': 'Constitutional'
            },
            {
                'code': 'UNA002',
                'display': 'Soo-i-Hazm (Dyspepsia)',
                'definition': 'Digestive disorder characterized by impaired digestion',
                'system': 'Unani',
                'category': 'Digestive Disorders',
                'body_system': 'Gastrointestinal'
            },
            {
                'code': 'NAM006',
                'display': 'Shirahshula (Headache)',
                'definition': 'Head pain due to various doshic imbalances',
                'system': 'Ayurveda',
                'category': 'Neurological Disorders',
                'body_system': 'Nervous System'
            }
        ]
        
        return sample_data
    
    def generate_fhir_code_system(self, namaste_data: List[Dict[str, Any]]) -> FHIRCodeSystem:
        """
        Generate FHIR R4 CodeSystem from NAMASTE DataFrame
        
        Args:
            namaste_data: List containing NAMASTE codes
            
        Returns:
            FHIR CodeSystem resource
        """
        try:
            # Create CodeSystem concepts
            concepts = []
            for row in namaste_data:
                # Create properties for additional metadata
                properties = []
                if row.get('system'):
                    properties.append({
                        'code': 'system',
                        'valueString': str(row['system'])
                    })
                if row.get('category'):
                    properties.append({
                        'code': 'category',
                        'valueString': str(row['category'])
                    })
                if row.get('body_system'):
                    properties.append({
                        'code': 'bodySystem',
                        'valueString': str(row['body_system'])
                    })
                
                concept = CodeSystemConcept(
                    code=str(row['code']),
                    display=str(row['display']),
                    definition=str(row.get('definition', row['display'])),
                    property=properties
                )
                concepts.append(concept)
            
            # Create CodeSystem properties
            code_system_properties = [
                CodeSystemProperty(
                    code='system',
                    description='AYUSH system (Ayurveda, Siddha, Unani)',
                    type='string'
                ),
                CodeSystemProperty(
                    code='category',
                    description='Disorder category',
                    type='string'
                ),
                CodeSystemProperty(
                    code='bodySystem',
                    description='Affected body system',
                    type='string'
                )
            ]
            
            # Create FHIR CodeSystem
            code_system = FHIRCodeSystem(
                id=f"namaste-codesystem-{uuid.uuid4().hex[:8]}",
                url=self.code_system_url,
                version=self.code_system_version,
                name="NAMASTETerminology",
                title="National AYUSH Morbidity & Standardized Terminologies Electronic (NAMASTE)",
                status=PublicationStatus.ACTIVE,
                experimental=False,
                date=datetime.now(),
                publisher="Ministry of AYUSH, Government of India",
                description="Standardized terminology for Ayurveda, Siddha, and Unani disorders as defined by NAMASTE",
                purpose="To provide standardized coding for traditional medicine disorders in Indian healthcare systems",
                copyright="© Ministry of AYUSH, Government of India",
                caseSensitive=True,
                content="complete",
                count=len(concepts),
                property=code_system_properties,
                concept=concepts,
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
            
            logger.info(f"Generated FHIR CodeSystem with {len(concepts)} concepts")
            return code_system
            
        except Exception as e:
            logger.error(f"Error generating FHIR CodeSystem: {str(e)}")
            raise
    
    def search_namaste_codes(self, search_term: str, namaste_data: List[Dict[str, Any]], 
                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search NAMASTE codes by term
        
        Args:
            search_term: Search string
            namaste_data: List containing NAMASTE codes
            limit: Maximum number of results
            
        Returns:
            List of matching codes with metadata
        """
        try:
            search_term = search_term.lower().strip()
            
            # Search in code, display, and definition fields
            matching_results = []
            for row in namaste_data:
                code_lower = str(row.get('code', '')).lower()
                display_lower = str(row.get('display', '')).lower()
                definition_lower = str(row.get('definition', '')).lower()
                
                if (search_term in code_lower or 
                    search_term in display_lower or 
                    search_term in definition_lower):
                    matching_results.append(row)
                    if len(matching_results) >= limit:
                        break
            
            # Format results
            formatted_results = []
            for row in matching_results:
                formatted_results.append({
                    'code': str(row['code']),
                    'display': str(row['display']),
                    'definition': str(row.get('definition', row['display'])),
                    'system': str(row.get('system', 'Unknown')),
                    'category': str(row.get('category', 'General')),
                    'bodySystem': str(row.get('body_system', 'Unknown')),
                    'codeSystem': self.code_system_url
                })
            
            logger.info(f"Found {len(formatted_results)} matches for search term: {search_term}")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching NAMASTE codes: {str(e)}")
            raise
    
    def get_namaste_code_details(self, code: str, namaste_data: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific NAMASTE code
        
        Args:
            code: NAMASTE code
            namaste_data: List containing NAMASTE codes
            
        Returns:
            Code details or None if not found
        """
        try:
            row = None
            for item in namaste_data:
                if str(item.get('code')) == code:
                    row = item
                    break
            
            if not row:
                return None
            return {
                'code': str(row['code']),
                'display': str(row['display']),
                'definition': str(row.get('definition', row['display'])),
                'system': str(row.get('system', 'Unknown')),
                'category': str(row.get('category', 'General')),
                'bodySystem': str(row.get('body_system', 'Unknown')),
                'codeSystem': self.code_system_url,
                'version': self.code_system_version
            }
            
        except Exception as e:
            logger.error(f"Error getting NAMASTE code details: {str(e)}")
            raise
    
    def validate_namaste_code(self, code: str, namaste_data: List[Dict[str, Any]]) -> bool:
        """
        Validate if a NAMASTE code exists
        
        Args:
            code: NAMASTE code to validate
            namaste_data: List containing NAMASTE codes
            
        Returns:
            True if code exists, False otherwise
        """
        try:
            return any(str(item.get('code')) == code for item in namaste_data)
        except Exception as e:
            logger.error(f"Error validating NAMASTE code: {str(e)}")
            return False
    
    def get_codes_by_system(self, system: str, namaste_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Get all codes for a specific AYUSH system
        
        Args:
            system: AYUSH system (Ayurveda, Siddha, Unani)
            namaste_data: List containing NAMASTE codes
            
        Returns:
            List of codes for the specified system
        """
        try:
            results = []
            for row in namaste_data:
                if str(row.get('system', '')).lower() == system.lower():
                    results.append({
                        'code': str(row['code']),
                        'display': str(row['display']),
                        'definition': str(row.get('definition', row['display'])),
                        'category': str(row.get('category', 'General')),
                        'bodySystem': str(row.get('body_system', 'Unknown'))
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error getting codes by system: {str(e)}")
            raise
