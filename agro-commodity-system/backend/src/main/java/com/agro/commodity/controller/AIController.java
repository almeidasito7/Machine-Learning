package com.agro.commodity.controller;

import com.agro.commodity.dto.AIAnalysisRequest;
import com.agro.commodity.dto.AIAnalysisResponse;
import com.agro.commodity.service.AIAnalysisService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/ai")
@RequiredArgsConstructor
@Tag(name = "AI Analysis", description = "Análise com IA via LangChain4j + LangGraph")
@CrossOrigin(origins = {"http://localhost:4200", "http://localhost:3000"})
public class AIController {

    private final AIAnalysisService aiAnalysisService;

    @PostMapping("/analyze")
    @Operation(summary = "Análise completa de mercado via LangGraph workflow")
    public ResponseEntity<AIAnalysisResponse> analyze(@RequestBody AIAnalysisRequest request) {
        return ResponseEntity.ok(aiAnalysisService.analyze(request));
    }

    @PostMapping("/chat")
    @Operation(summary = "Chat com assistente especialista em agronegócio")
    public ResponseEntity<AIAnalysisResponse> chat(@RequestBody AIAnalysisRequest request) {
        request.setAnalysisType("CHAT");
        return ResponseEntity.ok(aiAnalysisService.analyze(request));
    }

    @PostMapping("/market-analysis")
    @Operation(summary = "Análise de mercado para commodity específica ou geral")
    public ResponseEntity<AIAnalysisResponse> marketAnalysis(@RequestBody AIAnalysisRequest request) {
        request.setAnalysisType("MARKET_ANALYSIS");
        return ResponseEntity.ok(aiAnalysisService.analyze(request));
    }

    @PostMapping("/recommendation")
    @Operation(summary = "Recomendação de compra/venda baseada em IA")
    public ResponseEntity<AIAnalysisResponse> recommendation(@RequestBody AIAnalysisRequest request) {
        request.setAnalysisType("RECOMMENDATION");
        return ResponseEntity.ok(aiAnalysisService.analyze(request));
    }
}
