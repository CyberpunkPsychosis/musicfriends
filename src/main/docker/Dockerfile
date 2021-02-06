FROM openjdk:8-jdk-alpine
VOLUME /tmp
MAINTAINER ym
ADD docker-music-friends.jar app.jar
ENTRYPOINT ["java","-Djava.security.egd=file:/dev/./urandom","-jar","/app.jar"]
