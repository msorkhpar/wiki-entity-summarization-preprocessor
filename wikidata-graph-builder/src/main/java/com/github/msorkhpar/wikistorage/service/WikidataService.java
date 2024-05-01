package com.github.msorkhpar.wikistorage.service;

import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;


@Service
@Slf4j
@RequiredArgsConstructor
public class WikidataService {

    @Value("${app.dump-files.multi-stream}")
    private boolean multiStream;
    private final WikidataDumpFileService tripleExtractorService;


    @SneakyThrows
    public void constructWikidataTree(List<Path> dumpFiles) {
        ArrayList<CompletableFuture<Path>> results = new ArrayList<>();
        for (Path dumpFile : dumpFiles) {
            results.add(tripleExtractorService.process(dumpFile, multiStream));
        }
        CompletableFuture.allOf(results.toArray(new CompletableFuture[0])).join();
    }

}
