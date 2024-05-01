package com.github.msorkhpar.wikistorage;

import com.github.msorkhpar.wikistorage.service.WikidataService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;


import java.nio.file.DirectoryStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;

@SpringBootApplication
@RequiredArgsConstructor
@EnableJpaRepositories
@Slf4j
public class WikidataGraphBuilderApplication implements CommandLineRunner {
    @Value("${app.dump-files.dir}")
    private String baseDirectory;
    @Value("${app.dump-files.pattern}")
    private String pattern;

    private final WikidataService wikidataProcessor;


    public static void main(String[] args) {
        SpringApplication.run(WikidataGraphBuilderApplication.class, args).close();
    }

    @Override
    public void run(String... args) throws Exception {
        List<Path> dumpFiles = new ArrayList<>();
        try (DirectoryStream<Path> stream = Files.newDirectoryStream(Paths.get(baseDirectory), pattern)) {
            for (Path dumpFile : stream) {
                logger.info("Dump file [{}] has been detected.", dumpFile.getFileName().toString());
                dumpFiles.add(dumpFile);
            }
        }
        wikidataProcessor.constructWikidataTree(dumpFiles.reversed());
        logger.info("Extraction process is Done!");

    }
}
