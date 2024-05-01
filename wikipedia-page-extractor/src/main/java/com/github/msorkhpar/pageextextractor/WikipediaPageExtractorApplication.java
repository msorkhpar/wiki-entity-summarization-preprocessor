package com.github.msorkhpar.pageextextractor;

import com.github.msorkhpar.pageextextractor.service.WikipediaService;
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
public class WikipediaPageExtractorApplication implements CommandLineRunner {
    @Value("${app.dump-files.dir}")
    private String baseDirectory;
    @Value("${app.dump-files.pattern}")
    private String pattern;

    private final WikipediaService wikidataProcessor;


    public static void main(String[] args) {
        SpringApplication.run(WikipediaPageExtractorApplication.class, args).close();
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
        wikidataProcessor.extractWikipediaPages(dumpFiles.reversed());
        logger.info("Extraction process is Done!");
    }
}
