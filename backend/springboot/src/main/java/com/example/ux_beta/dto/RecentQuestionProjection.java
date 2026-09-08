package com.example.ux_beta.dto;

import java.time.Instant;

public interface RecentQuestionProjection {
    Long getId();
    String getTitle();
    Instant getCreatedAt();
    int getAttachmentCount();
} 