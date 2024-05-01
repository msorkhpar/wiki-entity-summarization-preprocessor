FROM maven:3.9.4-eclipse-temurin-21-alpine as build
WORKDIR /workspace/app

COPY lombok.config .
COPY pom.xml .
COPY wikidata_graph_builder wikidata_graph_builder

RUN mvn install -DskipTests
RUN mkdir -p wikidata_graph_builder/target/dependency && (cd wikidata_graph_builder/target/dependency; jar -xf ../*.jar)

FROM eclipse-temurin:21_35-jdk
VOLUME /tmp
ARG DEPENDENCY=/workspace/app/wikidata_graph_builder/target/dependency
COPY --from=build ${DEPENDENCY}/BOOT-INF/lib /app/lib
COPY --from=build ${DEPENDENCY}/META-INF /app/META-INF
COPY --from=build ${DEPENDENCY}/BOOT-INF/classes /app
ENTRYPOINT ["java","-cp","app:app/lib/*","com.github.msorkhpar.graphbuilder.WikidataGraphBuilderApplication"]