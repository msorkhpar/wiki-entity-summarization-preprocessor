package com.github.msorkhpar.wikistorage.data;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "wiki_page_to_wiki_data_mappings")
@Getter
@Setter
@NoArgsConstructor
public class WikiMapping {

    @Id
    @Column(name="wikipedia_id")
    private Integer id;

    @Column(name="wikipedia_title")
    private String title;

    @Column(name = "wikidata_id")
    private String wikiId;

}
