import requests
from bs4 import BeautifulSoup
from tabulate import tabulate
import math

import timeit

start_time = timeit.default_timer()


def scrape(username,password=None,desired_percentage=60):
    if password==None:
        password=username
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://example.com/login',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    session = requests.Session()
    login_url = 'https://portal.lnct.ac.in/Accsoft2/StudentLogin.aspx'
    login_page = session.get(login_url)
    soup = BeautifulSoup(login_page.content, 'html.parser')

    viewstate = soup.find('input', {'name': '__VIEWSTATE'})['value']
    eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})['value']
    viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
    
    payload = {
        '__EVENTTARGET': '',
        '__EVENTARGUMENT': '',
        '__LASTFOCUS': '',
        '__VIEWSTATE': viewstate, 
        '__VIEWSTATEGENERATOR': viewstategenerator,  
        '__EVENTVALIDATION': eventvalidation,  
        'ctl00$cph1$rdbtnlType': '2',
        'ctl00$cph1$hdnSID': '',
        'ctl00$cph1$hdnSNO': '',
        'ctl00$cph1$hdnRDURL': '',
        'ctl00$cph1$txtStuUser': username,  # replace with username
        'ctl00$cph1$txtStuPsw': password,  # replace with password
        '__ASYNCPOST': 'true',
        'ctl00$cph1$btnStuLogin': 'Login »'
    }

    response = session.post(login_url, data=payload, headers=headers)

    LoginState = False

    vsoup = BeautifulSoup(session.get('https://portal.lnct.ac.in/Accsoft2/Parents/StuAttendanceStatus.aspx').text, 'html.parser')
    verifyState = str(vsoup.find('a', id='alertsDropdown'))
    if verifyState.find(str(username)) != -1:
        LoginState = True
        print("login successful")

    result = list()

    if LoginState:
        viewstate2 = vsoup.find('input', {'name': '__VIEWSTATE'})['value']
        viewstategenerator2 = vsoup.find('input', {'name': '__VIEWSTATEGENERATOR'})['value']
        student_id = vsoup.find('input', {'name': 'ctl00$hdnStudentID'})['value']
        student_name = vsoup.find('input', {'name': 'ctl00$ContentPlaceHolder1$txtStudentName'})['value']
        class_id = vsoup.find('input', {'name': 'ctl00$ContentPlaceHolder1$hdnclassid1'})['value']
        stu_id1 = vsoup.find('input', {'name': 'ctl00$ContentPlaceHolder1$hdnStuID1'})['value']

        print(student_id, student_name, class_id, stu_id1)
         
        attendance_payload = {
            "ctl00$ScriptManager1": "ctl00$ContentPlaceHolder1$agneepath|ctl00$ContentPlaceHolder1$btnshow",
            "__PREVIOUSPAGE": "W9Yjm1ohudklOzyMaXjR47kYTGjnhTrO0V1HAfjnmzK3D4BsGvQipSsfFM3S8qGmgBt_P7HGj0m3ynVTiqMqDg09FKghH4zStGteWuQNeSaglKFHQX6ughkRHV3fn2RQAiub3r92yO6V2UBrE5c5EA2",
            "ctl00$hdnCompanyID": "1", 
            "ctl00$hdnFinYearID": "19",
            "ctl00$hdnStudentID": student_id,
            "ctl00$ContentPlaceHolder1$txtStudentName": student_name,
            "ctl00$ContentPlaceHolder1$hdnclassid1": class_id,
            "ctl00$ContentPlaceHolder1$hdnStuID1": stu_id1, 
            "ctl00$ContentPlaceHolder1$ddlclass": '3615', #changes (for IoT:3501)
            "ctl00$ContentPlaceHolder1$txtfromdate": "18-Jan-2024",
            "ctl00$ContentPlaceHolder1$hdnExamSessionId": "71",
            "ctl00$ContentPlaceHolder1$txtTodate": "26-Jul-2024",
            "__EVENTTARGET": "",
            "__EVENTARGUMENT": "",
            "__LASTFOCUS": "",
            "__VIEWSTATE": viewstate2,
            "__VIEWSTATEGENERATOR": viewstategenerator2,
            "__ASYNCPOST": "true",
            "ctl00$ContentPlaceHolder1$btnshow": "Show"
        }

        response = session.post("https://portal.lnct.ac.in/Accsoft2/Parents/StuAttendanceStatus.aspx", data=attendance_payload, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extracting the table data
        overall=soup.find('span',id='ctl00_ContentPlaceHolder1_lblPer119').text[12:].rstrip(' %')
        print(f"OVERALL={overall}%")    
        table = soup.find('table', id='ctl00_ContentPlaceHolder1_grdSubjectWiseAttendance')
        rows = table.find_all('tr')
        
        # List to hold table data
        table_data = []
        
        # Extract header row
        headers = [header.text.strip() for header in rows[0].find_all('th')]+["Sub. Att.%","Class Need"]
        # Extract the remaining rows
        print("#######################################################################")
        for row in rows[1:]:
            cols = row.find_all('td')
            sub=cols[0].text.strip()
            held=int(cols[1].text.strip())
            present=int(cols[2].text.strip())
            percentage=(present/held)*100
        
            classes_needed="-"
            if percentage<desired_percentage:
                classes_needed=math.ceil(desired_percentage * held - 100 * present) / (100 - desired_percentage)
                print("\033[93m {}\033[00m".format(f"{sub}:\n Current Attendance = {percentage}\n For {desired_percentage}% attendance, you need to attend {classes_needed} more classes"),"\n#######################################################################")
            else:
                print("\033[92m {}\033[00m".format(f"{sub}:\n Current Attendance = {percentage}%"),"\n#######################################################################")
            
            table_data.append([col.text.strip() for col in cols]+[percentage,classes_needed])
        
        # Pretty print the table using tabulate
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        return 
    else:
        temp = {
            'response code': -1,
            'response': 'login failed'
        }
        result.append(temp)
        return result

# Example usage
#print(scrape('11151130265','alok1234'))
print(scrape('11156929783','Lnct@2023'))

end_time = timeit.default_timer()

execution_time = end_time - start_time
print(f"Time taken: {execution_time} seconds")