FROM python

# Path: /app
WORKDIR /app

RUN pip install -U discord.py

ENV discord_token = MTExMjczNTY0MzExNDY4MDM2MQ.GqKZwF.xkssxtmPKE7C4RzEYAYoL-S6GuJop7I_9hyBQg

COPY . .

# run main.py
CMD ["python", "main.py"]

