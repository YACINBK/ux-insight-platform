package com.example.ux_beta;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.domain.Pageable;
import java.util.List;

public interface QuestionRepository extends JpaRepository<Question, Long> {
    List<Question> findTop5ByOrderByCreatedAtDesc();

    @Query("""
        SELECT q.id AS id, q.title AS title, q.createdAt AS createdAt, SIZE(q.attachments) AS attachmentCount
        FROM Question q
        ORDER BY q.createdAt DESC
        """)
    List<RecentQuestionProjection> findTop5RecentQuestionsWithAttachmentCount(Pageable pageable);
} 