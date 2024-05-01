package com.github.msorkhpar.wikistorage.utils;

import com.fasterxml.jackson.annotation.JsonProperty;
import com.fasterxml.jackson.databind.annotation.JsonDeserialize;
import lombok.Data;

import java.util.Map;

@Data
public class AdditionalInfo {
    @JsonProperty("labels")
    @JsonDeserialize(using = LabelDescDeserializer.class)
    private Map<String, Info> labels;

    @JsonProperty("descriptions")
    @JsonDeserialize(using = LabelDescDeserializer.class)
    private Map<String, Info> description;

    @JsonProperty("sitelinks")
    @JsonDeserialize(using = SiteLinksDeserializer.class)
    private Map<String, Site> siteLinks;


    @Data
    public static class Info {
        @JsonProperty("language")
        private String language;

        @JsonProperty("value")
        private String value;
    }

    @Data
    public static class Site {
        @JsonProperty("site")
        private String site;

        @JsonProperty("title")
        private String title;
    }
}