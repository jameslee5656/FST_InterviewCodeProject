FROM continuumio/miniconda:latest
WORKDIR /home/FST_CodeProject
COPY environment.yml ./
COPY requirements.txt ./
COPY app.py ./
COPY boot.sh ./
RUN chmod +x boot.sh

RUN conda env update -n base --file environment.yml
RUN python3 -m pip install -r requirements.txt
# RUN conda env create -f environment.yml
# RUN echo "source activate FST_CodeProject" &gt; ~/.bashrc
RUN echo "Make sure flask is installed:"

COPY app.py .
ENTRYPOINT ["python3", "app.py"]
# ENV PATH /opt/conda/envs/your-environment-name/bin:$PATH
# EXPOSE 5000

# ENTRYPOINT ["./boot.sh"]