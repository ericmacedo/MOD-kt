FROM nvidia/cuda:11.2.0-base-ubuntu18.04


# ==========================================================
#       Update system and install OS dependencies           
# ==========================================================
RUN apt-get update && apt-get -y install \
  --no-install-recommends --no-install-suggests \
  python3.6 curl unzip wget virtualenv \
  python3-pip python3-virtualenv


# ==========================================================
#               Setup virtual environment                   
# ==========================================================
RUN mkdir -p /venv
WORKDIR /venv
RUN virtualenv --python=/usr/bin/python3.6 /venv/ \
  --prompt="(IDC [Python + Node.js])"

ENV PATH="/venv/bin:$PATH"


# ==========================================================
#              Virtual Environment: Python                  
# ==========================================================
COPY ./python_requirements.txt /venv/python_requirements.txt
RUN pip3 install --no-cache-dir -r /venv/python_requirements.txt

RUN mkdir -p  /venv/data/nltk \
  /venv/data/scikit_learn \
  /venv/data/transformers
ENV NLTK_DATA="/venv/data/nltk"
ENV SCIKIT_LEARN_DATA="/venv/data/scikit_learn"
ENV SENTENCE_TRANSFORMERS_HOME="/venv/data/transformers"


# ==========================================================
#               Virtual Environment: Node.js                
# ==========================================================
COPY ./node_env.cfg /venv/node_env.cfg
RUN . /venv/bin/activate && \
  nodeenv --config-file=/venv/node_env.cfg --python-virtualenv


# ==========================================================
#                     Running system                        
# ==========================================================
WORKDIR /app/server/

COPY ./docker_entrypoint.sh /
RUN chmod +x /docker_entrypoint.sh
ENTRYPOINT [ "/docker_entrypoint.sh" ]

CMD [ "/docker_entrypoint.sh" , "server"]