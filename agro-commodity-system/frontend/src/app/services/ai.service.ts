import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { AIAnalysisRequest, AIAnalysisResponse } from '../models/commodity.model';

@Injectable({ providedIn: 'root' })
export class AiService {
  private readonly base = `${environment.apiUrl}/ai`;

  constructor(private http: HttpClient) {}

  chat(question: string, commodityId?: number): Observable<AIAnalysisResponse> {
    const req: AIAnalysisRequest = { question, commodityId, analysisType: 'CHAT' };
    return this.http.post<AIAnalysisResponse>(`${this.base}/chat`, req);
  }

  marketAnalysis(question: string, commodityId?: number): Observable<AIAnalysisResponse> {
    const req: AIAnalysisRequest = { question, commodityId, analysisType: 'MARKET_ANALYSIS' };
    return this.http.post<AIAnalysisResponse>(`${this.base}/market-analysis`, req);
  }

  recommendation(question: string, commodityId?: number): Observable<AIAnalysisResponse> {
    const req: AIAnalysisRequest = { question, commodityId, analysisType: 'RECOMMENDATION' };
    return this.http.post<AIAnalysisResponse>(`${this.base}/recommendation`, req);
  }

  analyze(request: AIAnalysisRequest): Observable<AIAnalysisResponse> {
    return this.http.post<AIAnalysisResponse>(`${this.base}/analyze`, request);
  }
}
