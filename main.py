from flask import Flask, request, jsonify, redirect
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import math
import os

app = Flask(__name__)
CORS(app)

@app.route('/')
def redirect_to_github():
    return redirect("https://github.com/alw8n", code=302)

@app.route('/attendance-subwise', methods=['POST'])
def attendance_subwise():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    desired_percentage = data.get('targetPercentage', 75)
    first_login = data.get('firstLogin', False)

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
    }

    session = requests.Session()
    login_url = 'https://portal.lnct.ac.in/Accsoft2/StudentLogin.aspx'
    soup = BeautifulSoup(session.get(login_url).content, 'lxml')

    try:
        viewstate = soup.select_one('input[name="__VIEWSTATE"]')['value']
        eventvalidation = soup.select_one('input[name="__EVENTVALIDATION"]')['value']
        viewstategenerator = soup.select_one('input[name="__VIEWSTATEGENERATOR"]')['value']
    except TypeError:
        return jsonify({'error': 'Failed to parse login page'}), 500

    payload = {
        '__VIEWSTATE': viewstate,
        '__VIEWSTATEGENERATOR': viewstategenerator,
        '__EVENTVALIDATION': eventvalidation,
        'ctl00$cph1$rdbtnlType': '2',
        'ctl00$cph1$txtStuUser': username,
        'ctl00$cph1$txtStuPsw': password,
        '__ASYNCPOST': 'true',
        'ctl00$cph1$btnStuLogin': 'Login »'
    }

    response = session.post(login_url, data=payload, headers=headers)
    if "Invalid" in response.text:
        return jsonify({'error': 'Invalid Username or Password'}), 401

    attendance_url = "https://portal.lnct.ac.in/Accsoft2/Parents/StuAttendanceStatus.aspx"
    soup = BeautifulSoup(session.get(attendance_url).content, 'lxml')

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
        percentage = (present / held) * 100
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

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000)) #Configure PORT env variable in your deployment server, if required
    app.run(host='0.0.0.0', port=port, debug=False)