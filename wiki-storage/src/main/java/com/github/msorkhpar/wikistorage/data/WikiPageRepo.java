package com.github.msorkhpar.wikistorage.data;

import org.springframework.data.repository.CrudRepository;

public interface WikiPageRepo extends CrudRepository<WikipediaPage, Long> {
}
