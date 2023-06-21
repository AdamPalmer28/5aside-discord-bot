FROM python
#FROM continuumio/miniconda3

# install dependencies
RUN pip install discord.py pandas requests bs4

# Path: /app
WORKDIR /app

ENV discord_token=$TOKEN
ENV discord_channel_key=$CHANNEL
ENV discord_bot_path=$PATH

COPY . .


# run main.py
CMD ["python", "main.py"]

