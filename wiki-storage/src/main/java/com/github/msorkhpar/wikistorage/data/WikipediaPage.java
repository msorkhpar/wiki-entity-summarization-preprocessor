package com.github.msorkhpar.wikistorage.data;


import io.hypersistence.utils.hibernate.type.array.ListArrayType;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;
import org.hibernate.annotations.Type;

@Entity(name = "wikipedia_pages")
@Getter
@NoArgsConstructor
@AllArgsConstructor
public class WikipediaPage {

    @Id
    @Column(name = "id")
    private Long id;

    @Column(name = "title", columnDefinition = "varchar(255)")
    private String title;

    @Column(name = "content", columnDefinition = "text")
    private String content;

    @Column(name = "content_length")
    private Integer contentLength;
}
