package com.github.msorkhpar.pageextextractor.service;

import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;


@Service
@Slf4j
@RequiredArgsConstructor
public class WikipediaService {

    private final WikidataDumpFileService wikidataDumpFileService;


    @SneakyThrows
    public void extractWikipediaPages(List<Path> dumpFiles) {
        ArrayList<CompletableFuture<Path>> results = new ArrayList<>();
        for (Path dumpFile : dumpFiles) {
            results.add(wikidataDumpFileService.process(dumpFile));
        }
        CompletableFuture.allOf(results.toArray(new CompletableFuture[0])).join();
    }

}
