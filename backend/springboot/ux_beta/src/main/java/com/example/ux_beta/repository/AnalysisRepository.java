package com.example.ux_beta;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;
import java.util.List;
import java.util.Optional;

@Repository
public interface AnalysisRepository extends JpaRepository<Analysis, Long> {
    
    /**
     * Find analysis by analysis ID (UUID)
     */
    Optional<Analysis> findByAnalysisId(String analysisId);
    
    /**
     * Find all analyses by status
     */
    List<Analysis> findByStatus(String status);
    
    /**
     * Find all completed analyses
     */
    List<Analysis> findByStatusOrderByCreatedAtDesc(String status);
    
    /**
     * Find analyses by URL
     */
    List<Analysis> findByUrlContainingIgnoreCaseOrderByCreatedAtDesc(String url);
    
    /**
     * Find analyses by type (DEMO, REAL)
     */
    List<Analysis> findByAnalysisTypeOrderByCreatedAtDesc(String analysisType);
    
    /**
     * Find recent analyses (last 10)
     */
    @Query("SELECT a FROM Analysis a ORDER BY a.createdAt DESC")
    List<Analysis> findRecentAnalyses();
    
    /**
     * Find analyses created after a specific date
     */
    @Query("SELECT a FROM Analysis a WHERE a.createdAt >= :since ORDER BY a.createdAt DESC")
    List<Analysis> findAnalysesSince(@Param("since") java.time.Instant since);
    
    /**
     * Count analyses by status
     */
    long countByStatus(String status);
    
    /**
     * Count analyses by type
     */
    long countByAnalysisType(String analysisType);
    
    /**
     * Find failed analyses
     */
    List<Analysis> findByStatusAndErrorMessageIsNotNullOrderByCreatedAtDesc(String status);
    
    /**
     * Find analyses that took longer than specified duration
     */
    @Query("SELECT a FROM Analysis a WHERE a.completedAt IS NOT NULL AND (a.completedAt - a.createdAt) > :duration")
    List<Analysis> findSlowAnalyses(@Param("duration") java.time.Duration duration);
    
    /**
     * Get analysis statistics
     */
    @Query("SELECT " +
           "COUNT(a) as total, " +
           "COUNT(CASE WHEN a.status = 'COMPLETED' THEN 1 END) as completed, " +
           "COUNT(CASE WHEN a.status = 'FAILED' THEN 1 END) as failed, " +
           "COUNT(CASE WHEN a.status = 'IN_PROGRESS' THEN 1 END) as inProgress " +
           "FROM Analysis a")
    Object[] getAnalysisStats();
} 