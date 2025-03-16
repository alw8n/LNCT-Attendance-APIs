 # LNCT AccSoft 2.0 Attendance Scraper API

This is a Flask-based API that scrapes attendance data from the **LNCT portal ([AccSoft 2.0](https://portal.lnct.ac.in/Accsoft2/studentlogin.aspx "accsoft2.0"))** and calculates the number of classes needed to reach a desired attendance percentage. 

##  Features
- Secure login using session-based authentication.
- Scrapes attendance data using **BeautifulSoup**.
- Calculates additional classes needed to meet a target percentage.
- Deployed using **Gunicorn** on render  

## Setup & Installation

### 1. Clone the Repository
```sh
git clone https://github.com/alw8n/LNCT-Data-Extractor.git
cd LNCT-Data-Extractor
```

### 2. Install Dependencies
```sh
pip install -r requirements.txt
```

### 3. Run Locally
```sh
python app.py
```

The server will start at `http://127.0.0.1:5000`

---

## 📡 API Endpoint
### Send a `POST` request to `*serverurl*/scrape`
**Request Body (JSON):**
```json
{
  "username": "your_username",
  "password": "your_password",
  "targetPercentage": 75
}
```

**Response (JSON):**
```json
{
  "status": "success",
  "overall_attendance": "85%",
  "attendance_data": [
    {
      "subject": "Math",
      "classes_held": 30,
      "classes_present": 25,
      "current_percentage": 83.3,
      "classes_needed": "-"
    }
  ]
}
```
**cURL Example:**
```
curl --location 'http://127.0.0.1:5000/scrape' \
--header 'Content-Type: application/json' \
--data-raw '{
           "username": "username",
           "password": "password",
           "targetPercentage": 75
         }  '
```