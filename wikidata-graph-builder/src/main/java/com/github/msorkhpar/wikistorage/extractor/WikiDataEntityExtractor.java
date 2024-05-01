package com.github.msorkhpar.wikistorage.extractor;

import com.fasterxml.jackson.databind.DeserializationFeature;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.github.msorkhpar.wikistorage.utils.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.w3c.dom.Document;
import org.w3c.dom.Element;
import org.xml.sax.InputSource;

import javax.xml.parsers.DocumentBuilder;
import javax.xml.parsers.DocumentBuilderFactory;
import java.io.*;
import java.util.Optional;
import java.util.Set;

@Slf4j
@RequiredArgsConstructor
public class WikiDataEntityExtractor {

    private final static String NAMESPACE_MAIN = "0";

    private static String extractJsonString(Element xmlPage) {
        String nsValue = xmlPage.getElementsByTagName("ns").item(0).getTextContent();
        if (!nsValue.equals(NAMESPACE_MAIN)) {
            return null;
        }
        if (xmlPage.getElementsByTagName("text").getLength() < 1) {
            return null;
        }
        return xmlPage.getElementsByTagName("text").item(0).getTextContent();
    }

    public static Element createPage(String xmlData) throws Exception {
        DocumentBuilderFactory factory = DocumentBuilderFactory.newInstance();
        DocumentBuilder builder = factory.newDocumentBuilder();
        Document doc = builder.parse(new InputSource(new StringReader(xmlData)));
        return doc.getDocumentElement();
    }


    public static Optional<WikidataEnglishInfoDTO> extractMetadata(Element xmlPage)
            throws Exception {
        String ns = xmlPage.getElementsByTagName("ns").item(0).getTextContent();
        if(!NAMESPACE_MAIN.equals(ns)){
            return Optional.empty();
        }
        String title = xmlPage.getElementsByTagName("title").item(0).getTextContent();
        String text = extractJsonString(xmlPage);
        if (text != null && !text.trim().isEmpty()) {
            try {
                ObjectMapper objectMapper = new ObjectMapper();
                objectMapper.configure(DeserializationFeature.FAIL_ON_UNKNOWN_PROPERTIES, false);
                AdditionalInfo data = objectMapper.readValue(text, AdditionalInfo.class);
                return Optional.of(new WikidataEnglishInfoDTO(title, data));
            } catch (Exception e) {
                logger.error("An unexpected error happened...", e);
            }
        }
        return Optional.empty();
    }

    public static Optional<Set<KGTriple>> extractTriples(Element xmlPage) throws Exception {
        String nsValue = xmlPage.getElementsByTagName("ns").item(0).getTextContent();
        if (!nsValue.equals(NAMESPACE_MAIN)) {
            return Optional.empty();
        }
        if (xmlPage.getElementsByTagName("text").getLength() < 1) {
            return Optional.empty();
        }

        return Optional.of(
                new SnapshotParser().parseSnapshot(
                        xmlPage.getElementsByTagName("text").item(0).getTextContent()
                )
        );

    }
}
