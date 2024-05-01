CREATE TABLE "subjects"
(
    name         VARCHAR(255) NOT NULL,
    label       VARCHAR(255),
    description TEXT
);
CREATE INDEX idx_subjects_pk ON subjects (name);