import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { Subscription, interval } from 'rxjs';
import { switchMap } from 'rxjs/operators';
import { Commodity, COMMODITY_TYPE_LABELS } from '../../models/commodity.model';
import { CommodityService } from '../../services/commodity.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [
    CommonModule, MatCardModule, MatButtonModule, MatIconModule,
    MatChipsModule, MatProgressSpinnerModule, MatTooltipModule, MatDividerModule
  ],
  template: `
    <div class="dashboard-container">
      <div class="header">
        <h1><mat-icon>dashboard</mat-icon> Dashboard de Mercado</h1>
        <span class="subtitle">Cotações em tempo real do agronegócio brasileiro</span>
      </div>

      <!-- Summary Cards -->
      <div class="summary-cards" *ngIf="!loading">
        <mat-card class="summary-card">
          <mat-card-content>
            <div class="summary-icon green"><mat-icon>trending_up</mat-icon></div>
            <div class="summary-info">
              <span class="summary-value">{{ bullishCount }}</span>
              <span class="summary-label">Em Alta</span>
            </div>
          </mat-card-content>
        </mat-card>
        <mat-card class="summary-card">
          <mat-card-content>
            <div class="summary-icon red"><mat-icon>trending_down</mat-icon></div>
            <div class="summary-info">
              <span class="summary-value">{{ bearishCount }}</span>
              <span class="summary-label">Em Baixa</span>
            </div>
          </mat-card-content>
        </mat-card>
        <mat-card class="summary-card">
          <mat-card-content>
            <div class="summary-icon blue"><mat-icon>grain</mat-icon></div>
            <div class="summary-info">
              <span class="summary-value">{{ commodities.length }}</span>
              <span class="summary-label">Commodities</span>
            </div>
          </mat-card-content>
        </mat-card>
        <mat-card class="summary-card">
          <mat-card-content>
            <div class="summary-icon orange"><mat-icon>schedule</mat-icon></div>
            <div class="summary-info">
              <span class="summary-value">{{ lastUpdate | date:'HH:mm' }}</span>
              <span class="summary-label">Última Atualização</span>
            </div>
          </mat-card-content>
        </mat-card>
      </div>

      <div *ngIf="loading" class="loading-state">
        <mat-spinner diameter="48"></mat-spinner>
        <span>Carregando cotações...</span>
      </div>

      <!-- Commodity Grid -->
      <div class="commodity-grid" *ngIf="!loading">
        <mat-card
          *ngFor="let c of commodities"
          class="commodity-card"
          [class.bullish]="(c.priceVariation ?? 0) > 0"
          [class.bearish]="(c.priceVariation ?? 0) < 0"
          (click)="viewDetail(c)"
          matTooltip="Clique para detalhes">

          <mat-card-header>
            <div class="commodity-header">
              <span class="commodity-code">{{ c.code }}</span>
              <mat-chip [class]="getTypeClass(c.type)">{{ getTypeLabel(c.type) }}</mat-chip>
            </div>
          </mat-card-header>

          <mat-card-content>
            <h3 class="commodity-name">{{ c.name }}</h3>

            <div class="price-section">
              <span class="current-price">
                R$ {{ c.currentPrice | number:'1.2-2' }}
                <span class="unit">/ {{ c.unit }}</span>
              </span>
              <div class="variation" [class.positive]="(c.priceVariation ?? 0) > 0"
                                     [class.negative]="(c.priceVariation ?? 0) < 0">
                <mat-icon>{{ (c.priceVariation ?? 0) >= 0 ? 'arrow_upward' : 'arrow_downward' }}</mat-icon>
                {{ c.priceVariationFormatted }}
              </div>
            </div>

            <div class="region" *ngIf="c.originRegion">
              <mat-icon>location_on</mat-icon> {{ c.originRegion }}
            </div>
          </mat-card-content>

          <mat-card-actions>
            <button mat-button color="primary" (click)="viewDetail(c); $event.stopPropagation()">
              <mat-icon>bar_chart</mat-icon> Gráfico
            </button>
            <button mat-button color="accent" (click)="analyzeWithAI(c); $event.stopPropagation()">
              <mat-icon>smart_toy</mat-icon> Analisar IA
            </button>
          </mat-card-actions>
        </mat-card>
      </div>
    </div>
  `,
  styles: [`
    .dashboard-container { padding: 24px; max-width: 1400px; margin: 0 auto; }
    .header { margin-bottom: 24px; }
    .header h1 { display: flex; align-items: center; gap: 8px; margin: 0; font-size: 1.8rem; color: #2e7d32; }
    .subtitle { color: #666; font-size: 0.9rem; }

    .summary-cards { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
    .summary-card mat-card-content { display: flex; align-items: center; gap: 16px; padding: 16px; }
    .summary-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; }
    .summary-icon mat-icon { color: white; font-size: 24px; }
    .summary-icon.green { background: #2e7d32; }
    .summary-icon.red { background: #c62828; }
    .summary-icon.blue { background: #1565c0; }
    .summary-icon.orange { background: #e65100; }
    .summary-value { font-size: 1.8rem; font-weight: 700; display: block; }
    .summary-label { color: #666; font-size: 0.85rem; }

    .loading-state { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 48px; }

    .commodity-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px; }

    .commodity-card { cursor: pointer; transition: transform 0.2s, box-shadow 0.2s; border-top: 4px solid #ccc; }
    .commodity-card:hover { transform: translateY(-2px); box-shadow: 0 6px 20px rgba(0,0,0,0.15); }
    .commodity-card.bullish { border-top-color: #2e7d32; }
    .commodity-card.bearish { border-top-color: #c62828; }

    .commodity-header { display: flex; justify-content: space-between; align-items: center; width: 100%; padding: 8px 16px 0; }
    .commodity-code { font-weight: 700; font-size: 1rem; color: #555; letter-spacing: 1px; }
    .commodity-name { font-size: 1.1rem; font-weight: 600; margin: 4px 0 8px; }

    .price-section { display: flex; justify-content: space-between; align-items: flex-end; margin: 8px 0; }
    .current-price { font-size: 1.4rem; font-weight: 700; }
    .unit { font-size: 0.8rem; color: #888; font-weight: 400; }

    .variation { display: flex; align-items: center; gap: 2px; font-weight: 600; font-size: 0.95rem; }
    .variation mat-icon { font-size: 18px; height: 18px; width: 18px; }
    .positive { color: #2e7d32; }
    .negative { color: #c62828; }

    .region { display: flex; align-items: center; gap: 4px; color: #888; font-size: 0.85rem; margin-top: 4px; }
    .region mat-icon { font-size: 16px; height: 16px; width: 16px; }

    @media (max-width: 768px) {
      .summary-cards { grid-template-columns: repeat(2, 1fr); }
      .commodity-grid { grid-template-columns: 1fr; }
    }
  `]
})
export class DashboardComponent implements OnInit, OnDestroy {
  commodities: Commodity[] = [];
  loading = true;
  lastUpdate = new Date();
  private subscription = new Subscription();

