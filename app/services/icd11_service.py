"""
WHO ICD-11 API Integration Service
Handles interaction with WHO ICD-11 API for Traditional Medicine Module 2 (TM2) and Biomedicine
"""

import requests
import json
import uuid
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, quote

from app.models.fhir_models import FHIRCodeSystem, CodeSystemConcept, PublicationStatus

logger = logging.getLogger(__name__)


class ICD11Service:
    """Service for WHO ICD-11 API integration"""
    
    def __init__(self, client_id: str = None, client_secret: str = None):
        self.base_url = "https://id.who.int"
        self.api_url = f"{self.base_url}/icd"
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expires = None
        
        # ICD-11 System URLs
        self.icd11_biomedicine_url = "http://id.who.int/icd/release/11/2023-01/mms"
        self.icd11_tm2_url = "http://id.who.int/icd/release/11/2023-01/tm2"
        
    def authenticate(self) -> str:
        """
        Authenticate with WHO ICD-11 API and get access token
        
        Returns:
            Access token string
        """
        try:
            if self.access_token and self.token_expires and datetime.now() < self.token_expires:
                return self.access_token
            
            # For demo purposes, we'll use a mock token
            # In production, you would implement actual OAuth2 flow
            if not self.client_id or not self.client_secret:
                logger.warning("WHO ICD-11 credentials not provided, using demo mode")
                self.access_token = "demo_token_12345"
                self.token_expires = datetime.now() + timedelta(hours=1)
                return self.access_token
            
            # Actual authentication would be implemented here
            auth_url = f"{self.base_url}/oauth2/token"
            
            auth_data = {
                'grant_type': 'client_credentials',
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'scope': 'icdapi'
            }
            
            response = requests.post(auth_url, data=auth_data, timeout=30)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            self.token_expires = datetime.now() + timedelta(seconds=expires_in - 300)  # 5 min buffer
            
            logger.info("Successfully authenticated with WHO ICD-11 API")
            return self.access_token
            
        except requests.RequestException as e:
            logger.error(f"Error authenticating with WHO ICD-11 API: {str(e)}")
            # Fall back to demo mode
            self.access_token = "demo_token_12345"
            self.token_expires = datetime.now() + timedelta(hours=1)
            return self.access_token
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Make authenticated API request to WHO ICD-11
        
        Args:
            endpoint: API endpoint
            params: Query parameters
            
        Returns:
            API response data
        """
        try:
            token = self.authenticate()
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Accept': 'application/json',
                'API-Version': 'v2'
            }
            
            url = urljoin(self.api_url, endpoint)
            response = requests.get(url, headers=headers, params=params or {}, timeout=30)
            
            # For demo purposes, return mock data if authentication fails
            if response.status_code == 401 or self.access_token == "demo_token_12345":
                return self._get_mock_icd11_data(endpoint)
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error making ICD-11 API request: {str(e)}")
            # Return mock data for demo
            return self._get_mock_icd11_data(endpoint)
    
    def _get_mock_icd11_data(self, endpoint: str) -> Dict[str, Any]:
        """
        Get mock ICD-11 data for demonstration purposes
        
        Args:
            endpoint: Requested endpoint
            
        Returns:
            Mock ICD-11 data
        """
        if "tm2" in endpoint.lower() or "traditional" in endpoint.lower():
            return {
                "entities": [
                    {
                        "@id": "http://id.who.int/icd/release/11/2023-01/tm2/1234567890",
                        "code": "TM2.01",
                        "title": {"@language": "en", "@value": "Traditional Medicine Pattern - Constitutional Type"},
                        "definition": {"@language": "en", "@value": "Traditional medicine constitutional pattern disorders"},
                        "parent": ["http://id.who.int/icd/release/11/2023-01/tm2"],
                        "child": [],
                        "isLeaf": True
                    },
                    {
                        "@id": "http://id.who.int/icd/release/11/2023-01/tm2/1234567891",
                        "code": "TM2.02",
                        "title": {"@language": "en", "@value": "Traditional Medicine Pattern - Digestive Disorders"},
                        "definition": {"@language": "en", "@value": "Traditional medicine digestive pattern disorders"},
                        "parent": ["http://id.who.int/icd/release/11/2023-01/tm2"],
                        "child": [],
                        "isLeaf": True
                    },
                    {
                        "@id": "http://id.who.int/icd/release/11/2023-01/tm2/1234567892",
                        "code": "TM2.03",
                        "title": {"@language": "en", "@value": "Traditional Medicine Pattern - Neurological Disorders"},
                        "definition": {"@language": "en", "@value": "Traditional medicine neurological pattern disorders"},
                        "parent": ["http://id.who.int/icd/release/11/2023-01/tm2"],
                        "child": [],
                        "isLeaf": True
                    }
                ]
            }
        else:
            # Biomedicine mock data
            return {
                "entities": [
                    {
                        "@id": "http://id.who.int/icd/release/11/2023-01/mms/1234567890",
                        "code": "K59.0",
                        "title": {"@language": "en", "@value": "Constipation"},
                        "definition": {"@language": "en", "@value": "Difficulty in passing stools or infrequent bowel movements"},
                        "parent": ["http://id.who.int/icd/release/11/2023-01/mms/K59"],
                        "child": [],
                        "isLeaf": True
                    },
                    {
                        "@id": "http://id.who.int/icd/release/11/2023-01/mms/1234567891",
                        "code": "G44.2",
                        "title": {"@language": "en", "@value": "Tension-type headache"},
                        "definition": {"@language": "en", "@value": "Primary headache disorder characterized by bilateral pain"},
                        "parent": ["http://id.who.int/icd/release/11/2023-01/mms/G44"],
                        "child": [],
                        "isLeaf": True
                    }
                ]
            }
    
    def search_icd11_codes(self, search_term: str, system: str = "both", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search ICD-11 codes in both TM2 and Biomedicine
        
        Args:
            search_term: Search query
            system: "tm2", "biomedicine", or "both"
            limit: Maximum results per system
            
        Returns:
            List of matching ICD-11 codes
        """
        try:
            results = []
            
            if system in ["tm2", "both"]:
                tm2_results = self._search_tm2_codes(search_term, limit)
                results.extend(tm2_results)
            
            if system in ["biomedicine", "both"]:
                bio_results = self._search_biomedicine_codes(search_term, limit)
                results.extend(bio_results)
            
            logger.info(f"Found {len(results)} ICD-11 matches for: {search_term}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching ICD-11 codes: {str(e)}")
            raise
    
    def _search_tm2_codes(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Traditional Medicine Module 2 codes"""
        try:
            endpoint = f"/release/11/2023-01/tm2"
            params = {
                'q': search_term,
                'flatResults': 'true',
                'limit': limit
            }
            
            data = self._make_api_request(endpoint, params)
            
            results = []
            for entity in data.get('entities', []):
                results.append({
                    'id': entity.get('@id', ''),
                    'code': entity.get('code', ''),
                    'display': entity.get('title', {}).get('@value', ''),
                    'definition': entity.get('definition', {}).get('@value', ''),
                    'system': self.icd11_tm2_url,
                    'systemName': 'ICD-11 Traditional Medicine Module 2',
                    'isLeaf': entity.get('isLeaf', False)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching TM2 codes: {str(e)}")
            return []
    
    def _search_biomedicine_codes(self, search_term: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Biomedicine codes"""
        try:
            endpoint = f"/release/11/2023-01/mms"
            params = {
                'q': search_term,
                'flatResults': 'true',
                'limit': limit
            }
            
            data = self._make_api_request(endpoint, params)
            
            results = []
            for entity in data.get('entities', []):
                results.append({
                    'id': entity.get('@id', ''),
                    'code': entity.get('code', ''),
                    'display': entity.get('title', {}).get('@value', ''),
                    'definition': entity.get('definition', {}).get('@value', ''),
                    'system': self.icd11_biomedicine_url,
                    'systemName': 'ICD-11 Biomedicine',
                    'isLeaf': entity.get('isLeaf', False)
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching Biomedicine codes: {str(e)}")
            return []
    
    def get_icd11_code_details(self, code_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific ICD-11 code
        
        Args:
            code_id: ICD-11 code identifier
            
        Returns:
            Detailed code information
        """
        try:
            # Extract the endpoint from the code_id
            if "tm2" in code_id:
                endpoint = code_id.replace(self.base_url, "")
            elif "mms" in code_id:
                endpoint = code_id.replace(self.base_url, "")
            else:
                logger.error(f"Invalid ICD-11 code ID format: {code_id}")
                return None
            
            data = self._make_api_request(endpoint)
            
            if not data:
                return None
            
            system_url = self.icd11_tm2_url if "tm2" in code_id else self.icd11_biomedicine_url
            system_name = "ICD-11 Traditional Medicine Module 2" if "tm2" in code_id else "ICD-11 Biomedicine"
            
            return {
                'id': data.get('@id', ''),
                'code': data.get('code', ''),
                'display': data.get('title', {}).get('@value', ''),
                'definition': data.get('definition', {}).get('@value', ''),
                'system': system_url,
                'systemName': system_name,
                'parent': data.get('parent', []),
                'children': data.get('child', []),
                'isLeaf': data.get('isLeaf', False),
                'synonyms': data.get('synonym', []),
                'narrowerTerm': data.get('narrowerTerm', []),
                'broaderTerm': data.get('broaderTerm', [])
            }
            
        except Exception as e:
            logger.error(f"Error getting ICD-11 code details: {str(e)}")
            return None
    
    def generate_icd11_code_system(self, system_type: str = "tm2") -> FHIRCodeSystem:
        """
        Generate FHIR CodeSystem for ICD-11 subset
        
        Args:
            system_type: "tm2" or "biomedicine"
            
        Returns:
            FHIR CodeSystem resource
        """
        try:
            if system_type == "tm2":
                system_url = self.icd11_tm2_url
                title = "ICD-11 Traditional Medicine Module 2"
                description = "WHO ICD-11 Traditional Medicine Module 2 for traditional medicine patterns"
                endpoint = "/release/11/2023-01/tm2"
            else:
                system_url = self.icd11_biomedicine_url
                title = "ICD-11 Biomedicine"
                description = "WHO ICD-11 Biomedicine classification system"
                endpoint = "/release/11/2023-01/mms"
            
            # Get sample of codes for the CodeSystem
            data = self._make_api_request(endpoint, {'limit': 50})
            
            concepts = []
            for entity in data.get('entities', []):
                concept = CodeSystemConcept(
                    code=entity.get('code', ''),
                    display=entity.get('title', {}).get('@value', ''),
                    definition=entity.get('definition', {}).get('@value', '')
                )
                concepts.append(concept)
            
            code_system = FHIRCodeSystem(
                id=f"icd11-{system_type}-{uuid.uuid4().hex[:8]}",
                url=system_url,
                version="2023-01",
                name=f"ICD11{system_type.upper()}",
                title=title,
                status=PublicationStatus.ACTIVE,
                experimental=False,
                date=datetime.now(),
                publisher="World Health Organization",
                description=description,
                purpose="International classification for health information",
                copyright="© World Health Organization",
                caseSensitive=True,
                content="example",  # This would be "complete" with full data
                count=len(concepts),
                concept=concepts,
                contact=[
                    {
                        "name": "World Health Organization",
                        "telecom": [
                            {
                                "system": "url",
                                "value": "https://www.who.int"
                            }
                        ]
                    }
                ],
                jurisdiction=[
                    {
                        "coding": [
                            {
                                "system": "http://unstats.un.org/unsd/methods/m49/m49.htm",
                                "code": "001",
                                "display": "World"
                            }
                        ]
                    }
                ]
            )
            
            logger.info(f"Generated ICD-11 {system_type} CodeSystem with {len(concepts)} concepts")
            return code_system
            
        except Exception as e:
            logger.error(f"Error generating ICD-11 CodeSystem: {str(e)}")
            raise
    
    def validate_icd11_code(self, code: str, system: str = "both") -> bool:
        """
        Validate if an ICD-11 code exists
        
        Args:
            code: ICD-11 code to validate
            system: "tm2", "biomedicine", or "both"
            
        Returns:
            True if code exists, False otherwise
        """
        try:
            search_results = self.search_icd11_codes(code, system, limit=1)
            return len(search_results) > 0 and any(r['code'] == code for r in search_results)
            
        except Exception as e:
            logger.error(f"Error validating ICD-11 code: {str(e)}")
            return False
    
    def get_icd11_hierarchy(self, code_id: str) -> Dict[str, Any]:
        """
        Get hierarchical structure for an ICD-11 code
        
        Args:
            code_id: ICD-11 code identifier
            
        Returns:
            Hierarchical structure information
        """
        try:
            code_details = self.get_icd11_code_details(code_id)
            
            if not code_details:
                return {}
            
            hierarchy = {
                'code': code_details,
                'parents': [],
                'children': []
            }
            
            # Get parent information
            for parent_id in code_details.get('parent', []):
                parent_info = self.get_icd11_code_details(parent_id)
                if parent_info:
                    hierarchy['parents'].append(parent_info)
            
            # Get children information
            for child_id in code_details.get('children', []):
                child_info = self.get_icd11_code_details(child_id)
                if child_info:
                    hierarchy['children'].append(child_info)
            
            return hierarchy
            
        except Exception as e:
            logger.error(f"Error getting ICD-11 hierarchy: {str(e)}")
            return {}
