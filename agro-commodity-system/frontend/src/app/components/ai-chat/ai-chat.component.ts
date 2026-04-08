import { Component, OnInit, ViewChild, ElementRef, AfterViewChecked } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatChipsModule } from '@angular/material/chips';
import { MatSelectModule } from '@angular/material/select';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { ChatMessage, AIAnalysisResponse } from '../../models/commodity.model';
import { AiService } from '../../services/ai.service';

type AnalysisMode = 'CHAT' | 'MARKET_ANALYSIS' | 'RECOMMENDATION';

@Component({
  selector: 'app-ai-chat',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatCardModule, MatButtonModule, MatIconModule, MatInputModule,
    MatFormFieldModule, MatProgressSpinnerModule, MatChipsModule,
    MatSelectModule, MatExpansionModule, MatTooltipModule, MatDividerModule
  ],
  template: `
    <div class="chat-container">
      <!-- Sidebar -->
      <div class="chat-sidebar">
        <div class="sidebar-header">
          <mat-icon class="ai-icon">smart_toy</mat-icon>
          <div>
            <h2>IA Assistente</h2>
            <span class="powered-by">LangChain4j + LangGraph</span>
          </div>
        </div>

        <mat-divider></mat-divider>

        <div class="mode-section">
          <label class="section-label">Modo de Análise</label>
          <div class="mode-buttons">
            <button mat-stroked-button [class.active]="mode === 'CHAT'" (click)="mode = 'CHAT'">
              <mat-icon>chat</mat-icon> Chat
            </button>
            <button mat-stroked-button [class.active]="mode === 'MARKET_ANALYSIS'" (click)="mode = 'MARKET_ANALYSIS'">
              <mat-icon>analytics</mat-icon> Mercado
            </button>
            <button mat-stroked-button [class.active]="mode === 'RECOMMENDATION'" (click)="mode = 'RECOMMENDATION'">
              <mat-icon>recommend</mat-icon> Recomendação
            </button>
          </div>
        </div>

        <mat-divider></mat-divider>

        <div class="quick-questions">
          <label class="section-label">Perguntas Rápidas</label>
          <button mat-button *ngFor="let q of quickQuestions" (click)="askQuestion(q)" class="quick-btn">
            {{ q }}
          </button>
        </div>

        <mat-divider></mat-divider>

        <div class="sidebar-stats" *ngIf="lastAnalysis">
          <label class="section-label">Última Análise</label>
          <div class="stat-item">
            <mat-icon>psychology</mat-icon>
            <span>Sentimento: <strong [class]="getSentimentClass(lastAnalysis.sentiment)">
              {{ getSentimentLabel(lastAnalysis.sentiment) }}
            </strong></span>
          </div>
          <div class="stat-item">
            <mat-icon>speed</mat-icon>
            <span>Confiança: <strong>{{ (lastAnalysis.confidenceScore * 100).toFixed(0) }}%</strong></span>
          </div>
          <div class="stat-item">
            <mat-icon>memory</mat-icon>
            <span class="model-text">{{ lastAnalysis.modelUsed }}</span>
          </div>
        </div>
      </div>

      <!-- Chat Area -->
      <div class="chat-main">
        <div class="chat-messages" #messagesContainer>
          <!-- Welcome message -->
          <div class="welcome-message" *ngIf="messages.length === 0">
            <mat-icon class="welcome-icon">eco</mat-icon>
            <h3>Bem-vindo ao Assistente de Commodities IA</h3>
            <p>Pergunte sobre preços, tendências, riscos e estratégias do agronegócio brasileiro.</p>
            <p class="powered">Powered by <strong>LangChain4j + LangGraph Workflow</strong></p>
          </div>

          <!-- Messages -->
          <div *ngFor="let msg of messages" class="message" [class.user-message]="msg.role === 'user'"
               [class.assistant-message]="msg.role === 'assistant'">
            <div class="message-avatar">
              <mat-icon>{{ msg.role === 'user' ? 'person' : 'smart_toy' }}</mat-icon>
            </div>
            <div class="message-content">
              <div class="message-text">{{ msg.content }}</div>
              <div class="message-time">{{ msg.timestamp | date:'HH:mm' }}</div>

              <!-- Workflow Steps (LangGraph) -->
              <mat-expansion-panel *ngIf="msg.analysis?.workflowSteps?.length" class="workflow-panel">
                <mat-expansion-panel-header>
                  <mat-panel-title>
                    <mat-icon style="font-size:16px;margin-right:4px">account_tree</mat-icon>
                    LangGraph Workflow ({{ msg.analysis!.workflowSteps.length }} etapas)
                  </mat-panel-title>
                </mat-expansion-panel-header>
                <div class="workflow-steps">
                  <div *ngFor="let step of msg.analysis!.workflowSteps" class="workflow-step"
                       [class.step-completed]="step.status === 'COMPLETED'"
                       [class.step-error]="step.status === 'ERROR'">
                    <mat-icon class="step-icon">
                      {{ step.status === 'COMPLETED' ? 'check_circle' : step.status === 'ERROR' ? 'error' : 'skip_next' }}
                    </mat-icon>
                    <div class="step-info">
                      <strong>{{ step.stepName | titlecase }}</strong>
                      <span>{{ step.description }}</span>
                      <span class="step-output" *ngIf="step.output">→ {{ step.output }}</span>
                    </div>
                  </div>
                </div>
              </mat-expansion-panel>

              <!-- Sentiment chip -->
              <mat-chip *ngIf="msg.analysis?.sentiment" [class]="getSentimentClass(msg.analysis!.sentiment)">
                {{ getSentimentLabel(msg.analysis!.sentiment) }}
              </mat-chip>
            </div>
          </div>

          <!-- Typing indicator -->
          <div class="message assistant-message typing" *ngIf="loading">
            <div class="message-avatar"><mat-icon>smart_toy</mat-icon></div>
            <div class="message-content">
              <div class="typing-indicator"><span></span><span></span><span></span></div>
              <div class="loading-text">Analisando com LangGraph...</div>
            </div>
          </div>
        </div>

        <!-- Input -->
        <div class="chat-input">
          <mat-form-field appearance="outline" class="input-field">
            <mat-label>{{ getInputPlaceholder() }}</mat-label>
            <textarea matInput [(ngModel)]="userInput" (keydown.enter)="onEnter($event)"
                      rows="1" [disabled]="loading"></textarea>
          </mat-form-field>
          <button mat-fab color="primary" (click)="sendMessage()" [disabled]="!userInput.trim() || loading"
                  matTooltip="Enviar mensagem">
            <mat-icon>{{ loading ? 'hourglass_empty' : 'send' }}</mat-icon>
          </button>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .chat-container { display: flex; height: calc(100vh - 64px); background: #f5f5f5; }

    /* Sidebar */
    .chat-sidebar { width: 280px; background: white; border-right: 1px solid #e0e0e0; display: flex; flex-direction: column; overflow-y: auto; }
    .sidebar-header { display: flex; align-items: center; gap: 12px; padding: 20px 16px; background: #1b5e20; color: white; }
    .ai-icon { font-size: 32px; width: 32px; height: 32px; }
    .sidebar-header h2 { margin: 0; font-size: 1rem; }
    .powered-by { font-size: 0.7rem; opacity: 0.8; }

    .mode-section, .quick-questions, .sidebar-stats { padding: 12px 16px; }
    .section-label { font-size: 0.75rem; text-transform: uppercase; color: #888; letter-spacing: 0.5px; display: block; margin-bottom: 8px; }

    .mode-buttons { display: flex; flex-direction: column; gap: 6px; }
    .mode-buttons button { justify-content: flex-start; gap: 8px; }
    .mode-buttons button.active { background: #e8f5e9; color: #2e7d32; border-color: #2e7d32; }

    .quick-btn { display: block; text-align: left; font-size: 0.8rem; color: #555; white-space: normal; line-height: 1.3; margin-bottom: 4px; }
    .stat-item { display: flex; align-items: center; gap: 8px; font-size: 0.85rem; margin-bottom: 6px; }
    .stat-item mat-icon { font-size: 16px; width: 16px; height: 16px; color: #888; }
    .model-text { font-size: 0.72rem; color: #888; }
    .bullish-label { color: #2e7d32; }
    .bearish-label { color: #c62828; }
    .neutral-label { color: #f57c00; }

    /* Main Chat */
    .chat-main { flex: 1; display: flex; flex-direction: column; overflow: hidden; }

    .chat-messages { flex: 1; overflow-y: auto; padding: 24px; display: flex; flex-direction: column; gap: 16px; }

    .welcome-message { text-align: center; padding: 48px 24px; color: #555; }
    .welcome-icon { font-size: 64px; width: 64px; height: 64px; color: #2e7d32; margin-bottom: 16px; }
    .welcome-message h3 { color: #2e7d32; }
    .powered { font-size: 0.85rem; color: #888; margin-top: 8px; }

    .message { display: flex; gap: 12px; max-width: 85%; }
    .user-message { align-self: flex-end; flex-direction: row-reverse; }
    .assistant-message { align-self: flex-start; }

    .message-avatar { width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
    .user-message .message-avatar { background: #1565c0; color: white; }
    .assistant-message .message-avatar { background: #2e7d32; color: white; }

    .message-content { background: white; border-radius: 12px; padding: 12px 16px; box-shadow: 0 1px 4px rgba(0,0,0,0.1); }
    .user-message .message-content { background: #1565c0; color: white; }
    .message-text { white-space: pre-wrap; line-height: 1.5; }
    .message-time { font-size: 0.7rem; color: #aaa; margin-top: 4px; }
    .user-message .message-time { color: rgba(255,255,255,0.7); }

    .workflow-panel { margin-top: 8px; background: #fafafa; }
    .workflow-steps { display: flex; flex-direction: column; gap: 8px; padding: 4px 0; }
    .workflow-step { display: flex; gap: 8px; align-items: flex-start; }
    .step-icon { font-size: 18px; width: 18px; height: 18px; flex-shrink: 0; }
    .step-completed .step-icon { color: #2e7d32; }
    .step-error .step-icon { color: #c62828; }
    .step-info { display: flex; flex-direction: column; font-size: 0.82rem; }
    .step-output { color: #888; font-style: italic; }

    .typing .message-content { padding: 16px; }
    .typing-indicator { display: flex; gap: 4px; }
    .typing-indicator span { width: 8px; height: 8px; background: #888; border-radius: 50%; animation: bounce 1.4s infinite; }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes bounce { 0%,80%,100% { transform: scale(0); } 40% { transform: scale(1); } }
    .loading-text { font-size: 0.78rem; color: #888; margin-top: 4px; }

    .chat-input { display: flex; gap: 12px; align-items: flex-end; padding: 16px; background: white; border-top: 1px solid #e0e0e0; }
    .input-field { flex: 1; }

    @media (max-width: 768px) {
      .chat-sidebar { display: none; }
    }
  `]
})
export class AiChatComponent implements OnInit, AfterViewChecked {
  @ViewChild('messagesContainer') private messagesContainer!: ElementRef;

