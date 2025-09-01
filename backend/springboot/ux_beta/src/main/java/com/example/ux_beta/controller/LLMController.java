package com.example.ux_beta.controller;

import com.example.ux_beta.dto.QueryRequest;
import com.example.ux_beta.dto.QueryResponse;
import com.example.ux_beta.domain.Question;
import com.example.ux_beta.repository.QuestionRepository;
import com.example.ux_beta.service.LLMService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;
import java.time.Instant;

@RestController
@RequestMapping("/api/llm")
public class LLMController {
    @Autowired
    private LLMService llmService;
    @Autowired
    private QuestionRepository questionRepository;

    @PostMapping("/query")
    public QueryResponse queryLLM(@RequestBody QueryRequest request) {
        Question q = new Question();
        q.setTitle(request.getQuestion());
        q.setCreatedAt(Instant.now());
        q = questionRepository.save(q);

        QueryResponse llmResponse = llmService.queryLLM(request);

        q.setResponse(llmResponse.getAnswer());
        questionRepository.save(q);

        return llmResponse;
    }
} 