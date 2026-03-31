import requests
from django.conf import settings
from requests import Response


def create_email_payload(
    user_email: str, link: str, mail_type: str = "verify"
) -> dict:
    """
    mail_type: defaults to "verify" - verify user email.
    Other options are: "password" for password reset.
    """
    if mail_type == "verify":
        subject = "Drinkly Email verification"
        intro = (
            "Thank you for registration! To confirm your "
            "email, please click on the link below:"
        )
        button_text = "Verify"
    else:
        subject = "Drinkly password reset"
        intro = (
            "You've requested a password reset on Drinkly."
            " To confirm reset, please click on the link below:"
        )
        button_text = "Reset"

    payload = {
        "from": f"{settings.EMAIL_DOMAIN}",
        "to": user_email,
        "subject": subject,
        "text": f"Hello,\n{intro}\n{link}\nIf you didn't invoke this action "
        f"- just ignore the letter.\nWith all respect,\nDrinkly team.",
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
                      
                      <p style="text-align:center; margin:30px 0;">
                        <a href="{link}" 
                           style="background-color:#7E2F4E; color:#ffffff; padding:12px 24px; text-decoration:none; border-radius:5px; display:inline-block;">
                          {button_text}
                        </a>
                      </p>
        
                      <p>If you didn't invoke this action - just ignore the letter.</p>
        
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
            "User-Agent": "drinkly-app/1.0"
        },
    )
    return response
