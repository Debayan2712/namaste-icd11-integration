"""
REST API Endpoints for NAMASTE-ICD11 Integration
Provides FHIR-compliant REST endpoints for terminology services
"""

from flask import Flask, request, jsonify, current_app
from flask_restful import Api, Resource
from flask_cors import CORS
import json
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, List

from app.services.namaste_service import NAMASTEService
from app.services.icd11_service import ICD11Service  
from app.services.mapping_service import MappingService
from app.models.fhir_models import (
    FHIRBundle, BundleEntry, FHIRCondition, CodeableConcept, Coding
)

logger = logging.getLogger(__name__)


class HealthCheck(Resource):
    """Health check endpoint"""
    
    def get(self):
        return {
            'status': 'healthy',
            'service': 'NAMASTE-ICD11 Integration API',
            'version': '1.0.0',
            'timestamp': datetime.now().isoformat()
        }


class NAMASTESearch(Resource):
    """NAMASTE code search endpoint"""
    
    def __init__(self):
        self.namaste_service = NAMASTEService()
    
    def get(self):
        """
        Search NAMASTE codes
        Query parameters:
        - q: search term (required)
        - limit: maximum results (default: 10)
        - system: AYUSH system filter (Ayurveda, Siddha, Unani)
        """
        try:
            search_term = request.args.get('q', '').strip()
            if not search_term:
                return {'error': 'Search term (q) is required'}, 400
            
            limit = int(request.args.get('limit', 10))
            system_filter = request.args.get('system', '').strip()
            
            # Get sample data (in production, this would load from actual CSV/database)
            sample_data = self.namaste_service.create_sample_namaste_data()
            
            # Perform search
            results = self.namaste_service.search_namaste_codes(search_term, sample_data, limit)
            
            # Filter by system if specified
            if system_filter:
                results = [r for r in results if r.get('system', '').lower() == system_filter.lower()]
            
            return {
                'resourceType': 'Bundle',
                'id': f'namaste-search-{uuid.uuid4().hex[:8]}',
                'type': 'searchset',
                'timestamp': datetime.now().isoformat(),
                'total': len(results),
                'entry': [
                    {
                        'fullUrl': f"{current_app.config.get('FHIR_BASE_URL', '')}/CodeSystem/namaste/{result['code']}",
                        'resource': {
                            'resourceType': 'CodeSystem',
                            'id': result['code'],
                            'code': result['code'],
                            'display': result['display'],
                            'definition': result['definition'],
                            'system': result['system'],
                            'category': result['category'],
                            'bodySystem': result['bodySystem']
                        }
                    } for result in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in NAMASTE search: {str(e)}")
            return {'error': 'Internal server error'}, 500


class ICD11Search(Resource):
    """ICD-11 code search endpoint"""
    
    def __init__(self):
        self.icd11_service = ICD11Service()
    
    def get(self):
        """
        Search ICD-11 codes
        Query parameters:
        - q: search term (required)
        - system: tm2, biomedicine, or both (default: both)
        - limit: maximum results (default: 10)
        """
        try:
            search_term = request.args.get('q', '').strip()
            if not search_term:
                return {'error': 'Search term (q) is required'}, 400
            
            system = request.args.get('system', 'both')
            limit = int(request.args.get('limit', 10))
            
            # Perform search
            results = self.icd11_service.search_icd11_codes(search_term, system, limit)
            
            return {
                'resourceType': 'Bundle',
                'id': f'icd11-search-{uuid.uuid4().hex[:8]}',
                'type': 'searchset',
                'timestamp': datetime.now().isoformat(),
                'total': len(results),
                'entry': [
                    {
                        'fullUrl': result['id'],
                        'resource': {
                            'resourceType': 'CodeSystem',
                            'id': result['code'],
                            'code': result['code'],
                            'display': result['display'],
                            'definition': result['definition'],
                            'system': result['system'],
                            'systemName': result['systemName']
                        }
                    } for result in results
                ]
            }
            
        except Exception as e:
            logger.error(f"Error in ICD-11 search: {str(e)}")
            return {'error': 'Internal server error'}, 500


class TerminologyTranslate(Resource):
    """FHIR $translate operation for code translation"""
    
    def __init__(self):
        self.mapping_service = MappingService()
    
    def get(self):
        """
        Translate codes using GET parameters
        Query parameters:
        - system: source system URI (required)
        - code: source code (required) 
        - target: target system (tm2, biomedicine, both, or namaste)
        """
        return self._translate_code()
    
    def post(self):
        """
        Translate codes using POST body
        Request body should contain Parameters resource with:
        - system: source system URI
        - code: source code
        - target: target system
        """
        return self._translate_code()
    
    def _translate_code(self):
        """Internal method to handle code translation"""
        try:
            # Get parameters from query string or POST body
            if request.method == 'GET':
                system = request.args.get('system', '').strip()
                code = request.args.get('code', '').strip()
                target = request.args.get('target', 'both').strip()
            else:
                data = request.get_json() or {}
                # Extract parameters from FHIR Parameters resource
                params = {}
                for param in data.get('parameter', []):
                    params[param['name']] = param.get('valueString', param.get('valueCode', ''))
                
                system = params.get('system', '').strip()
                code = params.get('code', '').strip()
                target = params.get('target', 'both').strip()
            
            if not system or not code:
                return {
                    'resourceType': 'Parameters',
                    'parameter': [
                        {
                            'name': 'result',
                            'valueBoolean': False
                        },
                        {
                            'name': 'message',
                            'valueString': 'Both system and code parameters are required'
                        }
                    ]
                }, 400
            
            # Determine source system and perform translation
            results = []
            
            if 'namaste' in system.lower():
                # NAMASTE to ICD-11 translation
                if target == 'namaste':
                    return self._create_error_response('Cannot translate NAMASTE to NAMASTE')
                results = self.mapping_service.translate_namaste_to_icd11(code, target)
            
            elif 'icd' in system.lower():
                # ICD-11 to NAMASTE translation
                if 'tm2' in system.lower():
                    icd_system = 'tm2'
                elif 'mms' in system.lower():
                    icd_system = 'biomedicine'
                else:
                    return self._create_error_response('Invalid ICD-11 system URI')
                
                results = self.mapping_service.reverse_translate_icd11_to_namaste(code, icd_system)
            
            else:
                return self._create_error_response('Unsupported source system')
            
            # Create FHIR Parameters response
            parameters = [
                {
                    'name': 'result',
                    'valueBoolean': len(results) > 0
                }
            ]
            
            if results:
                for result in results:
                    match_param = {
                        'name': 'match',
                        'part': [
                            {
                                'name': 'equivalence',
                                'valueCode': result.get('equivalence', 'wider')
                            },
                            {
                                'name': 'concept',
                                'valueCoding': {
                                    'system': result.get('system', result.get('codeSystem', '')),
                                    'code': result['code'],
                                    'display': result['display']
                                }
                            }
                        ]
                    }
                    
                    # Add confidence and method if available
                    if 'confidence' in result:
                        match_param['part'].append({
                            'name': 'confidence',
                            'valueDecimal': result['confidence']
                        })
                    
                    if 'mappingMethod' in result:
                        match_param['part'].append({
                            'name': 'method',
                            'valueString': result['mappingMethod']
                        })
                    
                    parameters.append(match_param)
            else:
                parameters.append({
                    'name': 'message',
                    'valueString': f'No translation found for {system}#{code}'
                })
            
            return {
                'resourceType': 'Parameters',
                'id': f'translate-{uuid.uuid4().hex[:8]}',
                'parameter': parameters
            }
            
        except Exception as e:
            logger.error(f"Error in code translation: {str(e)}")
            return self._create_error_response('Internal server error'), 500
    
    def _create_error_response(self, message: str):
        """Create error response in FHIR Parameters format"""
        return {
            'resourceType': 'Parameters',
            'parameter': [
                {
                    'name': 'result',
                    'valueBoolean': False
                },
                {
                    'name': 'message',
                    'valueString': message
                }
            ]
        }


class ValueSetExpand(Resource):
    """FHIR $expand operation for ValueSet expansion"""
    
    def __init__(self):
        self.namaste_service = NAMASTEService()
        self.icd11_service = ICD11Service()
    
    def get(self):
        """
        Expand ValueSet
        Query parameters:
        - url: ValueSet URL (optional)
        - system: CodeSystem URL to expand
        - filter: text filter
        - count: maximum number of codes
        """
        try:
            system_url = request.args.get('system', '').strip()
            text_filter = request.args.get('filter', '').strip()
            count = int(request.args.get('count', 50))
            
            concepts = []
            
            if 'namaste' in system_url.lower():
                # Expand NAMASTE codes
                sample_data = self.namaste_service.create_sample_namaste_data()
                if text_filter:
                    results = self.namaste_service.search_namaste_codes(text_filter, sample_data, count)
                else:
                    results = sample_data[:count]  # Take first 'count' items
                    results = [
                        {
                            'code': str(row['code']),
                            'display': str(row['display']),
                            'definition': str(row.get('definition', row['display']))
                        } for row in results
                    ]
                
                concepts = [
                    {
                        'system': system_url,
                        'code': result['code'],
                        'display': result['display']
                    } for result in results
                ]
            
            elif 'icd' in system_url.lower():
                # Expand ICD-11 codes
                system_type = 'tm2' if 'tm2' in system_url.lower() else 'biomedicine'
                if text_filter:
                    results = self.icd11_service.search_icd11_codes(text_filter, system_type, count)
                    concepts = [
                        {
                            'system': result['system'],
                            'code': result['code'],
                            'display': result['display']
                        } for result in results
                    ]
            
            return {
                'resourceType': 'ValueSet',
                'id': f'expansion-{uuid.uuid4().hex[:8]}',
                'url': request.args.get('url', system_url),
                'version': '1.0.0',
                'name': 'ExpandedValueSet',
                'status': 'active',
                'expansion': {
                    'identifier': str(uuid.uuid4()),
                    'timestamp': datetime.now().isoformat(),
                    'total': len(concepts),
                    'parameter': [
                        {
                            'name': 'count',
                            'valueInteger': count
                        }
                    ] + ([{
                        'name': 'filter',
                        'valueString': text_filter
                    }] if text_filter else []),
                    'contains': concepts
                }
            }
            
        except Exception as e:
            logger.error(f"Error in ValueSet expansion: {str(e)}")
            return {'error': 'Internal server error'}, 500


class FHIRBundleUpload(Resource):
    """FHIR Bundle upload endpoint for encounter data"""
    
    def post(self):
        """
        Upload FHIR Bundle with dual-coded conditions
        Request body should contain FHIR Bundle resource
        """
        try:
            bundle_data = request.get_json()
            
            if not bundle_data or bundle_data.get('resourceType') != 'Bundle':
                return {'error': 'Request must contain a FHIR Bundle resource'}, 400
            
            # Validate and process bundle
            processed_entries = []
            validation_issues = []
            
            for entry in bundle_data.get('entry', []):
                resource = entry.get('resource', {})
                
                if resource.get('resourceType') == 'Condition':
                    # Validate dual coding
                    condition_code = resource.get('code', {})
                    coding = condition_code.get('coding', [])
                    
                    namaste_codes = [c for c in coding if 'namaste' in c.get('system', '').lower()]
                    icd11_codes = [c for c in coding if 'icd' in c.get('system', '').lower()]
                    
                    if not namaste_codes:
                        validation_issues.append(f"Condition {resource.get('id', 'unknown')} missing NAMASTE code")
                    
                    if not icd11_codes:
                        validation_issues.append(f"Condition {resource.get('id', 'unknown')} missing ICD-11 code")
                    
                    # Add audit metadata
                    resource['meta'] = resource.get('meta', {})
                    resource['meta']['lastUpdated'] = datetime.now().isoformat()
                    resource['meta']['versionId'] = '1'
                    
                    # Add extension for dual coding compliance
                    extensions = resource.get('extension', [])
                    extensions.append({
                        'url': 'http://terminology.mohayush.gov.in/StructureDefinition/dual-coding',
                        'valueBoolean': len(namaste_codes) > 0 and len(icd11_codes) > 0
                    })
                    resource['extension'] = extensions
                
                processed_entries.append({
                    'fullUrl': entry.get('fullUrl', f"urn:uuid:{uuid.uuid4()}"),
                    'resource': resource,
                    'response': {
                        'status': '201 Created',
                        'location': f"Condition/{resource.get('id', uuid.uuid4().hex[:8])}"
                    }
                })
            
            # Create response bundle
            response_bundle = {
                'resourceType': 'Bundle',
                'id': f'bundle-response-{uuid.uuid4().hex[:8]}',
                'type': 'transaction-response',
                'timestamp': datetime.now().isoformat(),
                'entry': processed_entries
            }
            
            # Add operation outcome if there are validation issues
            if validation_issues:
                outcome_entry = {
                    'fullUrl': f"urn:uuid:{uuid.uuid4()}",
                    'resource': {
                        'resourceType': 'OperationOutcome',
                        'id': f'outcome-{uuid.uuid4().hex[:8]}',
                        'issue': [
                            {
                                'severity': 'warning',
                                'code': 'business-rule',
                                'details': {
                                    'text': issue
                                }
                            } for issue in validation_issues
                        ]
                    }
                }
                response_bundle['entry'].insert(0, outcome_entry)
            
            return response_bundle, 201
            
        except Exception as e:
            logger.error(f"Error processing FHIR Bundle: {str(e)}")
            return {
                'resourceType': 'OperationOutcome',
                'issue': [
                    {
                        'severity': 'error',
                        'code': 'exception',
                        'details': {
                            'text': 'Internal server error'
                        }
                    }
                ]
            }, 500


class ConceptMapResource(Resource):
    """ConceptMap resource endpoint"""
    
    def __init__(self):
        self.mapping_service = MappingService()
        self.namaste_service = NAMASTEService()
    
    def get(self, concept_map_id=None):
        """Get ConceptMap resource"""
        try:
            if concept_map_id:
                # Return specific ConceptMap (in production, retrieve from database)
                return {'error': 'ConceptMap not found'}, 404
            else:
                # Generate ConceptMap from current NAMASTE data
                sample_data = self.namaste_service.create_sample_namaste_data()
                concept_map = self.mapping_service.generate_concept_map(sample_data)
                
                concept_map_dict = concept_map.dict(exclude_none=True)
                # Convert datetime to string for JSON serialization
                if 'date' in concept_map_dict and concept_map_dict['date']:
                    concept_map_dict['date'] = concept_map_dict['date'].isoformat()
                return concept_map_dict
        
        except Exception as e:
            logger.error(f"Error retrieving ConceptMap: {str(e)}")
            return {'error': 'Internal server error'}, 500


def create_api(app: Flask) -> Api:
    """Create and configure Flask-RESTful API"""
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {"origins": "*"},
        r"/fhir/*": {"origins": "*"}
    })
    
    api = Api(app)
    
    # Register endpoints
    api.add_resource(HealthCheck, '/api/health', '/fhir/metadata')
    api.add_resource(NAMASTESearch, '/api/namaste/search', '/fhir/CodeSystem')
    api.add_resource(ICD11Search, '/api/icd11/search')
    api.add_resource(TerminologyTranslate, '/api/translate', '/fhir/ConceptMap/$translate')
    api.add_resource(ValueSetExpand, '/api/valueset/$expand', '/fhir/ValueSet/$expand')
    api.add_resource(FHIRBundleUpload, '/api/bundle', '/fhir/Bundle')
    api.add_resource(ConceptMapResource, '/api/conceptmap', '/api/conceptmap/<concept_map_id>', 
                    '/fhir/ConceptMap', '/fhir/ConceptMap/<concept_map_id>')
    
    return api
