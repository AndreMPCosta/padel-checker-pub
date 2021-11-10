from os import environ

from mailjet_rest import Client

API_KEY = environ.get('MAILJET_API_KEY')
API_SECRET = environ.get('MAILJET_API_SECRET')

mailjet = Client(auth=(API_KEY, API_SECRET), version='v3.1')


async def send_email(user, message: str):
    data = {
        'Messages': [
            {
                "From": {
                    "Email": environ.get('SENDER_EMAIL'),
                    "Name": "Padel Checker"
                },
                "To": [
                    {
                        "Email": f"{user.email}",
                        "Name": f"{user.first_name} {user.last_name}"
                    }
                ],
                "Subject": "Vaga(s) nos seguinte(s) campo(s)",
                "TextPart": f"{message}",
                "CustomID": "PadelCheckerSender"
            }
        ]
    }
    result = mailjet.send.create(data=data)


if __name__ == '__main__':
    from app.models.user import UserModel
    import asyncio
    loop = asyncio.get_event_loop()
    u = loop.run_until_complete(UserModel.get_by_email('sample_email@domain.com'))
    loop.run_until_complete(send_email(u, 'teste2'))
