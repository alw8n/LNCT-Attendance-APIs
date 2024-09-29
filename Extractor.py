import requests
from bs4 import BeautifulSoup
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
    'ctl00$cph1$rdbtnlType': '2',  # This value seems to indicate the type but idk
    'ctl00$cph1$hdnSID': '',
    'ctl00$cph1$hdnSNO': '',
    'ctl00$cph1$hdnRDURL': '',
    'ctl00$cph1$txtStuUser': '11151129265',  # replace with username
    'ctl00$cph1$txtStuPsw': '11151129265',  # replace with password
    '__ASYNCPOST': 'true',
    'ctl00$cph1$btnStuLogin': 'Login »'  # Button
}

response = session.post(login_url, data=payload, headers=headers)

print(response.text)  # First Response


redirected_url = "https://portal.lnct.ac.in/Accsoft2/Parents/ParentDesk.aspx"
redirect_response = session.get(redirected_url)
print(redirect_response.text)  #prints page after redirect