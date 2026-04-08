import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router } from '@angular/router';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatTabsModule } from '@angular/material/tabs';
import { MatChipsModule } from '@angular/material/chips';
import { BaseChartDirective } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';
import { Commodity, PriceHistory, COMMODITY_TYPE_LABELS } from '../../models/commodity.model';
import { CommodityService } from '../../services/commodity.service';

@Component({
  selector: 'app-commodity-detail',
  standalone: true,
  imports: [
    CommonModule, FormsModule,
    MatCardModule, MatButtonModule, MatIconModule, MatInputModule,
    MatFormFieldModule, MatProgressSpinnerModule, MatSnackBarModule,
    MatTabsModule, MatChipsModule, BaseChartDirective
  ],
  template: `
    <div class="detail-container" *ngIf="commodity">
      <!-- Header -->
      <div class="detail-header">
        <button mat-icon-button (click)="goBack()">
          <mat-icon>arrow_back</mat-icon>
        </button>
        <div class="header-info">
          <span class="code-badge">{{ commodity.code }}</span>
          <h1>{{ commodity.name }}</h1>
          <mat-chip>{{ getTypeLabel(commodity.type) }}</mat-chip>
        </div>
        <div class="header-price">
          <span class="big-price">R$ {{ commodity.currentPrice | number:'1.2-2' }}</span>
          <span class="price-unit">/ {{ commodity.unit }}</span>
          <div class="big-variation" [class.positive]="(commodity.priceVariation ?? 0) > 0"
                                     [class.negative]="(commodity.priceVariation ?? 0) < 0">
            <mat-icon>{{ (commodity.priceVariation ?? 0) >= 0 ? 'trending_up' : 'trending_down' }}</mat-icon>
            {{ commodity.priceVariationFormatted }}
          </div>
        </div>
      </div>

      <mat-tab-group>
        <!-- Chart Tab -->
        <mat-tab label="Histórico de Preços">
          <div class="tab-content">
            <mat-card>
              <mat-card-header>
                <mat-card-title>Evolução do Preço (últimas {{ priceHistory.length }} atualizações)</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                <div *ngIf="loadingHistory" class="loading-state"><mat-spinner diameter="40"></mat-spinner></div>
                <div class="chart-wrapper" *ngIf="!loadingHistory && priceHistory.length > 0">
                  <canvas baseChart
                    [data]="lineChartData"
                    [options]="lineChartOptions"
                    [type]="lineChartType">
                  </canvas>
                </div>
                <div *ngIf="!loadingHistory && priceHistory.length === 0" class="empty-state">
                  Sem histórico disponível
                </div>
              </mat-card-content>
            </mat-card>
          </div>
        </mat-tab>

        <!-- Update Price Tab -->
        <mat-tab label="Atualizar Preço">
          <div class="tab-content">
            <mat-card class="update-card">
              <mat-card-header>
                <mat-card-title>Atualização de Cotação</mat-card-title>
              </mat-card-header>
              <mat-card-content>
                <div class="current-info">
                  <span>Preço atual: <strong>R$ {{ commodity.currentPrice | number:'1.2-2' }}</strong></span>
                  <span class="separator">|</span>
                  <span *ngIf="commodity.originRegion">Região: {{ commodity.originRegion }}</span>
                </div>
                <div class="price-update-form">
                  <mat-form-field appearance="outline">
                    <mat-label>Novo Preço (R$)</mat-label>
                    <input matInput type="number" [(ngModel)]="newPrice" step="0.01" min="0">
                  </mat-form-field>
                  <button mat-raised-button color="primary" (click)="updatePrice()" [disabled]="!newPrice || saving">
                    <mat-spinner *ngIf="saving" diameter="20"></mat-spinner>
                    <mat-icon *ngIf="!saving">update</mat-icon>
                    {{ saving ? 'Atualizando...' : 'Atualizar' }}
                  </button>
                </div>
              </mat-card-content>
            </mat-card>
          </div>
        </mat-tab>

        <!-- Info Tab -->
        <mat-tab label="Informações">
          <div class="tab-content">
            <mat-card>
              <mat-card-content>
                <div class="info-grid">
                  <div class="info-item">
                    <span class="info-label">Nome</span>
                    <span class="info-value">{{ commodity.name }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Código</span>
                    <span class="info-value">{{ commodity.code }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Tipo</span>
                    <span class="info-value">{{ getTypeLabel(commodity.type) }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Unidade</span>
                    <span class="info-value">{{ commodity.unit }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Moeda</span>
                    <span class="info-value">{{ commodity.currency }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Região</span>
                    <span class="info-value">{{ commodity.originRegion ?? 'N/A' }}</span>
                  </div>
                  <div class="info-item">
                    <span class="info-label">Última Atualização</span>
                    <span class="info-value">{{ commodity.lastUpdated | date:'dd/MM/yyyy HH:mm' }}</span>
                  </div>
                  <div class="info-item" *ngIf="commodity.description">
                    <span class="info-label">Descrição</span>
                    <span class="info-value">{{ commodity.description }}</span>
                  </div>
                </div>
              </mat-card-content>
            </mat-card>
          </div>
        </mat-tab>
      </mat-tab-group>
    </div>

    <div *ngIf="loading" class="loading-state page-loading">
      <mat-spinner diameter="60"></mat-spinner>
    </div>
  `,
  styles: [`
    .detail-container { padding: 24px; max-width: 1200px; margin: 0 auto; }
    .detail-header { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; background: white; padding: 16px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .header-info { flex: 1; }
    .code-badge { background: #e8f5e9; color: #2e7d32; padding: 2px 10px; border-radius: 12px; font-weight: 700; font-size: 0.85rem; }
    .header-info h1 { margin: 4px 0; font-size: 1.6rem; }
    .header-price { text-align: right; }
    .big-price { font-size: 2rem; font-weight: 700; display: block; }
    .price-unit { color: #888; font-size: 0.9rem; }
    .big-variation { display: flex; align-items: center; justify-content: flex-end; gap: 4px; font-size: 1.1rem; font-weight: 600; }
    .positive { color: #2e7d32; }
    .negative { color: #c62828; }
    .tab-content { padding: 16px 0; }
    .chart-wrapper { position: relative; height: 350px; }
    .loading-state { display: flex; justify-content: center; padding: 32px; }
    .page-loading { padding: 80px; }
    .empty-state { text-align: center; padding: 32px; color: #888; }
    .update-card { max-width: 500px; }
    .current-info { margin-bottom: 16px; color: #555; }
    .separator { margin: 0 8px; }
    .price-update-form { display: flex; gap: 16px; align-items: center; }
    .price-update-form mat-form-field { width: 200px; }
    .info-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
    .info-item { display: flex; flex-direction: column; }
    .info-label { font-size: 0.8rem; color: #888; text-transform: uppercase; letter-spacing: 0.5px; }
    .info-value { font-size: 1rem; font-weight: 500; margin-top: 2px; }
  `]
})
export class CommodityDetailComponent implements OnInit {
  commodity?: Commodity;
  priceHistory: PriceHistory[] = [];
  loading = true;
  loadingHistory = true;
  saving = false;
  newPrice?: number;

