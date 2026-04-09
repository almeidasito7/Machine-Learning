package com.agro.commodity.ai;

import com.agro.commodity.dto.AIAnalysisResponse;
import com.agro.commodity.dto.WorkflowStep;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Component;

import java.time.LocalDateTime;
import java.util.*;

/**
 * LangGraph-inspired stateful workflow for commodity AI analysis.
 *
 * Implements a directed graph of analysis nodes:
 *
 *   [START]
 *      |
 *   [dataCollectionNode]  → collect commodity context
 *      |
 *   [marketAnalysisNode]  → analyze market conditions
 *      |
 *   [riskAssessmentNode]  → assess risks
 *      |
 *   [recommendationNode]  → generate final recommendation
 *      |
 *   [END]
 *
 * Each node receives the shared GraphState and can modify it.
 */
@Component
@RequiredArgsConstructor
@Slf4j
public class LangGraphWorkflow {

    private final CommodityAIAssistant aiAssistant;

    // ─── Graph State ───────────────────────────────────────────────────────────

    public static class GraphState {
        public String userQuestion;
        public String commodityContext;
        public String marketAnalysis;
        public String riskAssessment;
        public String finalRecommendation;
        public String sentiment;
        public double confidenceScore;
        public List<WorkflowStep> steps = new ArrayList<>();
        public Map<String, String> metadata = new LinkedHashMap<>();
    }

    // ─── Public Entry Point ────────────────────────────────────────────────────

    public AIAnalysisResponse runAnalysisWorkflow(String question, String commodityContext) {
        log.info("Starting LangGraph analysis workflow for question: {}", question);

        GraphState state = new GraphState();
        state.userQuestion = question;
        state.commodityContext = commodityContext;

        // Execute the graph nodes in sequence
        state = dataCollectionNode(state);
        state = marketAnalysisNode(state);
        state = riskAssessmentNode(state);
        state = recommendationNode(state);

        return buildResponse(state);
    }

    public AIAnalysisResponse runChatWorkflow(String userMessage, String context) {
        log.info("Running chat workflow");

        GraphState state = new GraphState();
        state.userQuestion = userMessage;
        state.commodityContext = context;

        state = chatNode(state);

        return buildResponse(state);
    }

    // ─── Graph Nodes ──────────────────────────────────────────────────────────

    /**
     * Node 1: Data Collection — enriches state with structured context
     */
    private GraphState dataCollectionNode(GraphState state) {
        log.debug("Executing dataCollectionNode");
        WorkflowStep step = WorkflowStep.builder()
                .stepName("data_collection")
                .description("Coleta e estruturação dos dados de mercado")
                .build();
        try {
            // Enrich context with metadata
            state.metadata.put("question_type", classifyQuestion(state.userQuestion));
            state.metadata.put("timestamp", LocalDateTime.now().toString());

            step.setStatus("COMPLETED");
            step.setOutput("Contexto de " + countWords(state.commodityContext) + " palavras processado");
        } catch (Exception e) {
            log.error("dataCollectionNode error: {}", e.getMessage());
            step.setStatus("ERROR");
            step.setOutput("Erro na coleta: " + e.getMessage());
        }
        state.steps.add(step);
        return state;
    }

    /**
     * Node 2: Market Analysis — calls LLM for market conditions
     */
    private GraphState marketAnalysisNode(GraphState state) {
        log.debug("Executing marketAnalysisNode");
        WorkflowStep step = WorkflowStep.builder()
                .stepName("market_analysis")
                .description("Análise das condições de mercado via LLM")
                .build();
        try {
            String prompt = buildMarketAnalysisPrompt(state);
            state.marketAnalysis = aiAssistant.analyzeMarket(prompt);

            step.setStatus("COMPLETED");
            step.setOutput("Análise de mercado gerada com sucesso");
        } catch (Exception e) {
            log.error("marketAnalysisNode error: {}", e.getMessage());
            state.marketAnalysis = "Análise de mercado indisponível no momento.";
            step.setStatus("ERROR");
            step.setOutput("Erro: " + e.getMessage());
        }
        state.steps.add(step);
        return state;
    }

    /**
     * Node 3: Risk Assessment — evaluates risks based on context
     */
    private GraphState riskAssessmentNode(GraphState state) {
        log.debug("Executing riskAssessmentNode");
        WorkflowStep step = WorkflowStep.builder()
                .stepName("risk_assessment")
                .description("Avaliação de riscos de mercado")
                .build();
        try {
            String prompt = "Dados: " + state.commodityContext + "\n\nAnálise prévia: " + state.marketAnalysis;
            state.riskAssessment = aiAssistant.assessRisk(prompt);

            step.setStatus("COMPLETED");
            step.setOutput("Avaliação de riscos concluída");
        } catch (Exception e) {
            log.error("riskAssessmentNode error: {}", e.getMessage());
            state.riskAssessment = "Avaliação de riscos não disponível.";
            step.setStatus("ERROR");
            step.setOutput("Erro: " + e.getMessage());
        }
        state.steps.add(step);
        return state;
    }

