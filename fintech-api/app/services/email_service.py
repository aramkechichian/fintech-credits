"""
Email service for sending notifications
Uses SMTP for sending emails
"""
import logging
from typing import Optional
import asyncio
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

# Optional import for aiosmtplib (may not be installed in test environments)
try:
    import aiosmtplib
    HAS_AIOSMTPLIB = True
except ImportError:
    HAS_AIOSMTPLIB = False

logger = logging.getLogger(__name__)

# Country to language mapping
COUNTRY_LANGUAGE_MAP = {
    "Brazil": "pt",  # Portugués
    "Mexico": "es",  # Español
    "Spain": "es",  # Español
    "Portugal": "pt",  # Portugués
    "Italy": "it",  # Italiano
    "Colombia": "es",  # Español
}


async def send_email_async(
    to: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None
) -> bool:
    """
    Send email asynchronously using SMTP
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Plain text email body
        html_body: Optional HTML email body
        
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Check if aiosmtplib is available
        if not HAS_AIOSMTPLIB:
            logger.warning(f"aiosmtplib not installed. Email to {to} would be sent with subject: {subject}")
            logger.info(f"📧 Email (not sent - aiosmtplib not installed):")
            logger.info(f"   To: {to}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body: {body[:100]}..." if len(body) > 100 else f"   Body: {body}")
            return False
        
        # Check if SMTP is configured
        if not settings.smtp_user or not settings.smtp_password:
            logger.warning(f"SMTP not configured. Email to {to} would be sent with subject: {subject}")
            logger.info(f"📧 Email (not sent - SMTP not configured):")
            logger.info(f"   To: {to}")
            logger.info(f"   Subject: {subject}")
            logger.info(f"   Body: {body[:100]}..." if len(body) > 100 else f"   Body: {body}")
            return False
        
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = settings.smtp_from_email
        message["To"] = to
        message["Subject"] = subject
        
        # Add plain text and HTML parts
        part1 = MIMEText(body, "plain", "utf-8")
        message.attach(part1)
        
        if html_body:
            part2 = MIMEText(html_body, "html", "utf-8")
            message.attach(part2)
        
        # Send email using aiosmtplib
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_user,
            password=settings.smtp_password,
            use_tls=settings.smtp_use_tls,
        )
        
        logger.info(f"✅ Email sent successfully to {to}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error sending email to {to}: {str(e)}", exc_info=True)
        return False


async def send_credit_request_status_notification(
    email: str,
    full_name: str,
    status: str,
    request_id: str,
    country: str
) -> bool:
    """
    Send notification email when credit request status changes
    Email language is determined by the country
    
    Args:
        email: Recipient email address
        full_name: Full name of the recipient
        status: New status (in_review, approved, rejected)
        request_id: Credit request ID
        country: Country name (Brazil, Mexico, Spain, etc.) to determine language
        
    Returns:
        bool: True if email was sent successfully
    """
    # Get language based on country
    language = COUNTRY_LANGUAGE_MAP.get(country, "es")  # Default to Spanish
    
    # Email messages by language and status
    status_messages = {
        "es": {  # Spanish
            "in_review": {
                "subject": "Tu solicitud de crédito está en revisión",
                "body": f"Hola {full_name},\n\nTu solicitud de crédito (ID: {request_id}) ha sido puesta en revisión. Nuestro equipo la está analizando y te notificaremos cuando tengamos una respuesta.\n\nGracias por tu paciencia.",
                "html_body": f"""
                <html>
                <body>
                    <h2>Tu solicitud de crédito está en revisión</h2>
                    <p>Hola {full_name},</p>
                    <p>Tu solicitud de crédito (ID: {request_id}) ha sido puesta en revisión. Nuestro equipo la está analizando y te notificaremos cuando tengamos una respuesta.</p>
                    <p>Gracias por tu paciencia.</p>
                </body>
                </html>
                """
            },
            "approved": {
                "subject": "¡Tu solicitud de crédito ha sido aprobada!",
                "body": f"Hola {full_name},\n\n¡Excelentes noticias! Tu solicitud de crédito (ID: {request_id}) ha sido aprobada.\n\nNos pondremos en contacto contigo pronto con los próximos pasos.",
                "html_body": f"""
                <html>
                <body>
                    <h2>¡Tu solicitud de crédito ha sido aprobada!</h2>
                    <p>Hola {full_name},</p>
                    <p>¡Excelentes noticias! Tu solicitud de crédito (ID: {request_id}) ha sido aprobada.</p>
                    <p>Nos pondremos en contacto contigo pronto con los próximos pasos.</p>
                </body>
                </html>
                """
            },
            "rejected": {
                "subject": "Actualización sobre tu solicitud de crédito",
                "body": f"Hola {full_name},\n\nLamentamos informarte que tu solicitud de crédito (ID: {request_id}) no ha sido aprobada en esta ocasión.\n\nSi tienes preguntas, no dudes en contactarnos.",
                "html_body": f"""
                <html>
                <body>
                    <h2>Actualización sobre tu solicitud de crédito</h2>
                    <p>Hola {full_name},</p>
                    <p>Lamentamos informarte que tu solicitud de crédito (ID: {request_id}) no ha sido aprobada en esta ocasión.</p>
                    <p>Si tienes preguntas, no dudes en contactarnos.</p>
                </body>
                </html>
                """
            }
        },
        "pt": {  # Portuguese
            "in_review": {
                "subject": "Sua solicitação de crédito está em revisão",
                "body": f"Olá {full_name},\n\nSua solicitação de crédito (ID: {request_id}) foi colocada em revisão. Nossa equipe está analisando e notificaremos você quando tivermos uma resposta.\n\nObrigado pela sua paciência.",
                "html_body": f"""
                <html>
                <body>
                    <h2>Sua solicitação de crédito está em revisão</h2>
                    <p>Olá {full_name},</p>
                    <p>Sua solicitação de crédito (ID: {request_id}) foi colocada em revisão. Nossa equipe está analisando e notificaremos você quando tivermos uma resposta.</p>
                    <p>Obrigado pela sua paciência.</p>
                </body>
                </html>
                """
            },
            "approved": {
                "subject": "Sua solicitação de crédito foi aprovada!",
                "body": f"Olá {full_name},\n\nExcelentes notícias! Sua solicitação de crédito (ID: {request_id}) foi aprovada.\n\nEntraremos em contato em breve com os próximos passos.",
                "html_body": f"""
                <html>
                <body>
                    <h2>Sua solicitação de crédito foi aprovada!</h2>
                    <p>Olá {full_name},</p>
                    <p>Excelentes notícias! Sua solicitação de crédito (ID: {request_id}) foi aprovada.</p>
                    <p>Entraremos em contato em breve com os próximos passos.</p>
                </body>
                </html>
                """
            },
            "rejected": {
                "subject": "Atualização sobre sua solicitação de crédito",
                "body": f"Olá {full_name},\n\nLamentamos informar que sua solicitação de crédito (ID: {request_id}) não foi aprovada desta vez.\n\nSe tiver dúvidas, não hesite em nos contatar.",
                "html_body": f"""
                <html>
                <body>
                    <h2>Atualização sobre sua solicitação de crédito</h2>
                    <p>Olá {full_name},</p>
                    <p>Lamentamos informar que sua solicitação de crédito (ID: {request_id}) não foi aprovada desta vez.</p>
                    <p>Se tiver dúvidas, não hesite em nos contatar.</p>
                </body>
                </html>
                """
            }
        },
        "it": {  # Italian
            "in_review": {
                "subject": "La tua richiesta di credito è in revisione",
                "body": f"Ciao {full_name},\n\nLa tua richiesta di credito (ID: {request_id}) è stata messa in revisione. Il nostro team la sta analizzando e ti notificheremo quando avremo una risposta.\n\nGrazie per la tua pazienza.",
                "html_body": f"""
                <html>
                <body>
                    <h2>La tua richiesta di credito è in revisione</h2>
                    <p>Ciao {full_name},</p>
                    <p>La tua richiesta di credito (ID: {request_id}) è stata messa in revisione. Il nostro team la sta analizzando e ti notificheremo quando avremo una risposta.</p>
                    <p>Grazie per la tua pazienza.</p>
                </body>
                </html>
                """
            },
            "approved": {
                "subject": "La tua richiesta di credito è stata approvata!",
                "body": f"Ciao {full_name},\n\nOttime notizie! La tua richiesta di credito (ID: {request_id}) è stata approvata.\n\nTi contatteremo presto con i prossimi passi.",
                "html_body": f"""
                <html>
                <body>
                    <h2>La tua richiesta di credito è stata approvata!</h2>
                    <p>Ciao {full_name},</p>
                    <p>Ottime notizie! La tua richiesta di credito (ID: {request_id}) è stata approvata.</p>
                    <p>Ti contatteremo presto con i prossimi passi.</p>
                </body>
                </html>
                """
            },
            "rejected": {
                "subject": "Aggiornamento sulla tua richiesta di credito",
                "body": f"Ciao {full_name},\n\nCi dispiace informarti che la tua richiesta di credito (ID: {request_id}) non è stata approvata questa volta.\n\nSe hai domande, non esitare a contattarci.",
                "html_body": f"""
                <html>
                <body>
                    <h2>Aggiornamento sulla tua richiesta di credito</h2>
                    <p>Ciao {full_name},</p>
                    <p>Ci dispiace informarti che la tua richiesta di credito (ID: {request_id}) non è stata approvata questa volta.</p>
                    <p>Se hai domande, non esitare a contattarci.</p>
                </body>
                </html>
                """
            }
        }
    }
    
    # Get messages for the language
    language_messages = status_messages.get(language, status_messages["es"])  # Default to Spanish
    message = language_messages.get(status)
    
    if not message:
        logger.warning(f"Unknown status for email notification: {status}")
        return False
    
    return await send_email_async(
        to=email,
        subject=message["subject"],
        body=message["body"],
        html_body=message.get("html_body")
    )
