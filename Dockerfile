FROM continuumio/miniconda3:4.10.3-alpine

WORKDIR /app

# Create the environment:
COPY environment.yml .
RUN conda env create -f environment.yml

# Make RUN commands use the new environment:
SHELL ["conda", "run", "-n", "production-env", "/bin/bash", "-c"]

# Demonstrate the environment is activated:
# RUN echo "Make sure flask is installed:"
# RUN python -c "import flask"

# The code to run when container is started:
COPY ./modules ./modules
COPY MRMSDataset.py .
ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "production-env", "python", "MRMSDataset.py"]
# docker pull continuumio/miniconda3:4.10.3-alpine
# docker build -t leaver/conda:0.3 .