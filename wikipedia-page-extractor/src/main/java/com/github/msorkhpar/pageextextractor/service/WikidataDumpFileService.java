package com.github.msorkhpar.pageextextractor.service;

import com.github.msorkhpar.pageextextractor.utils.WikiPage;
import com.github.msorkhpar.wikistorage.data.PersistenceService;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import org.w3c.dom.Element;

import java.io.BufferedReader;
import java.io.IOException;
import java.nio.file.Path;
import java.util.concurrent.CompletableFuture;

import static com.github.msorkhpar.pageextextractor.extractor.WikipediaPageExtractor.*;
import static com.github.msorkhpar.pageextextractor.utils.BZip2BufferReader.createBufferedReader;

@Service
@Slf4j
@RequiredArgsConstructor
class WikidataDumpFileService {

    private final PersistenceService persistenceService;

    @SneakyThrows
    @Async
    public CompletableFuture<Path> process(Path dumpFile) {
        String fileName = dumpFile.getFileName().toString();
        long start = System.currentTimeMillis();
        long counter = 1;
        logger.info("Start processing [{}]", fileName);
        try (BufferedReader reader = createBufferedReader(dumpFile)) {
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
                        WikiPage page = extractTextString(xmlPage);
                        if (page != null) {
                            persistenceService.persistWikiPage(page.id(), page.title(), page.text());
                            if (counter++ % 10_000 == 0) {
                                logger.info("[{}] pages of [{}] is processed", counter, fileName);
                            }
                        }
                    } catch (Exception e) {
                        logger.info("Extraction from the following text was not successful, {}", pageString);
                    }
                    // prepare the builder for the next page
                    xmlBuilder.setLength(0);
                }
            }
        } catch (IOException e) {
            logger.error("Error processing [{}]", fileName, e);
            return CompletableFuture.failedFuture(e);
        }
        logger.info("Finish processing [{}] in [{}ms], Counter is [{}]", fileName, System.currentTimeMillis() - start, counter);
        return CompletableFuture.completedFuture(dumpFile);
    }

}
