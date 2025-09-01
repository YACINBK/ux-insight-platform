package com.example.ux_beta;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.http.ResponseEntity;

@Service
public class LLMService {
    private final RestTemplate restTemplate = new RestTemplate();

    @Value("${app.llm.base-url:http://localhost:8000}")
    private String llmBaseUrl;

    public QueryResponse queryLLM(QueryRequest request) {
        String url = llmBaseUrl.endsWith("/") ? llmBaseUrl + "query" : llmBaseUrl + "/query";
        ResponseEntity<QueryResponse> response = restTemplate.postForEntity(
            url, request, QueryResponse.class
        );
        return response.getBody();
    }
}