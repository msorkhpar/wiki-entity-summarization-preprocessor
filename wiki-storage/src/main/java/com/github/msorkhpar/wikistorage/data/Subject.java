package com.github.msorkhpar.wikistorage.data;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

@Entity
@Table(name = "subjects")
@Getter
@Setter
@NoArgsConstructor
public class Subject {
    public Subject(String name, String label, String description) {
        this.name = name;
        setLabel(label);
        this.description = description;
    }

    @Id
    @Column(nullable = false)
    private String name;

    @Column(columnDefinition = "varchar(255)")
    private String label;

    public void setLabel(String label) {
        if (label == null) {
            return;
        }
        if (label.length() > 255) {
            label = label.substring(0, 255);
        }
        this.label = label;
    }

    @Column(columnDefinition = "text")
    private String description;

}
