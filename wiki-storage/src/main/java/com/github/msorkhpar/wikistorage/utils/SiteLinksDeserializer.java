package com.github.msorkhpar.wikistorage.utils;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class SiteLinksDeserializer extends JsonDeserializer<Map<String, AdditionalInfo.Site>> {
    @Override
    public Map<String, AdditionalInfo.Site> deserialize(JsonParser jsonParser, DeserializationContext deserializationContext)
            throws IOException, JsonProcessingException {

        JsonNode node = jsonParser.getCodec().readTree(jsonParser);

        if (node.isArray() && node.isEmpty()) {
            return new HashMap<>();
        }

        Map<String, AdditionalInfo.Site> sites = new HashMap<>();
        for (JsonNode entry : node) {
            AdditionalInfo.Site site = new AdditionalInfo.Site();
            String key = entry.get("site").asText();
            site.setSite(key);
            site.setTitle(entry.get("title").asText());
            sites.put(key, site);
        }

        return sites;
    }
}