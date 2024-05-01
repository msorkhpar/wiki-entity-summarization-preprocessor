package com.github.msorkhpar.wikistorage.service;

import com.github.msorkhpar.wikistorage.data.PersistenceService;
import com.github.msorkhpar.wikistorage.extractor.WikiDataEntityExtractor;
import com.github.msorkhpar.wikistorage.utils.KGTriple;
import com.github.msorkhpar.wikistorage.utils.WikidataEnglishInfoDTO;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.w3c.dom.Element;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Path;
import java.util.Optional;
import java.util.Set;
import java.util.concurrent.CompletableFuture;

import static com.github.msorkhpar.wikistorage.extractor.WikiDataEntityExtractor.*;
import static com.github.msorkhpar.wikistorage.utils.BZip2BufferReader.createBufferedReader;

@Service
@Slf4j
@RequiredArgsConstructor
class WikidataDumpFileService {

    private final PersistenceService persistenceService;


    @SneakyThrows
    @Async
    public CompletableFuture<Path> process(Path dumpFile, boolean multiStream) {
        String fileName = dumpFile.getFileName().toString();
        long start = System.currentTimeMillis();
        long counter = 1;
        logger.info("Start processing [{}]", fileName);
        try (BufferedReader reader = createBufferedReader(dumpFile, multiStream)) {
            StringBuilder xmlBuilder = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                if (xmlBuilder.isEmpty() && !line.trim().equals("<page>")) {
                    continue;
                }

                // <page> is found. Start building the current xml tag.
                xmlBuilder.append(line);

                if (line.trim().equals("</page>")) {
                    String pageString = xmlBuilder.toString();
                    try {
                        Element xmlPage = createPage(pageString);
                        processMetadata(extractMetadata(xmlPage));
                        processTriples(WikiDataEntityExtractor.extractTriples(xmlPage));
                    } catch (Exception e) {
                        logger.info("Extraction from the following text was not successful, {}", pageString);
                    }
                    // prepare the builder for the next page
                    xmlBuilder.setLength(0);
                    counter++;
                    if (counter++ % 10_000 == 0) {
                        logger.info("[{}] pages of [{}] is processed", counter, fileName);
                    }
                }
            }
        } catch (IOException e) {
            logger.error("Error processing [{}]", fileName, e);
            return CompletableFuture.failedFuture(e);
        }
        logger.info("Finish processing [{}] in [{}ms]", fileName, System.currentTimeMillis() - start);
        return CompletableFuture.completedFuture(dumpFile);
    }

    private void processTriples(Optional<Set<KGTriple>> tripleSet) {
        tripleSet.ifPresent(triples -> {
            persistenceService.persistTriples(triples.stream().filter(kgTriple -> !kgTriple.isQualifier()).toList());
        });
    }

    private void processMetadata(Optional<WikidataEnglishInfoDTO> metadata) {
        metadata.ifPresent(info -> {
            persistenceService.persistSubject(info.getTitle(), info.getEnLabel(), info.getEnDescription());
        });
    }
}
