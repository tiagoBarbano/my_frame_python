# Etapa 1: Build da aplicação usando Maven e JDK 17
FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /app

# Copia os arquivos necessários para o build
COPY pom.xml .
COPY src ./src

# Gera o JAR (sem rodar testes para acelerar)
RUN mvn clean package -DskipTests

# Etapa 2: Runtime enxuto com JRE 17
FROM eclipse-temurin:17-jre-alpine AS runtime

WORKDIR /app

# Copia o JAR gerado na etapa de build
COPY --from=build /app/target/*.jar app.jar

# Expõe a porta padrão do WebFlux
EXPOSE 8080

# Comando de execução
ENTRYPOINT ["java", "-jar", "app.jar"]
