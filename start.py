from os import urandom
from threading import Thread

from typer import Option, style, colors, echo, Typer, run, Context

environ_folder = 'environment'


def callback():
    echo(style("RabbitMQ Configuration", fg=colors.GREEN, bold=True))


app = Typer(chain=True)


@app.callback(invoke_without_command=True)
def cli(ctx: Context):
    echo(style("RabbitMQ Configuration", fg=colors.GREEN, bold=True))
    ctx.invoke(build_celery)


@app.command('celery')
def build_celery(
        rabbitmq_user: str = Option(..., prompt='User'),
        rabbitmq_password: str = Option(..., prompt='Password', hide_input=True),
):
    with open(f'{environ_folder}/rabbit.env', 'w') as f:
        f.write(f'RABBITMQ_DEFAULT_USER={rabbitmq_user}\n')
        f.write(f'RABBITMQ_DEFAULT_PASS={rabbitmq_password}')
    with open(f'{environ_folder}/celery.env', 'w') as f:
        f.write(f'CELERY_BROKER_URL=amqp://{rabbitmq_user}:{rabbitmq_password}@rabbitmq/\n')
        f.write('C_FORCE_ROOT=1')
    with open(f'{environ_folder}/fastapi.env', 'w') as f:
        f.write(f'CELERY_BROKER_URL=amqp://{rabbitmq_user}:{rabbitmq_password}@rabbitmq/\n')


@app.command('mailjet')
def build_mailjet(mailjet_api_key: str = Option(..., prompt='API KEY'),
                  mailjet_api_secret: str = Option(..., prompt='API SECRET'),
                  mailjet_sender_email: str = Option(..., prompt='Sender Email')):
    with open(f'{environ_folder}/fastapi.env', 'a') as f:
        f.write(f'SECRET_KEY={urandom(24).hex()}\n')
        f.write(f'MAILJET_API_KEY={mailjet_api_key}\n')
        f.write(f'MAILJET_API_SECRET={mailjet_api_secret}\n')
        f.write(f'SENDER_EMAIL={mailjet_sender_email}\n')


@app.command('mongo')
def build_mongo(user: str = Option(..., prompt='User'),
                password: str = Option(..., prompt='Password', hide_input=True),
                host: str = Option(..., prompt='Host')):
    with open(f'{environ_folder}/fastapi.env', 'a') as f:
        f.write(f'MONGO_USER={user}\n')
        f.write(f'MONGO_PASSWORD={password}\n')
        f.write(f'MONGO_HOST={host}\n')
        f.write(f'MONGO_DB={"padel"}\n')


if __name__ == '__main__':

    echo(style("RabbitMQ Configuration", fg=colors.GREEN, bold=True))
    x = Thread(target=run, args=(build_celery,))
    x.start()
    x.join()

    echo(style("Mailjet Configuration", fg=colors.GREEN, bold=True))
    y = Thread(target=run, args=(build_mailjet,))
    y.start()
    y.join()

    echo(style("MongoDB Configuration", fg=colors.GREEN, bold=True))
    z = Thread(target=run, args=(build_mongo,))
    z.start()
    z.join()