  constructor(private commodityService: CommodityService, private router: Router) {}

  ngOnInit(): void {
    this.loadCommodities();
    // Auto-refresh every 60 seconds
    this.subscription.add(
      interval(60000).pipe(switchMap(() => this.commodityService.findAll()))
        .subscribe(data => { this.commodities = data; this.lastUpdate = new Date(); })
    );
  }

  ngOnDestroy(): void { this.subscription.unsubscribe(); }

  loadCommodities(): void {
    this.loading = true;
    this.commodityService.findAll().subscribe({
      next: data => { this.commodities = data; this.loading = false; this.lastUpdate = new Date(); },
      error: () => { this.loading = false; }
    });
  }

  get bullishCount(): number { return this.commodities.filter(c => (c.priceVariation ?? 0) > 0).length; }
  get bearishCount(): number { return this.commodities.filter(c => (c.priceVariation ?? 0) < 0).length; }

  getTypeLabel(type: string): string { return COMMODITY_TYPE_LABELS[type as keyof typeof COMMODITY_TYPE_LABELS] ?? type; }

  getTypeClass(type: string): string {
    const map: Record<string, string> = {
      GRAOS: 'chip-yellow', CAFE: 'chip-brown', CARNES: 'chip-red',
      FIBRAS: 'chip-blue', ACUCAR_ALCOOL: 'chip-green'
    };
    return map[type] ?? '';
  }

  viewDetail(c: Commodity): void { this.router.navigate(['/commodities', c.id]); }

  analyzeWithAI(c: Commodity): void {
    this.router.navigate(['/ai-chat'], { queryParams: { commodityId: c.id, name: c.name } });
  }
}
