 # LNCT AccSoft 2.0 Attendance Scraper API

This is a Flask-based API that scrapes attendance data from the **LNCT portal ([AccSoft 2.0](https://portal.lnct.ac.in/Accsoft2/studentlogin.aspx "accsoft2.0"))** and calculates the number of classes needed to reach a desired attendance percentage. 

##  Features
- Secure login using session-based authentication.
- Scrapes attendance data using **BeautifulSoup**.
- Calculates additional classes needed to meet a target percentage.
- Deployed using **Gunicorn** on render  

## Setup & Installation:

### 1. Clone the Repository
```sh
git clone https://github.com/alw8n/LNCT-Attendance-APIs.git
cd LNCT-Attendance-APIs
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

## API Reference:
Send a `POST` request to `*serverurl*/attendance-subwise`
### Request Body Parameters  

The API expects a **JSON payload** with the following parameters:  

| **Parameter**       | **Type**   | **Required**| **Description** |
|---------------------|-----------|-------------|-------------------|----------------|
| `username`         | string   | ✅ | Scholar Number/Username on AccSoft |
| `password`         | string   | ✅| Password on AccSoft |
| `targetPercent` | number  |❌ |The desired attendance percentage goal.** If omitted, the default value is 75%** |
| `firstLogin`       | boolean  |❌ | If `true`, additional user details such as name, class, and scholar number will be included in the response, **false by default** |

#### Example Request Body:  
```json
{
  "username": "your_username",
  "password": "your_password",
  "targetPercentage": 60,
  "firstLogin": true
}
```
**Example Response:**
```json
{
  "status": "success",
  "class": "B.Tech - C.S.E., SEC-A",
  "name": "John Doe",
  "overall_attendance": "75.65",
  "scholar_no": "11111111111",
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
curl --location 'http://127.0.0.1:5000/attendance-subwise' \
--header 'Content-Type: application/json' \
--data-raw '{
           "username": "username",
           "password": "password",
           "targetPercentage": 75,
           "firstLogin":true
         }  '
```