#!/usr/bin/env python
from celery import Celery
from twilio.rest import Client
from flask import Flask, request

import arrow
import os

from pytz import common_timezones

print(os.environ)
twilio_account_sid = os.environ['TWILIO_ACCOUNT_SID']
twilio_auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_number = os.environ['TWILIO_NUMBER']

client = Client(twilio_account_sid, twilio_auth_token)

application = Flask(__name__)

celery = Celery(application.import_name, broker=os.environ['CELERY_BROKER_URL'])

@application.route('/schedule', methods=['POST'])
def schedule():

    name = request.values.get('Name')
    number = request.values.get('Number')
    message = request.values.get('Body')
    at_time = request.values.get('DateTime')
    at_tzone = request.values.get('Timezone')

    fire_at = arrow.get(at_time, 'YYYY-MM-DDTHH:mm:ss', tzinfo=at_tzone).to('utc').naive

    send_scheduled_sms.apply_async(
        args=[name, number, message, at_time, at_tzone],
        eta=fire_at
    )
    return 'Created', 201

@celery.task()
def send_scheduled_sms(to_name, to_number, message, at_time, at_tzone):

    time = at_time #arrow.get(at_time).to(at_tzone)
    body = "Hello {0}. You have a message at {1}: {2}".format(
        to_name,
        time.format('h:mm a'),
        message
    )

    client.messages.create(
        to = to_number,
        from_ = twilio_number,
        body = body)

if __name__ == '__main__':
    application.run(debug=True, port=8000)
