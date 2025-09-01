package com.example.ux_beta.controller;

import com.example.ux_beta.domain.Analysis;
import com.example.ux_beta.domain.Attachment;
import com.example.ux_beta.domain.Question;
import com.example.ux_beta.dto.DashboardStats;
import com.example.ux_beta.dto.RecentQuestionProjection;
import com.example.ux_beta.repository.AnalysisRepository;
import com.example.ux_beta.repository.AttachmentRepository;
import com.example.ux_beta.repository.QuestionRepository;
import org.springframework.http.*;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.client.RestTemplate;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.core.io.Resource;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import com.fasterxml.jackson.databind.ObjectMapper;
import java.util.List;
import java.util.Map;
import java.util.HashMap;
import java.util.ArrayList;

@RestController
@RequestMapping("/api/questions")
@CrossOrigin(origins = "${app.cors.allowed-origins:http://localhost:4200}")
public class QuestionController {
    @Autowired
    private QuestionRepository questionRepository;
    @Autowired
    private AttachmentRepository attachmentRepository;
    @Autowired
    private AnalysisRepository analysisRepository;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @GetMapping("/dashboard/stats")
    public DashboardStats getDashboardStats() {
        DashboardStats stats = new DashboardStats();
        stats.setTotalQuestions(questionRepository.count());
        stats.setTotalAttachments(attachmentRepository.count());

        List<RecentQuestionProjection> recentQuestions = questionRepository.findTop5RecentQuestionsWithAttachmentCount(org.springframework.data.domain.PageRequest.of(0, 5));
        stats.setRecentQuestions(recentQuestions);
        return stats;
    }

    @PostMapping(consumes = {"multipart/form-data"})
    public ResponseEntity<String> submitQuestion(
            @RequestParam("title") String title,
            @RequestParam(value = "attachments", required = false) List<MultipartFile> attachments,
            @RequestParam(value = "visionAnalysis", required = false) String visionAnalysis
    ) {
        System.out.println("--- New question submission received ---");
        System.out.println("Title: " + title);
        if (attachments != null) System.out.println("Attachments count: " + attachments.size());
        if (visionAnalysis != null) System.out.println("Vision analysis included");

        Question question = new Question();
        question.setTitle(title);
        question.setCreatedAt(java.time.Instant.now());
        question = questionRepository.save(question);

        if (attachments != null && !attachments.isEmpty()) {
            for (MultipartFile file : attachments) {
                Attachment attachment = new Attachment();
                attachment.setFilename(file.getOriginalFilename());
                attachment.setFileType(file.getContentType());
                try {
                    attachment.setFileData(file.getBytes());
                } catch (java.io.IOException e) {
                    continue;
                }
                attachment.setQuestion(question);
                attachmentRepository.save(attachment);
            }
        }

        Map<String, Object> llmPayload = new HashMap<>();
        llmPayload.put("question", title);

        if (attachments != null && !attachments.isEmpty()) {
            List<Map<String, Object>> trackedDataList = new ArrayList<>();

            for (MultipartFile file : attachments) {
                if (file.getContentType() != null && file.getContentType().equals("application/json")) {
                    try {
                        String jsonContent = new String(file.getBytes(), "UTF-8");

                        if (jsonContent.trim().startsWith("[")) {
                            List<Map<String, Object>> jsonArray = objectMapper.readValue(jsonContent, List.class);
                            trackedDataList.addAll(jsonArray);
                        } else {
                            Map<String, Object> jsonObject = objectMapper.readValue(jsonContent, Map.class);
                            trackedDataList.add(jsonObject);
                        }

                        System.out.println("Added JSON file: " + file.getOriginalFilename() + " with " + trackedDataList.size() + " data points");
                    } catch (Exception e) {
                        System.err.println("Error reading JSON file " + file.getOriginalFilename() + ": " + e.getMessage());
                    }
                }
            }

            if (!trackedDataList.isEmpty()) {
                llmPayload.put("tracked_data", trackedDataList);
                System.out.println("Total tracked data points: " + trackedDataList.size());
            }
        }

        if (visionAnalysis != null && !visionAnalysis.isEmpty()) {
            try {
                List<Map<String, Object>> visionResults = objectMapper.readValue(visionAnalysis, List.class);
                llmPayload.put("vision", visionResults);
                System.out.println("Vision analysis added to LLM payload: " + visionResults.size() + " images processed");
            } catch (Exception e) {
                System.err.println("Error parsing vision analysis: " + e.getMessage());
            }
        }

        try {
            RestTemplate restTemplate = new RestTemplate();
            String llmApiBase = System.getenv().getOrDefault("APP_LLM_BASE_URL", "http://localhost:8000");
            if (!llmApiBase.endsWith("/")) llmApiBase += "/";
            String llmApiUrl = llmApiBase + "query";
            System.out.println("Calling LLM API with payload...");
            ResponseEntity<String> llmResponse = restTemplate.postForEntity(llmApiUrl, llmPayload, String.class);
            System.out.println("LLM API response: " + llmResponse.getStatusCode());
            return ResponseEntity.ok(llmResponse.getBody());
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.ok("Question saved, but LLM call failed");
        }
    }

    @PostMapping(value = "/test-upload", consumes = {"multipart/form-data"})
    public ResponseEntity<String> testUpload(
        @RequestParam("title") String title,
        @RequestParam(value = "attachments", required = false) List<MultipartFile> attachments
    ) {
        System.out.println("--- TEST UPLOAD ---");
        System.out.println("Title: " + title);
        if (attachments != null) {
            System.out.println("Attachments count: " + attachments.size());
            for (MultipartFile file : attachments) {
                System.out.println("Received: " + file.getOriginalFilename() + " (" + file.getContentType() + ")");
            }
        } else {
            System.out.println("No attachments received.");
        }
        return ResponseEntity.ok("OK");
    }

