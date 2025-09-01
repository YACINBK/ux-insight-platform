package com.uxinsight;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
@RestController
public class SpringbootGatewayApplication {
    public static void main(String[] args) {
        SpringApplication.run(SpringbootGatewayApplication.class, args);
    }

    @GetMapping("/health")
    public String health() {
        return "{\"status\": \"ok\", \"service\": \"springboot-gateway\"}";
    }
} 