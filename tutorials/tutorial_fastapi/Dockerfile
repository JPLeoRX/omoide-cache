FROM python:3.8

# Update
RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 libgl1 -y

# Common dependencies
RUN pip install requests==2.25.1
RUN pip install fastapi==0.63.0
RUN pip install uvicorn==0.13.3
RUN pip install injectable==3.4.4
RUN pip install SQLAlchemy==1.3.23
RUN pip install yoyo-migrations==7.3.1
RUN pip install psycopg2-binary==2.8.6
RUN pip install python-multipart==0.0.5
RUN pip install numpy==1.19.4
RUN pip install opencv-python==4.5.1.48
RUN pip install xlrd==1.2.0
RUN pip install pyzipcode==3.0.1
RUN pip install simplestr==0.5.0
RUN pip install omoide-cache==0.1.2
RUN pip install tekleo-common-message-protocol==0.0.0.1
RUN pip install tekleo-common-utils==0.0.0.7

# Main app
COPY ./service-extapi /app
WORKDIR /app
RUN chmod a+x main.sh

# Run command
CMD './main.sh'
