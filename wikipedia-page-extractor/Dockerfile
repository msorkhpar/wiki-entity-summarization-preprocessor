FROM maven:3.9.4-eclipse-temurin-21-alpine as build
WORKDIR /workspace/app

COPY lombok.config .
COPY pom.xml .
COPY wikipedia_page_extractor wikipedia_page_extractor

RUN mvn install -DskipTests
RUN mkdir -p wikipedia_page_extractor/target/dependency && (cd wikipedia_page_extractor/target/dependency; jar -xf ../*.jar)

FROM eclipse-temurin:21_35-jdk
VOLUME /tmp
ARG DEPENDENCY=/workspace/app/wikipedia_text_extractor/target/dependency
COPY --from=build ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY --from=build ${DEPENDENCY}/META-INF /app/META-INF
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
ENTRYPOINT ["java","-cp","app:app/lib/*","com.github.msorkhpar.pageextextractor.WikipediaPageExractorApplication"]