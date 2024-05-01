package com.github.msorkhpar.wikistorage.utils;

import com.fasterxml.jackson.core.JsonFactory;
import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonToken;
import lombok.extern.slf4j.Slf4j;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

// A modified version of https://github.com/klimzaporojets/ES-benchmark/blob/main/wikidata_reader/src/main/java/wikidata/misc/SnapshotParser.java
@Slf4j
public class SnapshotParser {

    public void addTripleStr(String subjectQid, String propertyId, String objectQid, Set<KGTriple> readTriples,
                             boolean isQualifier) {
        assert objectQid.startsWith("Q");
        assert propertyId.startsWith("P");
        assert subjectQid.startsWith("Q");
        KGTriple kgTriple = new KGTriple(subjectQid, propertyId, objectQid, isQualifier);
        readTriples.add(kgTriple);
    }


    public Set<KGTriple> parseSnapshot(String text) throws IOException {
        Set<KGTriple> triples = new HashSet<>();
        JsonParser jParser = new JsonFactory().createParser(text);
        int depth = 0;
        JsonToken nextToken = jParser.nextToken();
        boolean insideClaims = false;
        boolean insideMainSnak = false;
        boolean insideDataValue = false;
        boolean insideValue = false;
        boolean insideQualifiers = false;

        boolean insideQualifierDataValue = false;
        boolean insideQualifierValue = false;

        String propertyId = "";
        String subjectQid = "";
        String propertyQualifierId = "";
        String currQualifierEntityType = "";
        String currEntityType = "";
        boolean doAdd = true;
        Set<KGTriple> readCurrTriples = new HashSet<>();
        while (nextToken != null && doAdd) {
            if (nextToken == JsonToken.START_OBJECT) {
                depth += 1;
            }
            if (nextToken == JsonToken.START_ARRAY) {
                depth += 1;
            }
            if (depth == 1 && "claims".equals(jParser.getCurrentName()) && nextToken == JsonToken.FIELD_NAME) {
                insideClaims = true;
            }
            if (depth == 4 && insideClaims && nextToken == JsonToken.FIELD_NAME) {
                if ("mainsnak".equals(jParser.getCurrentName())) {
                    insideMainSnak = true;
                }
                if ("qualifiers".equals(jParser.getCurrentName())) {
                    insideQualifiers = true;
                }
            }
            if (depth == 5 && insideMainSnak && nextToken == JsonToken.FIELD_NAME) {
                if ("datavalue".equals(jParser.getCurrentName())) {
                    insideDataValue = true;
                }
            }
            if (depth == 6 && insideDataValue && nextToken == JsonToken.FIELD_NAME) {
                if ("value".equals(jParser.getCurrentName())) {
                    insideValue = true;
                    currEntityType = "";
                }
            }
            if (depth == 7 && insideQualifiers && nextToken == JsonToken.FIELD_NAME) {
                if ("datavalue".equals(jParser.getCurrentName())) {
                    insideQualifierDataValue = true;
                }
            }
            if (depth == 8 && insideQualifierDataValue && nextToken == JsonToken.FIELD_NAME) {
                if ("value".equals(jParser.getCurrentName())) {
                    insideQualifierValue = true;
                    currQualifierEntityType = "";
                }
            }
            if (depth == 1 && nextToken == JsonToken.VALUE_STRING) {
                if ("id".equals(jParser.getCurrentName())) {
                    subjectQid = jParser.getValueAsString();
                }
            }
            if (depth == 2 && insideClaims && nextToken == JsonToken.FIELD_NAME) {
                propertyId = jParser.getCurrentName();
            }
            if (depth == 5 && insideQualifiers && nextToken == JsonToken.FIELD_NAME) {
                propertyQualifierId = jParser.getCurrentName();
            }
            if (depth == 9 && insideQualifierValue && nextToken == JsonToken.VALUE_STRING) {
                if ("entity-type".equals(jParser.getCurrentName())) {
                    currQualifierEntityType = jParser.getValueAsString();
                }
                if ("id".equals(jParser.getCurrentName())) {
                    if (currQualifierEntityType.equals("item")) {
                        String objectQualifierQid = jParser.getValueAsString();
                        addTripleStr(subjectQid, propertyQualifierId, objectQualifierQid, readCurrTriples, true);
                    }
                }
            }
            if (depth == 7 && insideValue && nextToken == JsonToken.VALUE_STRING) {
                if ("entity-type".equals(jParser.getCurrentName())) {
                    currEntityType = jParser.getValueAsString();
                }
                if ("id".equals(jParser.getCurrentName())) {
                    if (currEntityType.equals("item")) {
                        String objectQid = jParser.getValueAsString();
//                        if objectQid object == 13442814 or object == 7318358
                        if (objectQid.equals("Q13442814") || objectQid.equals("Q7318358")) {
                            doAdd = false;
                        }
                        addTripleStr(subjectQid, propertyId, objectQid, readCurrTriples, false);
                    }
                }
            }
            nextToken = jParser.nextToken();
            if (nextToken == JsonToken.END_OBJECT || nextToken == JsonToken.END_ARRAY) {
                depth -= 1;
                if (depth == 1 && insideClaims) {
                    insideClaims = false;
                }
                if (depth == 4 && insideMainSnak) {
                    insideMainSnak = false;
                }
                if (depth == 4 && insideQualifiers) {
                    insideQualifiers = false;
                }
                if (depth == 5 && insideDataValue) {
                    insideDataValue = false;
                }
                if (depth == 6 && insideValue) {
                    insideValue = false;
                }
                if (depth == 7 && insideQualifierDataValue) {
                    insideQualifierDataValue = false;
                }
                if (depth == 8 && insideQualifierValue) {
                    insideQualifierValue = false;
                }
            }
            if (nextToken == null && depth > 0) {
                logger.error("Something weird is going on with this json: {} ", text);
            }
        }
        if (doAdd) {
            // union
            triples.addAll(readCurrTriples);
        }
        jParser.close();
        return triples;
    }

}