  lineChartType: ChartType = 'line';
  lineChartData: ChartConfiguration['data'] = { datasets: [], labels: [] };
  lineChartOptions: ChartConfiguration['options'] = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { display: false }, tooltip: { mode: 'index' } },
    scales: {
      y: {
        title: { display: true, text: 'Preço (R$)' },
        ticks: { callback: (v) => 'R$ ' + Number(v).toFixed(2) }
      },
      x: { title: { display: true, text: 'Data' } }
    },
    elements: { point: { radius: 3 }, line: { tension: 0.4 } }
  };

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private commodityService: CommodityService,
    private snackBar: MatSnackBar
  ) {}

  ngOnInit(): void {
    const id = Number(this.route.snapshot.paramMap.get('id'));
    this.commodityService.findById(id).subscribe({
      next: c => { this.commodity = c; this.loading = false; this.loadHistory(id); },
      error: () => { this.loading = false; this.router.navigate(['/commodities']); }
    });
  }

  loadHistory(id: number): void {
    this.loadingHistory = true;
    this.commodityService.getPriceHistory(id, 30).subscribe({
      next: history => {
        this.priceHistory = history.reverse();
        this.buildChart();
        this.loadingHistory = false;
      },
      error: () => this.loadingHistory = false
    });
  }

  buildChart(): void {
    this.lineChartData = {
      labels: this.priceHistory.map(h => new Date(h.recordedAt).toLocaleDateString('pt-BR')),
      datasets: [{
        data: this.priceHistory.map(h => h.price),
        label: this.commodity?.name ?? '',
        borderColor: '#2e7d32',
        backgroundColor: 'rgba(46,125,50,0.1)',
        fill: true,
        pointBackgroundColor: '#2e7d32'
      }]
    };
  }

  updatePrice(): void {
    if (!this.newPrice || !this.commodity?.id) return;
    this.saving = true;
    this.commodityService.updatePrice(this.commodity.id, this.newPrice).subscribe({
      next: updated => {
        this.commodity = updated;
        this.saving = false;
        this.snackBar.open('Preço atualizado!', 'OK', { duration: 3000 });
        this.loadHistory(updated.id!);
      },
      error: () => { this.saving = false; this.snackBar.open('Erro ao atualizar preço', 'OK', { duration: 3000 }); }
    });
  }

  goBack(): void { this.router.navigate(['/commodities']); }

  getTypeLabel(type: string): string {
    return COMMODITY_TYPE_LABELS[type as keyof typeof COMMODITY_TYPE_LABELS] ?? type;
  }
}