    @PostMapping(value = "/vision/analyze", consumes = {"multipart/form-data"})
    public ResponseEntity<Map<String, Object>> analyzeVision(
        @RequestParam(value = "attachments", required = false) List<MultipartFile> attachments
    ) {
        System.out.println("--- Vision analysis request received ---");
        if (attachments != null) System.out.println("Attachments count: " + attachments.size());
        MultipartFile imageFile = null;
        if (attachments != null && !attachments.isEmpty()) {
            for (MultipartFile file : attachments) {
                if (imageFile == null && file.getContentType() != null && file.getContentType().startsWith("image/")) {
                    imageFile = file;
                }
            }
        }
        if (imageFile == null) {
            return ResponseEntity.badRequest().body(Map.of("error", "No image file provided"));
        }
        try {
            RestTemplate restTemplate = new RestTemplate();
            String visionApiBase = System.getenv().getOrDefault("APP_VISION_BASE_URL", "http://localhost:8001");
            HttpHeaders headers = new HttpHeaders();
            headers.setContentType(MediaType.MULTIPART_FORM_DATA);
            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            final MultipartFile imageFileFinal = imageFile;
            Resource imageResource = new ByteArrayResource(imageFileFinal.getBytes()) {
                @Override
                public String getFilename() {
                    return imageFileFinal.getOriginalFilename();
                }
            };
            body.add("file", imageResource);
            HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);
            Map<String, Object> classification = null;
            try {
                ResponseEntity<Map> classifyResp = restTemplate.postForEntity(visionApiBase + "/classify_screen", requestEntity, Map.class);
                if (classifyResp.getStatusCode().is2xxSuccessful()) {
                    classification = classifyResp.getBody();
                }
            } catch (Exception e) {
                System.err.println("Vision API /classify_screen failed: " + e.getMessage());
            }
            Map<String, Object> detections = null;
            try {
                ResponseEntity<Map> analyzeResp = restTemplate.postForEntity(visionApiBase + "/analyze", requestEntity, Map.class);
                if (analyzeResp.getStatusCode().is2xxSuccessful()) {
                    detections = analyzeResp.getBody();
                }
            } catch (Exception e) {
                System.err.println("Vision API /analyze failed: " + e.getMessage());
            }
            Map<String, Object> visionResult = new HashMap<>();
            if (classification != null) visionResult.put("classification", classification);
            if (detections != null) visionResult.put("detections", detections);
            return ResponseEntity.ok(visionResult);
        } catch (Exception e) {
            e.printStackTrace();
            return ResponseEntity.status(500).body(Map.of("error", e.getMessage()));
        }
    }

    @PostMapping("/premium-auto/analyze")
    public ResponseEntity<Map<String, Object>> premiumAutoAnalysis(@RequestBody Map<String, String> request) {
        System.out.println("--- Premium Auto Analysis request received ---");
        String url = request.get("url");
        System.out.println("URL: " + url);

        if (url == null || url.trim().isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "URL is required"));
        }

        String analysisId = java.util.UUID.randomUUID().toString();

        try {
            if (!url.startsWith("http://") && !url.startsWith("https://")) {
                url = "https://" + url;
            }

            Analysis analysis = new Analysis(analysisId, url);
            analysis.markInProgress();
            analysis = analysisRepository.save(analysis);

            Map<String, Object> demoResponse = new HashMap<>();
            demoResponse.put("status", "success");
            demoResponse.put("message", "Demo analysis completed");
            demoResponse.put("url", url);
            demoResponse.put("analysis_type", "demo");
            demoResponse.put("analysis_id", analysisId);

            Map<String, Object> results = new HashMap<>();
            results.put("user_engagement_score", 78);
            results.put("navigation_efficiency", 85);
            results.put("conversion_optimization", 72);
            results.put("mobile_responsiveness", 91);
            results.put("load_time_optimization", 88);

            List<String> recommendations = List.of(
                "Consider adding more prominent call-to-action buttons",
                "Optimize images for faster loading times",
                "Improve mobile navigation menu accessibility",
                "Add breadcrumb navigation for better user orientation",
                "Consider implementing a search functionality"
            );

            results.put("recommendations", recommendations);
            demoResponse.put("results", results);

            try {
                String resultsJson = objectMapper.writeValueAsString(demoResponse);
                System.out.println("💾 Analysis results would be saved to file storage (service removed)");
            } catch (Exception e) {
                System.err.println("⚠️ Warning: Could not save results to file: " + e.getMessage());
            }

            analysis.setResultsJson(objectMapper.writeValueAsString(demoResponse));
            analysis.markCompleted();
            analysisRepository.save(analysis);

            Question question = new Question();
            question.setTitle("Premium Auto Analysis: " + url);
            question.setCreatedAt(java.time.Instant.now());
            question = questionRepository.save(question);

            System.out.println("✅ Demo analysis completed for URL: " + url);
            return ResponseEntity.ok(demoResponse);

        } catch (Exception e) {
            System.err.println("❌ Error in premium auto analysis: " + e.getMessage());
            e.printStackTrace();

            try {
                Analysis analysis = analysisRepository.findByAnalysisId(analysisId).orElse(null);
                if (analysis != null) {
                    analysis.markFailed(e.getMessage());
                    analysisRepository.save(analysis);
                }
            } catch (Exception dbError) {
                System.err.println("⚠️ Could not update analysis status: " + dbError.getMessage());
            }

            return ResponseEntity.status(500).body(Map.of(
                "error", "Sorry for the inconvenience. This error is out of handling and will be resolved shortly.",
                "details", e.getMessage()
            ));
        }
    }
} 