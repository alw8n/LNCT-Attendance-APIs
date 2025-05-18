from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import math
import os
from collections import defaultdict
from datetime import datetime
from accsoft_config import attendance_url, headers, login_url

#Setup:
app = Flask(__name__)
app.json.sort_keys = False #Config: Disables sort by default in JSONify requests
CORS(app)

#Routes:
@app.route('/')
def redirect_to_github():
    return redirect("https://github.com/alw8n")

@app.route('/attendance-subwise', methods=['POST'])
def attendance_subwise():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    desired_percentage = data.get('targetPercentage', 75)
    first_login = data.get('firstLogin', False)

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    soup, error = fetch_attendance_page(username,password)
    if error:
        return jsonify({"error" : error["error_text"]}), error["error_code"]

    try:
        overall = soup.find('span', id='ctl00_ContentPlaceHolder1_lblPer119').text[12:].rstrip(' %')
    except AttributeError:
        return jsonify({'error': 'Failed to retrieve attendance data'}), 500

    table = soup.find('table', id='ctl00_ContentPlaceHolder1_grdSubjectWiseAttendance')
    if not table:
        return jsonify({'error': 'Attendance table not found'}), 500

    rows = table.find_all('tr')
    attendance_data = []

    for row in rows[1:]:
        cols = row.find_all('td')
        sub = cols[0].text.strip()
        held = int(cols[1].text.strip())
        present = int(cols[2].text.strip())
        percentage = (present / held * 100) if held > 0 else 0
        attendance_data.append({
            'subject': sub,
            'classes_held': held,
            'classes_present': present,
            'current_percentage': round(percentage, 2),
            'classes_needed': "-" if percentage >= desired_percentage or desired_percentage == 100 else math.ceil((desired_percentage * held - 100 * present) / (100 - desired_percentage))
        })

    response_data = {
        'status': 'success',
        'overall_attendance': overall,
        'attendance_data': attendance_data
    }

    if first_login:
        user_details = {}
        try:
            name = soup.find("span", class_="mr-2 d-none d-lg-inline small text-gray-500").text.strip()
            scholar_num = soup.find("a", id="alertsDropdown").br.next_sibling.strip()
            class_info = soup.find("a", id="messagesDropdown").br.next_sibling.replace("\r\n", "").replace("  ", "").strip()

            user_details = {
                "name": name,
                "scholar_no": scholar_num,
                "class": class_info
            }
        except AttributeError:
            return jsonify({'error': 'Failed to extract user details'}), 500
        response_data.update(user_details)

    return jsonify(response_data)

@app.route('/attendance-datewise', methods=['POST'])
def attendance_datewise():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400
    
    soup, error = fetch_attendance_page(username,password)
    if error:
        return jsonify({"error" : error["error_text"]}), error["error_code"]

    start_date = soup.select_one('#ctl00_ContentPlaceHolder1_txtfromdate')['value']
    end_date = soup.select_one('#ctl00_ContentPlaceHolder1_txtTodate')['value']
    table = soup.find('table', id='ctl00_ContentPlaceHolder1_Gridview1')
    if not table:
        return jsonify({'error': 'Subwise table not found'}), 500
    rows = table.find_all('tr')
    datewise_data=defaultdict(list)
    for row in rows[1:]:
        cols = row.find_all('td')
        sno = int(cols[0].text)
        date = datetime.strptime(cols[1].text.strip(), "%d %b %Y").strftime("%Y-%m-%d")  #Converts to standard date format (YYYY-MM-DD)
        period = int(cols[2].text)
        sub = cols[3].text.strip()
        status=cols[4].text.strip()
        datewise_data[date].append({
            "SNo":sno,
            "Subject":sub,
            "Period":period,
            "Status":status
        })

    response_data = {
        'status': 'success',
        'start_date': datetime.strptime(start_date, "%d-%b-%Y").strftime("%Y-%m-%d") , #Converts to standard date format (YYYY-MM-DD)
        'end_date': datetime.strptime(end_date, "%d-%b-%Y").strftime("%Y-%m-%d"), #Converts to standard date format (YYYY-MM-DD)
        'datewise':datewise_data
    }

    return jsonify(response_data)

#Helper Functions:
def login(username,password):
    session = requests.Session()
    soup = BeautifulSoup(session.get(login_url).content, 'lxml')

    try:
        viewstate = soup.select_one('input[name="__VIEWSTATE"]')['value']
        eventvalidation = soup.select_one('input[name="__EVENTVALIDATION"]')['value']
        viewstategenerator = soup.select_one('input[name="__VIEWSTATEGENERATOR"]')['value']
    except TypeError:
        return None, ({'error_text': 'Failed to parse login page','error_code':500})

    login_payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTVALIDATION': eventvalidation,
        'ctl00$cph1$rdbtnlType': '2',
        'ctl00$cph1$txtStuUser': username,
        'ctl00$cph1$txtStuPsw': password,
        '__ASYNCPOST': 'true',
        'ctl00$cph1$btnStuLogin': 'Login »'
    }

    response = session.post(login_url, data=login_payload, headers=headers)
    if "Invalid" in response.text:
        return None, ({'error_text': 'Invalid Username or Password','error_code':401})
    return session, None

def fetch_attendance_page(username, password):
    session, error = login(username, password)
    if error:
        return None, error
    soup = BeautifulSoup(session.get(attendance_url).content, 'lxml')
    return soup, None

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000)) #Configure PORT env variable in your deployment server, if required
    app.run(host='0.0.0.0', port=port, debug=False)