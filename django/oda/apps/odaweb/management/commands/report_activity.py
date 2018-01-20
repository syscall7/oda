# Generate a report of what was uploaded in a given day
#
import os
import hashlib
import MySQLdb
import traceback
import smtplib

from email.mime.text import MIMEText
from collections import namedtuple
from datetime import datetime, timedelta
from subprocess import Popen, PIPE

from django.core.management.base import BaseCommand
from django.template import Template, Context
from django.conf import settings
from django.contrib.auth.models import User

from oda.apps.odaweb.models import OdaMaster, BinaryFileModel

# pointer to upload directory
UPLOAD_DIR = '/tmp/odaweb2/uploads'

# email addresses of sender and receivers
SENDER = 'admin@onlinedisassembler.com'
RECEIVERS = [
    'anthony@onlinedisassembler.com',
    #'tom@onlinedisassembler.com',
    #'davis@onlinedisassembler.com',
]

# our template (could just as easily be stored in a separate file)
template = """
{% load humanize %}
<html>
<head>
<title>ODA Upload Report - {{ startdate }} to {{ enddate }}</title>
<link rel="stylesheet" type="text/css" href="http://www.onlinedisassembler.com/static/css/oda2.css" />
</head>
<body>
<h3>{{ date }}</h3>

Day's Visitors: {{ num_days_unique_ips | intcomma }}<br>
Day's OdaMasters: {{ num_new_masters | intcomma }}<br>
Day's File Uploads: {{ num_new_binary_files | intcomma  }}<br>
Day's Binary Strings: {{ num_new_binary_strings | intcomma }}<br>
Day's Bytes Uploaded: {{ num_new_bytes | filesizeformat }}<br>
Day's Unique Files: {{ num_new_unique_files | intcomma }}<br>
<br>

New Visitors: {{ num_new_unique_ips | intcomma }}<br>
New User Accounts: {{ num_new_users | intcomma }}<br>
<br>

Total User Accounts: {{ num_total_unique_users | intcomma }}<br>
Total Unique IPs: {{ num_total_unique_ips | intcomma }}<br>
Total ODA Masters: {{ num_total_oda_masters | intcomma }}<br>
<br>

<div style="border:3px solid #6B7C70; border-radius: 6px; float:left">
<table cellpadding="3" style="border:0px solid #6B7C70; border-spacing: 0;">
    <thead>
        <tr style="background-color:#6B7C70;color:white;font-weight:bold; padding: 5px">
            <!--<th align="left" style="padding: 2px 15px; -moz-border-radius: 6px 0 0 0; -webkit-border-radius: 6px 0 0 0;border-radius: 6px 0 0 0;">File Name</th>-->
            <th align="left" style="padding: 2px 15px;">File Name</th>
            <th>File Size</th>
            <th>File Description</th>
            <th>File MD5</th>
            <th>IP Address</th>
            <!--<th style="-moz-border-radius: 0 6px 0 0; -webkit-border-radius: 0 6px 0 0;border-radius: 0 6px 0 0;">Time</th>-->
            <th>Time</th>
        </tr>
    </thead>
    <tbody>
        {% for upload in new_binary_files %}
        <tr style="background-color:{% cycle '#B2CEBB' '#FFFFFF' %}">
            <td style="padding: 2px 15px;"><a href=http://www.onlinedisassembler.com/odaweb/{{ upload.shortname }}>{{ upload.filename }}</a></td>
            <td style="padding: 2px 15px;">{{ upload.size|filesizeformat }}</td>
            <td style="padding: 2px 15px;">{{ upload.desc }}</td>
            <td style="padding: 2px 15px; font-family:monospace">{{ upload.md5 }}</td>
            <td style="padding: 2px 15px;">{{ upload.ip }}</td>
            <td style="padding: 2px 15px;">{{ upload.date }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
</div>
</body>
</html>
"""


def generate_report(start, end):

    unique_md5s = []
    num_new_bytes = 0
    new_binary_files = []

    num_new_binary_strings = 0

    unique_binary_files = 0
    unique_binary_strings = 0

    Upload = namedtuple('Upload', 'date shortname filename ip desc size md5')

    # fetch all the new oda masters from today
    oda_masters = OdaMaster.objects.filter(creation_date__range=[start, end])

    for m in oda_masters:

        # how can this happen?
        if m.odb_file is None:
            continue

        if type(m.odb_file.binary) == BinaryFileModel:
            filename = m.odb_file.binary.name

            desc = 'fixme' # ' '.join(m.odb_file.binary.desc())[0:48]
            size = m.odb_file.binary.size()
            num_new_bytes += size
            md5 = m.odb_file.binary.md5()
            if md5 not in unique_md5s:
                unique_md5s.append(md5)
            md5 = "%s...%s" % (md5[0:6], md5[-6:])

            timestamp = m.creation_date.strftime('%I:%M:%S %p')

            u = Upload(timestamp, m.short_name, filename, m.ipAddress, desc=desc, size=size, md5=md5)
            new_binary_files.append(u)
        else:
            num_new_binary_strings += 1
    
    # the set of unique IP addresses not including the ones from this day
    lifetime_unique_ips = set(OdaMaster.objects.filter(creation_date__lt=start).values_list('ipAddress', flat=True).distinct())

    # the set of unique IP addresses from this day
    days_unique_ips = set(OdaMaster.objects.filter(creation_date__gte=start).values_list('ipAddress', flat=True).distinct())

    # IPs never seen before today
    num_new_unique_ips = len(lifetime_unique_ips & days_unique_ips)

    t = Template(template)
    c = Context({
        'startdate': start.isoformat(),
        'enddate': end.isoformat(),
        'num_new_masters': len(oda_masters),
        'num_new_binary_files': len(new_binary_files),
        'num_new_users': User.objects.filter(date_joined__range=[start, end]).count(),
        'num_new_binary_strings': num_new_binary_strings,
        'new_binary_files': new_binary_files,
        'num_new_bytes': num_new_bytes,
        'num_new_unique_files': len(unique_md5s),
        'num_days_unique_ips': oda_masters.values('ipAddress').distinct().count(),
        'num_new_unique_ips': num_new_unique_ips,
        'num_total_unique_users': User.objects.all().count(),
        'num_total_unique_ips': OdaMaster.objects.all().values('ipAddress').distinct().count(),
        'num_total_oda_masters': OdaMaster.objects.all().count(),
        })

    return t.render(c)

def email(start, end, report):
    # Create a text/plain message
    msg = MIMEText(report.encode('utf-8'), 'html', _charset='utf-8')

    msg['Subject'] = 'ODA Upload Report %s' % start.strftime('%m/%d/%y')
    msg['From'] = SENDER
    msg['To'] =''.join(['%s, ' % i for i in RECEIVERS])

    # Send the message via our own SMTP server, but don't include the
    # envelope header.
    s = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT)
    s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
    s.sendmail(SENDER, RECEIVERS, msg.as_string())
    s.quit()


class Command(BaseCommand):
    args = 'format=<text|email>'
    help = 'Example: ./migrate.py report_activity'

    def handle(self, *args, **options):
        # run the report for yesterday's date
        end = datetime.utcnow()
        start = end - timedelta(hours=24)
    
        # try to run the report
        try:
            report = generate_report(start, end)
        except:
            report = '<pre>%s</pre>' % traceback.format_exc()

        # email the report or the caught exception
        email(start, end, report)

