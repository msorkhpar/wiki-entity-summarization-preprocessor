package com.github.msorkhpar.wikistorage.utils;

import lombok.Data;

@Data
public class WikidataEnglishInfoDTO {
    String title;
    String enLabel;
    String enDescription;
    String enWikiTitle;

    public WikidataEnglishInfoDTO(String title, AdditionalInfo data) {
        this.title = title;
        AdditionalInfo.Info labelInfo = data.getLabels() != null ? data.getLabels().getOrDefault("en", null) : null;
        AdditionalInfo.Info descInfo = data.getLabels() != null ? data.getDescription().getOrDefault("en", null) : null;
        AdditionalInfo.Site wikipediaInfo = data.getSiteLinks() != null ? data.getSiteLinks().getOrDefault("enwiki", null) : null;
        if (labelInfo != null) {
            this.enLabel = labelInfo.getValue();
        }
        if (descInfo != null) {
            this.enDescription = descInfo.getValue();
        }
        if (wikipediaInfo != null) {
            this.enWikiTitle = wikipediaInfo.getTitle();
        }
    }
}