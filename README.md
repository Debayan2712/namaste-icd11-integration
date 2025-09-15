# NAMASTE-ICD11 Integration API

A **FHIR R4-compliant** terminology service that enables interoperability between **India's NAMASTE** (National AYUSH Morbidity & Standardized Terminologies Electronic) codes and **WHO ICD-11** Traditional Medicine Module 2 (TM2) & Biomedicine classifications.

## 🎯 Overview

This MVP provides a lightweight microservice that:

- ✅ **Ingests NAMASTE terminologies** and generates FHIR CodeSystem resources
- ✅ **Integrates with WHO ICD-11 API** for TM2 and Biomedicine data 
- ✅ **Performs bidirectional mapping** between NAMASTE ↔ ICD-11 codes
- ✅ **Provides FHIR-compliant REST endpoints** for terminology operations
- ✅ **Supports dual-coding** for traditional medicine and biomedical diagnoses
- ✅ **Enables auto-complete** search functionality
- ✅ **Generates FHIR ConceptMaps** for mapping visualization
- ✅ **Validates FHIR Bundles** with dual-coded conditions

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Web Interface                            │
│                  (Testing & Demo)                           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  REST API Layer                             │
│  /api/namaste/search  /api/icd11/search  /api/translate    │
│  /api/conceptmap      /api/bundle        /fhir/*           │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                  Service Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │  NAMASTE    │ │   ICD-11    │ │    Mapping Service      │ │
│  │  Service    │ │  Service    │ │  (Translation Logic)    │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                Data Sources                                 │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │  NAMASTE    │ │ WHO ICD-11  │ │     Mapping Rules       │ │
│  │    CSV      │ │    API      │ │   (Predefined + ML)     │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **pip** (Python package manager)
- **Git** (for cloning the repository)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd namaste-icd11-integration
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables (optional):**
   ```bash
   # Create .env file
   WHO_CLIENT_ID=your_who_client_id
   WHO_CLIENT_SECRET=your_who_client_secret
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   ```

5. **Run the application:**
   ```bash
   python app.py
   ```

6. **Access the application:**
   - **Web Interface:** http://localhost:5000
   - **API Documentation:** http://localhost:5000/api/health
   - **FHIR Metadata:** http://localhost:5000/fhir/metadata

## 📊 Sample Data

The MVP includes **sample NAMASTE data** covering:

- **Ayurveda:** Ama, Vata/Pitta/Kapha Dosha imbalances, Ajirna, Shirahshula
- **Siddha:** Vatham/Pitham imbalances  
- **Unani:** Su-i-Mizaj, Soo-i-Hazm

Each entry includes:
- **Code:** NAMASTE identifier (e.g., NAM001, SID001, UNA001)
- **Display:** Human-readable term
- **Definition:** Clinical description
- **System:** AYUSH system (Ayurveda/Siddha/Unani)
- **Category:** Disorder classification
- **Body System:** Affected organ system

## 🔌 API Endpoints

### Core Search Endpoints

#### **NAMASTE Search**
```http
GET /api/namaste/search?q={search_term}&system={ayush_system}&limit={max_results}
```
**Parameters:**
- `q` (required): Search term
- `system` (optional): Filter by Ayurveda/Siddha/Unani
- `limit` (optional, default=10): Maximum results

**Example:**
```bash
curl "http://localhost:5000/api/namaste/search?q=headache&system=Ayurveda"
```

#### **ICD-11 Search**
```http
GET /api/icd11/search?q={search_term}&system={icd_system}&limit={max_results}
```
**Parameters:**
- `q` (required): Search term
- `system` (optional, default=both): tm2, biomedicine, or both
- `limit` (optional, default=10): Maximum results

**Example:**
```bash
curl "http://localhost:5000/api/icd11/search?q=digestive&system=tm2"
```

### FHIR Terminology Operations

#### **$translate Operation**
```http
GET /api/translate?system={source_system}&code={source_code}&target={target_system}
POST /fhir/ConceptMap/$translate
```
**Parameters:**
- `system` (required): Source system URI
- `code` (required): Source code
- `target` (optional, default=both): Target system

**Example:**
```bash
curl "http://localhost:5000/api/translate?system=http://terminology.mohayush.gov.in/namaste&code=NAM006&target=both"
```

#### **ValueSet $expand Operation**
```http
GET /fhir/ValueSet/$expand?system={system_uri}&filter={text_filter}&count={max_count}
```

#### **ConceptMap Resource**
```http
GET /api/conceptmap
GET /fhir/ConceptMap
```

#### **Bundle Upload**
```http
POST /api/bundle
POST /fhir/Bundle
Content-Type: application/json

{
  "resourceType": "Bundle",
  "type": "transaction",
  "entry": [...]
}
```

## 🗺️ Mapping Logic

### **Predefined Mappings**

High-confidence mappings for common conditions:

| NAMASTE Code | Display | ICD-11 TM2 | ICD-11 Bio | Equivalence |
|--------------|---------|------------|------------|-------------|
| NAM001 | Ama (Undigested food toxins) | TM2.02 | K30 | equivalent/wider |
| NAM006 | Shirahshula (Headache) | TM2.03 | G44.2 | equivalent |
| UNA002 | Soo-i-Hazm (Dyspepsia) | TM2.02 | K30 | equivalent |

### **Automatic Mapping**

Uses **similarity algorithms** and **keyword matching**:

1. **Text Similarity:** Display name and definition comparison
2. **Keyword Matching:** Medical terms, body systems, categories
3. **Confidence Scoring:** 0.0-1.0 scale with thresholds
4. **Equivalence Determination:**
   - `equivalent` (≥0.8): Direct mapping
   - `wider` (≥0.6): Source concept is broader
   - `narrower` (≥0.4): Source concept is narrower  
   - `related` (<0.4): Related but inexact

## 📋 FHIR Resources

### **CodeSystem**
- **NAMASTE:** `http://terminology.mohayush.gov.in/namaste`
- **ICD-11 TM2:** `http://id.who.int/icd/release/11/2023-01/tm2`
- **ICD-11 Biomedicine:** `http://id.who.int/icd/release/11/2023-01/mms`

### **ConceptMap**
Maps NAMASTE codes to both ICD-11 systems with:
- **Equivalence levels** (equivalent, wider, narrower, related)
- **Confidence scores** (0.0-1.0)
- **Mapping methods** (predefined, automatic)

### **ValueSet**
Expandable value sets for terminology browsing and selection.

### **Bundle**
Transaction bundles with dual-coded Condition resources:
```json
{
  "resourceType": "Condition",
  "code": {
    "coding": [
      {
        "system": "http://terminology.mohayush.gov.in/namaste",
        "code": "NAM006",
        "display": "Shirahshula (Headache)"
      },
      {
        "system": "http://id.who.int/icd/release/11/2023-01/mms",
        "code": "G44.2", 
        "display": "Tension-type headache"
      }
    ]
  }
}
```

## 🌐 Web Interface

Interactive testing interface at http://localhost:5000 with:

### **Search & Translate Tab**
- ✅ **NAMASTE Search** with system filtering
- ✅ **ICD-11 Search** across TM2 and Biomedicine
- ✅ **Code Translation** with confidence scores

### **ConceptMap Tab**  
- ✅ **FHIR ConceptMap generation** 
- ✅ **Mapping statistics** and metadata
- ✅ **Raw JSON export**

### **FHIR Bundle Tab**
- ✅ **Bundle upload** with validation
- ✅ **Dual-coding compliance** checking
- ✅ **Sample bundle** for testing

## 🔧 Configuration

Environment variables:

```bash
# Application
FLASK_ENV=development|production|testing
SECRET_KEY=your-secret-key
DEBUG=true|false

# Database
DATABASE_URL=sqlite:///namaste_icd11.db

# WHO ICD-11 API
WHO_CLIENT_ID=your-who-client-id
WHO_CLIENT_SECRET=your-who-client-secret

# ABHA/ABDM Integration
ABHA_BASE_URL=https://dev.abdm.gov.in

# FHIR Configuration  
FHIR_BASE_URL=http://localhost:5000/fhir

# Logging
LOG_LEVEL=INFO|DEBUG|WARNING|ERROR
```

## 🧪 Testing

### **Manual Testing**

1. **Start the application:** `python app.py`

2. **Test NAMASTE search:**
   ```bash
   curl "http://localhost:5000/api/namaste/search?q=headache"
   ```

3. **Test code translation:**
   ```bash
   curl "http://localhost:5000/api/translate?system=http://terminology.mohayush.gov.in/namaste&code=NAM006&target=both"
   ```

4. **Test ConceptMap generation:**
   ```bash
   curl "http://localhost:5000/api/conceptmap"
   ```

### **Web Interface Testing**

1. **Navigate to:** http://localhost:5000
2. **Try searches:** "headache", "indigestion", "dosha"
3. **Test translations:** NAM006, NAM001, SID001
4. **Upload sample bundle:** Use provided JSON template

### **Unit Testing**

```bash
# Install test dependencies
pip install pytest pytest-flask pytest-cov

# Run tests
pytest tests/ -v --cov=app

# Generate coverage report
pytest --cov=app --cov-report=html
```

## 🏥 Production Deployment

### ✅ Free Hosting (Render/Railway)

Deploy for free on Render or Railway. This repo already includes a `Procfile` and uses `gunicorn`.

1. Push this repo to GitHub.
2. Create a new Web Service:
   - Render: New → Web Service → Connect repo
   - Railway: New Project → Deploy from GitHub
3. Configure build/run:
   - Build: `pip install -r requirements.txt`
   - Start: `gunicorn app:create_app()`
4. Set environment variables:
   - `FLASK_ENV=production`
   - `SECRET_KEY=<long-random-string>`
   - Optional: `WHO_CLIENT_ID`, `WHO_CLIENT_SECRET`
5. Deploy. The platform assigns a public URL. Services may sleep on free tier.

### **Docker Deployment**

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:create_app()"]
```

### **Environment Setup**

1. **Create production environment:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex())')
   export WHO_CLIENT_ID=your_production_client_id
   export WHO_CLIENT_SECRET=your_production_secret
   ```

2. **Use production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn --bind 0.0.0.0:5000 app:create_app()
   ```

### **Security Considerations**

- ✅ **HTTPS only** in production
- ✅ **OAuth 2.0 authentication** for sensitive endpoints  
- ✅ **Rate limiting** for API endpoints
- ✅ **Input validation** and sanitization
- ✅ **Audit logging** for all operations
- ✅ **CORS configuration** for web clients

## 📈 Compliance & Standards

### **FHIR R4 Compliance**
- ✅ **CodeSystem** resources for terminologies
- ✅ **ConceptMap** resources for mappings
- ✅ **ValueSet** resources for code sets
- ✅ **Bundle** resources for transactions
- ✅ **OperationOutcome** for error reporting

### **India EHR Standards 2016**
- ✅ **FHIR R4 APIs** for interoperability
- ✅ **SNOMED CT semantics** (conceptually aligned)
- ✅ **LOINC compatibility** (for observations)
- ✅ **ISO 22600** access control framework
- ✅ **OAuth 2.0** authentication readiness
- ✅ **Audit trails** for consent and versioning

### **WHO ICD-11 Integration**
- ✅ **TM2 Chapter 26** Traditional Medicine patterns
- ✅ **Biomedicine chapters** for dual coding
- ✅ **Official WHO API** integration (with fallback)
- ✅ **ICD-11 coding rules** compliance

## 🔮 Future Enhancements

### **Phase 2: Advanced Features**
- 🔄 **Machine Learning** mapping refinement
- 🔄 **SNOMED CT** integration
- 🔄 **LOINC** laboratory codes
- 🔄 **Real-time sync** with WHO updates
- 🔄 **Multi-language** support (Hindi, Tamil, Arabic)

### **Phase 3: Enterprise Features**  
- 🔄 **ABHA authentication** integration
- 🔄 **Advanced audit logging**
- 🔄 **Analytics dashboard**
- 🔄 **Bulk import/export** tools
- 🔄 **Custom mapping** UI for administrators

### **Phase 4: AI/ML Integration**
- 🔄 **NLP-powered** automatic mapping
- 🔄 **Similarity learning** from feedback
- 🔄 **Clinical context** awareness
- 🔄 **Quality metrics** and reporting

## 🤝 Contributing

1. **Fork** the repository
2. **Create** feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** changes (`git commit -m 'Add amazing feature'`)
4. **Push** to branch (`git push origin feature/amazing-feature`)
5. **Open** Pull Request

### **Development Setup**
```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Pre-commit hooks
pre-commit install

# Code formatting
black app/ tests/
flake8 app/ tests/

# Type checking
mypy app/
```

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Documentation:** [API Documentation](docs/api.md)
- **Issues:** [GitHub Issues](https://github.com/your-repo/issues)
- **Email:** support@mohayush.gov.in
- **Ministry of AYUSH:** https://www.ayush.gov.in

## 🙏 Acknowledgments

- **Ministry of AYUSH** for NAMASTE terminology specifications
- **World Health Organization** for ICD-11 standards and API access  
- **HL7 FHIR Community** for healthcare interoperability standards
- **All India Institute of Ayurveda (AIIA)** for clinical validation

---

**Built with ❤️ for India's Traditional Medicine Digital Transformation**

*Enabling seamless interoperability between traditional and modern healthcare systems through standardized terminology mapping.*
