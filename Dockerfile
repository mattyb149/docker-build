from cogniteev/oracle-java:java7

RUN apt-get update
RUN apt-get install -y git curl python python-jinja2

RUN adduser --disabled-password --gecos '' buildguy
RUN adduser --disabled-password --gecos '' gitguy

RUN sudo -u buildguy bash -c "cd /home/buildguy && curl http://www.apache.org/dist/maven/maven-3/3.3.3/binaries/apache-maven-3.3.3-bin.tar.gz | tar -xz"
RUN sudo -u buildguy bash -c "cd /home/buildguy && curl https://www.apache.org/dist/ant/binaries/apache-ant-1.9.6-bin.tar.gz | tar -xz"

RUN echo 'export JAVA_HOME=/usr/lib/jvm/java-7-oracle' >> ~buildguy/.profile
RUN echo 'export PATH="$JAVA_HOME/bin:$PATH"' >> ~buildguy/.profile
RUN echo 'export PATH="/home/buildguy/apache-ant-1.9.6/bin:$PATH"' >> ~buildguy/.profile
RUN echo 'export PATH="/home/buildguy/apache-maven-3.3.3/bin:$PATH"' >> ~buildguy/.profile
RUN mkdir ~buildguy/.ssh/

ADD git.py /home/gitguy/
ADD updatePr.py /home/gitguy/
ADD templates/ /home/gitguy/templates/
RUN chown -R gitguy:gitguy ~gitguy/
RUN chmod +x ~gitguy/git.py

ADD settings.xml /home/buildguy/.m2/
ADD build.py /home/buildguy/
ADD lib/ /home/buildguy/lib/
ADD start.sh /root/
RUN mkdir /home/buildguy/aggregate-metrics
RUN mkdir /home/buildguy/.ivy2
RUN chmod +x ~buildguy/build.py
RUN chmod +x /root/start.sh

RUN chown -R buildguy:buildguy /home/buildguy

ENTRYPOINT ["/root/start.sh"]
