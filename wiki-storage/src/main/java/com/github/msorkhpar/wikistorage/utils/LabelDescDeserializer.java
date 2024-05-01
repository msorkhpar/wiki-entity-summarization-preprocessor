package com.github.msorkhpar.wikistorage.utils;

import com.fasterxml.jackson.core.JsonParser;
import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.DeserializationContext;
import com.fasterxml.jackson.databind.JsonDeserializer;
import com.fasterxml.jackson.databind.JsonNode;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

public class LabelDescDeserializer extends JsonDeserializer<Map<String, AdditionalInfo.Info>> {
    @Override
    public Map<String, AdditionalInfo.Info> deserialize(JsonParser jsonParser, DeserializationContext deserializationContext)
            throws IOException, JsonProcessingException {

        JsonNode node = jsonParser.getCodec().readTree(jsonParser);

        if (node.isArray() && node.isEmpty()) {
            return new HashMap<>();
        }

        Map<String, AdditionalInfo.Info> descriptions = new HashMap<>();
        for (JsonNode entry : node) {
            String key = entry.get("language").asText();
            AdditionalInfo.Info value = new AdditionalInfo.Info();
            value.setLanguage(key);
            value.setValue(entry.get("value").asText());
            descriptions.put(key, value);
        }

        return descriptions;
    }
}