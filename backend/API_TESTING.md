# API Testing Guide (Backend Phase 6)

The FastAPI backend runs locally at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

---

## 1. Starting the Backend Server

```bash
# From repository root (d:\e-waste)
& "C:\Users\RAVITHEJA B R\AppData\Local\Programs\Python\Python314\python.exe" -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 2. Curl Commands

### A. Health Check (`GET /health`)
```bash
curl -X GET "http://localhost:8000/health"
```
**Expected Response:**
```json
{
  "status": "ok",
  "uptime_seconds": 12.4,
  "model_loaded": "efficientnet_b0_int8.onnx",
  "classes_count": 7,
  "execution_provider": "CPUExecutionProvider"
}
```

### B. List Classes (`GET /classes`)
```bash
curl -X GET "http://localhost:8000/classes"
```

### C. Recyclers Proximity Search (`GET /recyclers`)
```bash
# Query closest centers for battery near Electronic City (12.8452, 77.6602)
curl -X GET "http://localhost:8000/recyclers?class_name=battery&user_lat=12.8452&user_lon=77.6602&limit=3"
```

### D. Image Classification (`POST /predict`)
```bash
# Upload a local test image
curl -X POST "http://localhost:8000/predict?threshold=0.65&user_lat=12.9716&user_lon=77.5946" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@data/processed/test/battery/sample_001.jpg"
```

---

## 3. PowerShell Testing Commands

```powershell
# Health Check
Invoke-RestMethod -Uri "http://localhost:8000/health" -Method Get

# Supported Classes
Invoke-RestMethod -Uri "http://localhost:8000/classes" -Method Get

# Recyclers Query
Invoke-RestMethod -Uri "http://localhost:8000/recyclers?class_name=cfl_bulb&limit=3" -Method Get

# Image Prediction
$form = @{
    file = Get-Item -Path "data\processed\test\cfl_bulb\sample_001.jpg"
}
Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method Post -Form $form
```

---

## 4. Postman Collection Configuration

1. **Create Request**: `POST`
2. **URL**: `http://localhost:8000/predict`
3. **Params** (Optional):
   - `threshold`: `0.65`
   - `user_lat`: `12.9716`
   - `user_lon`: `77.5946`
4. **Body Tab**:
   - Select `form-data`
   - Key: `file` (Change key dropdown from *Text* to *File*)
   - Value: Select any JPG/PNG from `data/processed/test/`
5. **Send** and inspect the structured JSON output.

---

## 5. Security & Privacy Validations
- **Zero Disk Persistence**: Uploaded image bytes are kept purely in RAM (`io.BytesIO`) and garbage collected.
- **Rate Limit**: Default 30 requests/minute per client IP (HTTP 429 upon excess).
- **Size Safeguard**: Requests larger than 10 MB are rejected with HTTP 413.
- **Format Safeguard**: Only `.jpg`, `.jpeg`, `.png`, and `.webp` allowed (HTTP 415).
