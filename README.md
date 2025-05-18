# LNCT AccSoft 2.0 Attendance Scraper API

This is a Flask-based API that scrapes attendance data from the **LNCT portal ([AccSoft 2.0](https://portal.lnct.ac.in/Accsoft2/studentlogin.aspx "accsoft2.0"))**, providing both subject-wise and date-wise attendance details. It also calculates the minimum number of additional classes required to achieve a desired attendance percentage in each subject.

##  Features
- Secure login using session-based authentication.
- Parses attendance data using **BeautifulSoup**.
- Calculates additional number of classes required to meet a target percentage.

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

The server will start at `http://127.0.0.1:5000` by default.

---

## API Reference

### 1. `POST /attendance-subwise`

Returns detailed subject-wise attendance data, including the number of additional classes required to reach a specified attendance percentage for each subject.

#### Request Body Parameters

| **Parameter**      | **Type**  | **Required** | **Description**                                                                                  |
| ------------------ | --------- | ------------ | ------------------------------------------------------------------------------------------------ |
| `username`         | `string`  | ✅ Yes        | Scholar Number/Username on AccSoft.                                                              |
| `password`         | `string`  | ✅ Yes        | Password on AccSoft.                                                                             |
| `targetPercentage` | `number`  | ❌ No         | The desired attendance percentage goal. Defaults to **75%**.                                     |
| `firstLogin`       | `boolean` | ❌ No         | If `true`, returns additional details like name, class, and scholar number. Defaults to `false`. |

#### Example Request

```json
{
  "username": "your_username",
  "password": "your_password",
  "targetPercentage": 60,
  "firstLogin": true
}
```

#### Example Response

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

#### cURL Example

```
curl --location 'http://127.0.0.1:5000/attendance-subwise' \
--header 'Content-Type: application/json' \
--data-raw '{
  "username": "username",
  "password": "password",
  "targetPercentage": 75,
  "firstLogin": true
}'
```

---

### 📌 2. `POST /attendance-datewise`

Returns date-wise attendance details for the current semester

#### Request Body Parameters

| **Parameter** | **Type** | **Required** | **Description**                     |
| ------------- | -------- | ------------ | ----------------------------------- |
| `username`    | `string` | ✅ Yes        | Scholar Number/Username on AccSoft. |
| `password`    | `string` | ✅ Yes        | Password on AccSoft.                |

#### Example Request

```json
{
  "username": "your_username",
  "password": "your_password"
}
```

#### Example Response

```json
{
  "status": "success",
  "start_date": "2024-01-01",
  "end_date": "2024-03-01",
  "datewise": {
    "2024-02-01": [
      {
        "SNo": 1,
        "Subject": "Physics",
        "Period": 1,
        "Status": "P"
      },
      {
        "SNo": 2,
        "Subject": "Maths",
        "Period": 2,
        "Status": "A"
      }
    ]
  }
}
```

#### cURL Example

```
curl --location 'http://127.0.0.1:5000/attendance-datewise' \
--header 'Content-Type: application/json' \
--data-raw '{
  "username": "username",
  "password": "password"
}'
```
## License

This project is licensed under the [MIT License](./LICENSE).