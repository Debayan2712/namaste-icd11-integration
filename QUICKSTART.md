# 🚀 NAMASTE-ICD11 Integration - Quick Start Guide

## 📋 What You've Built

You now have a **fully functional MVP** for NAMASTE-ICD11 integration with:

✅ **FHIR R4-compliant API** with 8 REST endpoints  
✅ **Interactive web interface** for testing  
✅ **Bidirectional terminology mapping**  
✅ **Sample data** for immediate testing  
✅ **Dual-coding support** for FHIR Bundles  
✅ **WHO ICD-11 API integration** (with demo fallback)  

## 🏃‍♂️ Start the Application

1. **Navigate to project directory:**
   ```bash
   cd namaste-icd11-integration
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the server:**
   ```bash
   python app.py
   ```

4. **Access the application:**
   - **Web Interface:** http://localhost:5000
   - **API Health:** http://localhost:5000/api/health

## 🧪 Testing the Features

### 1. **NAMASTE Search**
Search Indian traditional medicine terminologies:

**Web Interface:** Go to http://localhost:5000 → Search & Translate Tab → NAMASTE Search
- Try: "headache", "indigestion", "dosha", "vata"

**API Call:**
```bash
curl "http://localhost:5000/api/namaste/search?q=headache"
```

### 2. **ICD-11 Search**
Search WHO ICD-11 Traditional Medicine Module 2 and Biomedicine:

**Web Interface:** Search & Translate Tab → ICD-11 Search
- Try: "digestive", "constitutional", "neurological"

**API Call:**
```bash
curl "http://localhost:5000/api/icd11/search?q=digestive&system=tm2"
```

### 3. **Code Translation**
Translate between NAMASTE and ICD-11 codes:

**Web Interface:** Search & Translate Tab → Code Translation
- Source Code: NAM006 (NAMASTE)
- Target: Both ICD-11 Systems

**API Call:**
```bash
curl "http://localhost:5000/api/translate?system=http://terminology.mohayush.gov.in/namaste&code=NAM006&target=both"
```

### 4. **FHIR ConceptMap**
Generate mapping between terminologies:

**Web Interface:** ConceptMap Tab → Generate ConceptMap

**API Call:**
```bash
curl "http://localhost:5000/api/conceptmap"
```

### 5. **FHIR Bundle Upload**
Test dual-coded condition upload:

**Web Interface:** FHIR Bundle Tab → Upload Bundle (sample provided)

**API Call:**
```bash
curl -X POST "http://localhost:5000/api/bundle" \
  -H "Content-Type: application/json" \
  -d '{
    "resourceType": "Bundle",
    "type": "transaction",
    "entry": [
      {
        "fullUrl": "urn:uuid:condition-1",
        "resource": {
          "resourceType": "Condition",
          "id": "condition-1",
          "subject": {"reference": "Patient/patient-1"},
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
        },
        "request": {"method": "POST", "url": "Condition"}
      }
    ]
  }'
```

## 🎯 Sample Test Cases

### **NAMASTE Codes to Test:**
- **NAM001** - Ama (Undigested food toxins) → Maps to digestive disorders
- **NAM002** - Vata Dosha Imbalance → Maps to constitutional patterns  
- **NAM006** - Shirahshula (Headache) → Maps to neurological disorders
- **SID001** - Vatham Imbalance (Siddha system)
- **UNA002** - Soo-i-Hazm (Unani dyspepsia)

### **Search Terms to Try:**
- **Traditional:** "dosha", "vata", "pitta", "kapha", "ama", "ajirna"
- **Clinical:** "headache", "indigestion", "digestive", "constitutional"
- **Systems:** Filter by "Ayurveda", "Siddha", "Unani"

### **Expected Results:**
- **Search:** Returns formatted results with codes, displays, definitions
- **Translation:** Shows mapped ICD-11 codes with confidence scores
- **ConceptMap:** Generates complete FHIR resource with mappings
- **Bundle:** Validates dual-coding and returns transaction response

## 🔍 What to Look For

### **1. Successful Mapping**
- Confidence scores between 0.3-1.0
- Equivalence levels: equivalent, wider, narrower, related
- Both TM2 and Biomedicine mappings where available

### **2. FHIR Compliance**
- All responses in FHIR R4 format
- Proper resource types and structures
- Bundle transactions with response codes

### **3. Error Handling**
- Graceful fallback when WHO API unavailable
- Proper error messages for invalid inputs
- Validation warnings for incomplete dual-coding

## 🐛 Troubleshooting

### **Common Issues:**

1. **ModuleNotFoundError**
   ```bash
   pip install -r requirements.txt
   ```

2. **WHO API Authentication**
   - System works in demo mode without credentials
   - Add WHO_CLIENT_ID/SECRET to .env for production

3. **Port Already in Use**
   ```bash
   python app.py  # Try different port if needed
   ```

4. **Import Errors**
   - Ensure all `__init__.py` files are present
   - Check Python path and virtual environment

### **Verification Steps:**

1. **Health Check:**
   ```bash
   curl http://localhost:5000/api/health
   # Should return: {"status": "healthy", ...}
   ```

2. **Basic Search:**
   ```bash
   curl "http://localhost:5000/api/namaste/search?q=test"
   # Should return FHIR Bundle with sample data
   ```

3. **Web Interface:**
   - Open http://localhost:5000
   - Should see styled interface with three tabs
   - Try any search or translation

## 📊 Demo Data Included

The MVP includes **10 sample NAMASTE codes** covering:

- **3 Ayurveda codes** (NAM001-NAM006)
- **2 Siddha codes** (SID001-SID002)  
- **2 Unani codes** (UNA001-UNA002)
- **Multiple categories:** Digestive, Constitutional, Neurological
- **Multiple body systems:** GI, Nervous, Metabolic, Immune

All codes have **predefined mappings** to ICD-11 for immediate testing.

## 🎉 Success Indicators

✅ **Web interface loads** at http://localhost:5000  
✅ **API health check** returns status "healthy"  
✅ **NAMASTE search** returns sample results  
✅ **Code translation** shows mapped ICD-11 codes  
✅ **ConceptMap generation** produces FHIR resource  
✅ **Bundle upload** validates dual-coding  

## 🚀 Next Steps

Once basic testing is complete:

1. **Load real NAMASTE CSV** data via the ingestion service
2. **Configure WHO ICD-11** credentials for live API access
3. **Extend mapping rules** for additional conditions
4. **Integrate with EMR systems** via FHIR endpoints
5. **Deploy to production** with proper security

## 📞 Need Help?

- **Check logs** in the terminal for detailed error messages
- **Review README.md** for comprehensive documentation
- **Test individual components** before full integration
- **Use sample data** first before adding real terminologies

---

**🎯 You now have a working NAMASTE-ICD11 integration system ready for demonstration and further development!**
