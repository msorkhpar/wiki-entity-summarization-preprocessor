package com.github.msorkhpar.wikistorage.data;


import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity(name = "predicates")
@NoArgsConstructor
@Getter
public class Predicate {

    @Id
    @Column(name = "property_id")
    private String predicateId;

    @Column(name = "property_label")
    private String label;

    private String description;

    private Double quantity;

}
