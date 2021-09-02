FROM nvidia/cuda:11.2.0-base-ubuntu18.04

# ==========================================================
#       Update system and install OS dependencies           
# ==========================================================
RUN apt update
RUN apt -y install -y python3.6 curl unzip wget virtualenv \
  --no-install-recommends \
  --no-install-suggests
RUN apt-get -y install python3-pip python3-virtualenv


# ==========================================================
#               Setup virtual environment                   
# ==========================================================
RUN mkdir /venv
WORKDIR /venv
RUN virtualenv --python=/usr/bin/python3.6 /venv/ \
  --prompt="(IDC [Python + Node.js])"
ENV PATH="/venv/bin:$PATH"


# ==========================================================
#              Virtual Environment: Python                  
# ==========================================================
COPY ./python_requirements.txt /venv/python_requirements.txt
RUN pip install -r /venv/python_requirements.txt


# ==========================================================
#               Virtual Environment: Node.js                
# ==========================================================
COPY ./node_env.cfg /venv/node_env.cfg
RUN . /venv/bin/activate && \
  nodeenv --config-file=/venv/node_env.cfg --python-virtualenv


# ==========================================================
#                     Running system                        
# ==========================================================
COPY --chmod=0555 ./docker-entrypont.sh /
ENTRYPOINT [ "/docker-entrypont.sh" ]

WORKDIR /app/server/
CMD /docker-entrypont.sh