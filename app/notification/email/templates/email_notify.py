import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from app.config import settings
from email.mime.base import MIMEBase
from email import encoders
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


template_type = {
    "new_register": "app/notification/email/templates/register.html",
}
async def send_email(subject, type, data, cc=None, attachments=None):
    template_url = template_type[type]

    # Replace template string with dictionay
    html_template = read_html_template(template_url)

    template = Template(html_template)
    html_content = template.render(data)

    # Extract recipients from data
    recipients = [data.get("email")]

    if data and type and subject:
        # DB.Email_Log.insert_one({"email_id":gen_uuid(),"email":data.get('email'),"name":data.get('user_name'),"mob_no":data.get('mob_no')})
        print("email log added")

        send_html_email(subject, html_content,recipients, cc, attachments)     


def read_html_template(template_path):

    try:
        with open(template_path, "r") as file:
            return file.read()
    except:
        return {"message": "error in reading html file"}



def send_html_email(subject, html_content, recipients, cc=None, attachments=None):
    # Ensure recipients is a list of dictionaries
    if not isinstance(recipients, list):  # Check if it's already a list
        recipients = [{"email": recipients}]  # Wrap it in a list of dicts
    elif isinstance(recipients[0], str): # Check if the first element is string
        recipients = [{"email": recipient} for recipient in recipients]  # Wrap it in a list of dicts

    # Format cc recipients (if provided)
    if cc:
        if not isinstance(cc, list):
            cc = [{"email": cc}]
        elif isinstance(cc[0], str):
            cc = [{"email": c} for c in cc]

    # ... (rest of your code remains the same) ...
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key['api-key'] = settings.BREVO_API_KEY

    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        to=recipients,  # Now correctly formatted
        cc=cc,
        attachment=attachments,
        html_content=html_content,
        sender={"email": settings.BREVO_SENDER_EMAIL, "name": "Maein360"},
        subject=subject
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        print("Email sent successfully:", api_response)
    except ApiException as e:
        print("Exception when calling TransactionalEmailsApi->send_transac_email: %s\n" % e)    
