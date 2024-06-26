package com.github.msorkhpar.pageextextractor.utils;

import org.apache.commons.compress.compressors.bzip2.BZip2CompressorInputStream;

import java.io.BufferedReader;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Path;

public class BZip2BufferReader {

    public static BufferedReader createBufferedReader(Path dumpFile) throws IOException {
        return new BufferedReader(
                new InputStreamReader(
                        new BZip2CompressorInputStream(
                                new FileInputStream(dumpFile.toFile())),
                        StandardCharsets.UTF_8));
    }
}
