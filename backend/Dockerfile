FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn -B -q dependency:go-offline
COPY src ./src
RUN mvn -B -q package -DskipTests

# JDK (not JRE) so javac exists, plus g++, python3 and node: the built-in code runner (EXEC_LOCAL) compiles submissions here.
FROM eclipse-temurin:21-jdk
RUN apt-get update \
 && apt-get install -y --no-install-recommends g++ python3 nodejs util-linux \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --no-create-home --shell /usr/sbin/nologin --uid 10001 runner
WORKDIR /app
COPY --from=build /app/target/*.jar app.jar
ENV JAVA_OPTS="-XX:MaxRAMPercentage=60" \
    EXEC_LOCAL=true \
    EXEC_RUN_AS=runner
EXPOSE 8080
CMD ["sh", "-c", "java $JAVA_OPTS -jar app.jar"]
