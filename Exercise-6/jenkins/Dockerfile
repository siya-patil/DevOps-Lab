FROM jenkins/jenkins:lts-jdk21

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends docker-cli curl \
    && rm -rf /var/lib/apt/lists/*

USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator

COPY --chown=jenkins:jenkins Jenkinsfile /opt/delivery-monitoring/Jenkinsfile