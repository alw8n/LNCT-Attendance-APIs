from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
import math

app = Flask(__name__)
CORS(app)
@app.route('/scrape', methods=['POST'])
def scrape():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    desired_percentage = data.get('targetPercentage', 75)

    if not username or not password:
        return jsonify({'error': 'Missing username or password'}), 400

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    session = requests.Session()
    login_url = 'https://portal.lnct.ac.in/Accsoft2/StudentLogin.aspx'
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')

    try:
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
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
        return jsonify({'error': 'Login failed'}), 401

    attendance_url = "https://portal.lnct.ac.in/Accsoft2/Parents/StuAttendanceStatus.aspx"
    attendance_page = session.get(attendance_url)
    soup = BeautifulSoup(attendance_page.text, 'html.parser')

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

        classes_needed = "-"
        if percentage < desired_percentage:
            classes_needed = math.ceil(desired_percentage * held - 100 * present) / (100 - desired_percentage)

        attendance_data.append({
            'subject': sub,
            'classes_held': held,
            'classes_present': present,
            'current_percentage': round(percentage, 2),
            'classes_needed': round(classes_needed, 2) if classes_needed != "-" else "-"
        })

    return jsonify({
        'status': 'success',
        'overall_attendance': overall,
        'attendance_data': attendance_data
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
