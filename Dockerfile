FROM centos7

RUN echo "**** update packages ****"
RUN yum -y update

RUN echo "**** setup tmp folder ****"
RUN rm -rf /tmp/tmp-con
RUN mkdir -p /tmp/tmp-con

#install bandit and deps
RUN echo "**** install pip and bandit ****"
RUN yum -y install python-pip
RUN pip install --no-cache-dir -U bandit

#install brakeman and deps
RUN echo "**** install gem and brakeman ****"
RUN yum -y install gem
RUN gem install brakeman

#install truffleHog and deps
RUN echo "**** install truffleHog ****"
RUN pip install --no-cache-dir -U trufflehog

WORKDIR /tmp/tmp-con
