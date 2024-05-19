package com.github.msorkhpar.wikistorage.utils;

import lombok.Data;

@Data
public class WikidataEnglishInfoDTO {
    String title;
    String label;
    String description;
    String enWikiTitle;

    public WikidataEnglishInfoDTO(String title, AdditionalInfo data) {
        this.title = title;
        AdditionalInfo.Info labelInfo = data.getLabels() != null ? data.getLabels().getOrDefault("en", null) : null;
        AdditionalInfo.Info descInfo = data.getLabels() != null ? data.getDescription().getOrDefault("en", null) : null;
        AdditionalInfo.Site wikipediaInfo = data.getSiteLinks() != null ? data.getSiteLinks().getOrDefault("enwiki", null) : null;
        if (labelInfo != null) {
            this.label = labelInfo.getValue();
        }
        if (descInfo != null) {
            this.description = descInfo.getValue();
        }
        if (wikipediaInfo != null) {
            this.enWikiTitle = wikipediaInfo.getTitle();
        }
        String key = "";
        if (this.label == null && data.getLabels().size() > 0) {
            key = data.getLabels().keySet().iterator().next();
            this.label = data.getLabels().get(key).getValue();
            this.description = data.getDescription().getOrDefault(key,null).getValue();
        }

        if (this.description == null && data.getDescription().size() > 0) {
            this.description = data.getDescription().values().iterator().next().getValue();
        }
    }
}