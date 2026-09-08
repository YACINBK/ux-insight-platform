package com.example.ux_beta.repository;

import com.example.ux_beta.domain.Analysis;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.Optional;

@Repository
public interface AnalysisRepository extends JpaRepository<Analysis, Long> {

    /**
     * Find analysis by analysis ID (UUID)
     */
    Optional<Analysis> findByAnalysisId(String analysisId);
}
