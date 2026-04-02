import requests
from django.conf import settings
from requests import Response


def create_email_payload(
    user_email: str, link: str = "", mail_type: str = "email_verify"
) -> dict:
    """
    mail_type: defaults to "email_verify" - verify user email.
    Other options are: "password_reset" for password reset,
    "email_change" for changing email address.
    "email_change_warn" for a warning to old email address during email change.
    """
    extra_style = ""
    if mail_type == "email_verify":
        subject = "Drinkly Email verification"
        intro = (
            "Thank you for registration! To confirm your "
            "email, please click on the button or the link below. "
            f"The link is valid for {int(settings.EMAIL_VERIFY_RESET_TIMEOUT) // 3600} hour(s)."
            "If you didn't invoke this action, just ignore it."
        )
        button_text = "Verify"
    elif mail_type == "password_reset":
        subject = "Drinkly password reset"
        intro = (
            "You've requested a password reset on Drinkly. To confirm "
            "reset, please click on the button or the link below. "
            f"The link is valid for {int(settings.PASSWORD_RESET_TIMEOUT) // 3600} hour(s)."
        )
        button_text = "Reset"
    elif mail_type == "email_change_warn":
        subject = "Drinkly Email change notification"
        intro = (
            "Someone requested an email change for your account on Drinkly. "
            "If it wasn't you, login into your account and change password."
        )
        button_text = ""
        extra_style = "display: none; "
    else:
        subject = "Drinkly Email change"
        intro = (
            "You've requested an email change on Drinkly. To confirm your "
            "new email, please click on the button or the link below. "
            f"The link is valid for {int(settings.EMAIL_VERIFY_RESET_TIMEOUT) // 3600} hour(s)."
            "If you didn't invoke this action, just ignore it."
        )
        button_text = "Change"

    payload = {
        "from": f"Drinkly <{settings.EMAIL_DOMAIN}>",
        "to": user_email,
        "subject": subject,
        "text": f"Hello,\n{intro}\n{link}\nWith all respect,\nDrinkly team.",
        "html": f"""
        <body style="margin:0; padding:0; background-color:#f4f4f4; font-family:Arial, sans-serif;">
          <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color:#f4f4f4; padding:20px 0;">
            <tr>
              <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" border="0" style="background-color:#ffffff; border-radius:8px; overflow:hidden;">
                  
                  <tr>
                    <td style="background-color:#7E2F4E; color:#ffffff; padding:20px; text-align:center; font-size:24px;">
                      Drinkly
                    </td>
                  </tr>
        
                  <tr>
                    <td style="padding:30px; color:#333333; font-size:16px; line-height:1.5;">
                      <p>Hello,</p>
                      
                      <p>{intro}</p>
                      
                      <p style="{extra_style}text-align:center; margin:30px 0;">
                        <a href="{link}" 
                           style="{extra_style}background-color:#7E2F4E; color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:5px; display:inline-block;">
                          {button_text}
                        </a>
                      </p>
                      
                      <p style="{extra_style}margin:30px;">
                        <a href="{link}" style="{extra_style}">{link}</a>
                      </p>
        
                      <p>With all respect,<br>Drinkly Team</p>
                    </td>
                  </tr>
        
                  <tr>
                    <td style="background-color:#f0f0f0; padding:15px; text-align:center; font-size:12px; color:#888888;">
                      © All rights reserved
                    </td>
                  </tr>
        
                </table>
              </td>
            </tr>
          </table>
        </body>
        """,
    }

    return payload


def send_email_via_provider(body: dict) -> Response:
    response = requests.post(
        f"{settings.EMAIL_API_BASE_URL}",
        json=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.EMAIL_API_KEY}",
            "User-Agent": "drinkly-app/1.0",
        },
    )
    return response