    /**
     * Node 4: Recommendation — synthesizes insights into final answer
     */
    private GraphState recommendationNode(GraphState state) {
        log.debug("Executing recommendationNode");
        WorkflowStep step = WorkflowStep.builder()
                .stepName("recommendation")
                .description("Síntese e geração de recomendação final")
                .build();
        try {
            String synthesisPrompt = buildSynthesisPrompt(state);
            state.finalRecommendation = aiAssistant.chat(synthesisPrompt);

            state.sentiment = extractSentiment(state.finalRecommendation);
            state.confidenceScore = estimateConfidence(state);

            step.setStatus("COMPLETED");
            step.setOutput("Recomendação gerada | Sentimento: " + state.sentiment
                    + " | Confiança: " + String.format("%.0f%%", state.confidenceScore * 100));
        } catch (Exception e) {
            log.error("recommendationNode error: {}", e.getMessage());
            state.finalRecommendation = "Não foi possível gerar uma recomendação no momento.";
            step.setStatus("ERROR");
            step.setOutput("Erro: " + e.getMessage());
        }
        state.steps.add(step);
        return state;
    }

    /**
     * Node for simple chat (single-step workflow)
     */
    private GraphState chatNode(GraphState state) {
        WorkflowStep step = WorkflowStep.builder()
                .stepName("chat")
                .description("Resposta conversacional do assistente agrícola")
                .build();
        try {
            String prompt = state.commodityContext.isBlank()
                    ? state.userQuestion
                    : "Contexto de mercado:\n" + state.commodityContext + "\n\nPergunta: " + state.userQuestion;

            state.finalRecommendation = aiAssistant.chat(prompt);
            state.sentiment = "NEUTRAL";
            state.confidenceScore = 0.8;
            step.setStatus("COMPLETED");
            step.setOutput("Resposta gerada");
        } catch (Exception e) {
            log.error("chatNode error: {}", e.getMessage());
            state.finalRecommendation = "Desculpe, não consigo responder no momento. Tente novamente.";
            step.setStatus("ERROR");
        }
        state.steps.add(step);
        return state;
    }

    // ─── Helpers ──────────────────────────────────────────────────────────────

    private String buildMarketAnalysisPrompt(GraphState state) {
        return String.format("""
                Pergunta do usuário: %s

                Dados de mercado disponíveis:
                %s

                Metadados: %s

                Por favor, realize uma análise completa do mercado.
                """, state.userQuestion, state.commodityContext, state.metadata);
    }

    private String buildSynthesisPrompt(GraphState state) {
        return String.format("""
                Com base nas análises abaixo, responda a pergunta do usuário de forma clara e direta.

                PERGUNTA: %s

                ANÁLISE DE MERCADO:
                %s

                AVALIAÇÃO DE RISCOS:
                %s

                Forneça uma resposta conclusiva com recomendação prática.
                """, state.userQuestion, state.marketAnalysis, state.riskAssessment);
    }

    private String classifyQuestion(String question) {
        String lower = question.toLowerCase();
        if (lower.contains("preço") || lower.contains("cotação")) return "PRICE_QUERY";
        if (lower.contains("tendência") || lower.contains("previsão")) return "TREND_ANALYSIS";
        if (lower.contains("risco") || lower.contains("crise")) return "RISK_ASSESSMENT";
        if (lower.contains("comprar") || lower.contains("vender")) return "TRADING_ADVICE";
        return "GENERAL_QUERY";
    }

    private String extractSentiment(String text) {
        String lower = text.toLowerCase();
        long bullishCount = Arrays.stream(new String[]{"alta", "subir", "positivo", "crescimento",
                "comprar", "bullish", "valorização", "otimista"})
                .filter(lower::contains).count();
        long bearishCount = Arrays.stream(new String[]{"queda", "cair", "negativo", "risco",
                "vender", "bearish", "desvalorização", "pessimista"})
                .filter(lower::contains).count();

        if (bullishCount > bearishCount) return "BULLISH";
        if (bearishCount > bullishCount) return "BEARISH";
        return "NEUTRAL";
    }

    private double estimateConfidence(GraphState state) {
        boolean hasMarketAnalysis = state.marketAnalysis != null && !state.marketAnalysis.isBlank();
        boolean hasRiskAssessment = state.riskAssessment != null && !state.riskAssessment.isBlank();
        boolean hasContext = state.commodityContext != null && !state.commodityContext.isBlank();

        double score = 0.5;
        if (hasMarketAnalysis) score += 0.2;
        if (hasRiskAssessment) score += 0.15;
        if (hasContext) score += 0.15;
        return Math.min(score, 1.0);
    }

    private int countWords(String text) {
        if (text == null || text.isBlank()) return 0;
        return text.split("\\s+").length;
    }

    private AIAnalysisResponse buildResponse(GraphState state) {
        List<String> insights = new ArrayList<>();
        List<String> recommendations = new ArrayList<>();

        if (state.marketAnalysis != null) insights.add(state.marketAnalysis);
        if (state.riskAssessment != null) insights.add(state.riskAssessment);
        if (state.finalRecommendation != null) recommendations.add(state.finalRecommendation);

        return AIAnalysisResponse.builder()
                .answer(state.finalRecommendation != null ? state.finalRecommendation : "Sem resposta disponível")
                .analysisType(state.metadata.getOrDefault("question_type", "GENERAL"))
                .insights(insights)
                .recommendations(recommendations)
                .sentiment(state.sentiment)
                .confidenceScore(state.confidenceScore)
                .generatedAt(LocalDateTime.now())
                .modelUsed("gpt-4o-mini via LangChain4j + LangGraph Workflow")
                .workflowSteps(state.steps)
                .build();
    }
}
