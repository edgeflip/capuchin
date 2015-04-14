from boto import ses
from admin import config
from flask import render_template
import logging

def load_templates(template, **kwargs):
    subject = render_template("email/{}/{}.subject".format(template, template), **kwargs)
    html = render_template("email/{}/{}.html".format(template, template), **kwargs)
    text = render_template("email/{}/{}.txt".format(template, template), **kwargs)
    return (subject, html, text)

def send(to, template, cc='', bcc='', **kwargs):
    conn = ses.connect_to_region(
        config.AWS_SES_REGION,
        aws_access_key_id=config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=config.AWS_SECRET_ACCESS_KEY
    )

    subject, html, text = load_templates(template, **kwargs)

    resp = conn.send_email(
        source=config.EMAIL_SOURCE,
        subject=subject,
        body=html,
        to_addresses=to,
        cc_addresses=cc,
        bcc_addresses=bcc,
        format='html',
        text_body=text,
    )

    logging.info(resp)