  messages: ChatMessage[] = [];
  userInput = '';
  loading = false;
  mode: AnalysisMode = 'CHAT';
  lastAnalysis?: AIAnalysisResponse;
  commodityId?: number;

  quickQuestions = [
    'Qual a tendência da soja para as próximas semanas?',
    'O milho está em alta ou baixa?',
    'Quais fatores impactam o preço do boi gordo?',
    'Como o câmbio afeta as exportações agrícolas?',
    'Devo comprar ou vender café agora?',
    'Quais são os riscos climáticos para o algodão?'
  ];

  constructor(private aiService: AiService, private route: ActivatedRoute) {}

  ngOnInit(): void {
    this.route.queryParams.subscribe(params => {
      if (params['commodityId']) {
        this.commodityId = Number(params['commodityId']);
        const name = params['name'] ?? 'esta commodity';
        this.askQuestion(`Faça uma análise completa de ${name}`);
      }
    });
  }

  ngAfterViewChecked(): void {
    this.scrollToBottom();
  }

  sendMessage(): void {
    const text = this.userInput.trim();
    if (!text || this.loading) return;

    this.messages.push({ role: 'user', content: text, timestamp: new Date() });
    this.userInput = '';
    this.loading = true;

    const obs = this.mode === 'MARKET_ANALYSIS'
      ? this.aiService.marketAnalysis(text, this.commodityId)
      : this.mode === 'RECOMMENDATION'
        ? this.aiService.recommendation(text, this.commodityId)
        : this.aiService.chat(text, this.commodityId);

    obs.subscribe({
      next: response => {
        this.lastAnalysis = response;
        this.messages.push({
          role: 'assistant',
          content: response.answer,
          timestamp: new Date(),
          analysis: response
        });
        this.loading = false;
      },
      error: () => {
        this.messages.push({
          role: 'assistant',
          content: 'Desculpe, ocorreu um erro na análise. Verifique se o backend está rodando e a chave da API OpenAI está configurada.',
          timestamp: new Date()
        });
        this.loading = false;
      }
    });
  }

  askQuestion(q: string): void {
    this.userInput = q;
    this.sendMessage();
  }

  onEnter(event: Event): void {
    const keyEvent = event as KeyboardEvent;
    if (!keyEvent.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  getSentimentClass(sentiment: string): string {
    const map: Record<string, string> = { BULLISH: 'bullish-chip', BEARISH: 'bearish-chip', NEUTRAL: 'neutral-chip' };
    return map[sentiment] ?? '';
  }

  getSentimentLabel(sentiment: string): string {
    const map: Record<string, string> = { BULLISH: 'Alta (Bullish)', BEARISH: 'Baixa (Bearish)', NEUTRAL: 'Neutro' };
    return map[sentiment] ?? sentiment;
  }

  getInputPlaceholder(): string {
    const map: Record<AnalysisMode, string> = {
      CHAT: 'Pergunte sobre commodities agrícolas...',
      MARKET_ANALYSIS: 'Peça uma análise de mercado...',
      RECOMMENDATION: 'Peça uma recomendação de compra/venda...'
    };
    return map[this.mode];
  }

  private scrollToBottom(): void {
    try { this.messagesContainer.nativeElement.scrollTop = this.messagesContainer.nativeElement.scrollHeight; }
    catch (_) { /* ignore */ }
  }
}
