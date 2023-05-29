FROM python

# Path: /app
WORKDIR /app

RUN pip install -U discord.py

ENV discord_token = {$token}
COPY . .

# run main.py
CMD ["python", "main.py"]

