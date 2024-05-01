package com.github.msorkhpar.wikistorage.utils;

import lombok.Data;

import java.util.Objects;

@Data
public class KGTriple {

    private String subjectQid;
    private String propertyId;
    private String objectQid;
    private boolean isQualifier;

    public KGTriple(String subjectQid, String propertyId, String objectQid,
                    boolean isQualifier) {
        this.subjectQid = subjectQid;
        this.propertyId = propertyId;
        this.objectQid = objectQid;
        this.isQualifier = isQualifier;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        KGTriple kgTriple = (KGTriple) o;
        return this.subjectQid.equals(kgTriple.subjectQid) &&
                this.propertyId.equals(kgTriple.propertyId) &&
                this.objectQid.equals(kgTriple.objectQid) &&
                this.isQualifier == kgTriple.isQualifier;
    }

    @Override
    public String toString() {
        return this.subjectQid + "-> " + this.propertyId + "-> " + this.objectQid + (this.isQualifier ? " (IS Qualifier)" : "");
    }

    @Override
    public int hashCode() {
        return Objects.hash(subjectQid, propertyId, objectQid, isQualifier);
    }
}