import requests
import smtplib
import os
import paramiko
import linode_api4
import time
import schedule


EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')


def restart_container():
    print('Restarting the application..')
    ssh = paramiko.SSHClient
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('135.216.124.354', username='ubuntu', key_filename='Downloads/reethu_devops.pem')
    stdin, stdout, stderr = ssh.exec_command('docker start 2a26a42a4f96')
    print(stdin)
    print(stdout.readlines())
    ssh.close()

def send_notification(email_msg):
    print('Sending an email...')
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.ehlo()
        msg = f"Subject: SITE DOWN\n {email_msg}"
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.sendmail(EMAIL_ADDESS, EMAIL_PASSWORD, msg)

def monitor_application():

  try:

    response = requests.get('http://ec2-18-140-63-188.ap-southeast-1.compute.amazonaws.com:8080/')
    print(response.text)
    if response.status_code == 200:
      print('Application is running successfully')
    else:
     print('Application is down. Fix it!')
     msg = f'Application returned {response.status_code}'
     send_notification(msg)
     restart_container()


    except Exception as ex:
     print(f'Connection Error happend: {ex}')
     msg = 'Application not accessible at all'
     send_notification(msg)

schedule.every(5).seconds.do(monitor_application())
while True:
    schedule.run_pending()

   # restart the server
    print('Rebooting the server')
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    nginx_server = client.load(linode_api4.Instance, 25654847)
    nginx_server.reboot()

    # restart the application
    while True:
      nginx_server = client.load(linode_api4.Instance, 25654847)
    if nginx_server.status == 'running':
      restart_container()
       break