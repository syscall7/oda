#!/bin/bash
rm -rf /var/oda/cache/*
/var/www/oda/env/bin/python /var/www/oda/site/manage.py report_activity --settings=oda.settings.production
