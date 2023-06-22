FROM python
#FROM continuumio/miniconda3

# install dependencies
RUN pip install discord.py pandas requests bs4

# Path: /app
WORKDIR /app

COPY . .

# run main.py
CMD ["python", "main.py"]

