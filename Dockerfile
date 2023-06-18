#FROM python
FROM continuumio/miniconda3

# Path: /app
WORKDIR /app

#ENV discord_token = {$token}
COPY . .

# Create a new Conda environment and install packages
RUN conda env create -f environment.yml
# Activate the Conda environment
RUN echo "source activate <environment_name>" > ~/.bashrc
ENV PATH /opt/conda/envs/<environment_name>/bin:$PATH


# run main.py
CMD ["python", "main.py"]

