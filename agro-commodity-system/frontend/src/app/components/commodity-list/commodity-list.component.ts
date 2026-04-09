import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { FormsModule, ReactiveFormsModule, FormBuilder, FormGroup, Validators } from '@angular/forms';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatDialogModule, MatDialog } from '@angular/material/dialog';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatSnackBarModule, MatSnackBar } from '@angular/material/snack-bar';
import { MatChipsModule } from '@angular/material/chips';
import { Commodity, CommodityType, COMMODITY_TYPE_LABELS } from '../../models/commodity.model';
import { CommodityService } from '../../services/commodity.service';

@Component({
  selector: 'app-commodity-list',
  standalone: true,
  imports: [
    CommonModule, FormsModule, ReactiveFormsModule,
    MatTableModule, MatCardModule, MatButtonModule, MatIconModule,
    MatInputModule, MatFormFieldModule, MatSelectModule,
    MatDialogModule, MatProgressSpinnerModule, MatSnackBarModule, MatChipsModule
  ],
  template: `
    <div class="list-container">
      <div class="page-header">
        <h1><mat-icon>grain</mat-icon> Gestão de Commodities</h1>
        <button mat-raised-button color="primary" (click)="showForm = !showForm">
          <mat-icon>{{ showForm ? 'close' : 'add' }}</mat-icon>
          {{ showForm ? 'Cancelar' : 'Nova Commodity' }}
        </button>
      </div>

      <!-- Create / Edit Form -->
      <mat-card class="form-card" *ngIf="showForm">
        <mat-card-header><mat-card-title>{{ editingId ? 'Editar' : 'Nova' }} Commodity</mat-card-title></mat-card-header>
        <mat-card-content>
          <form [formGroup]="form" (ngSubmit)="save()">
            <div class="form-row">
              <mat-form-field appearance="outline">
                <mat-label>Nome</mat-label>
                <input matInput formControlName="name" placeholder="Ex: Soja">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Código</mat-label>
                <input matInput formControlName="code" placeholder="Ex: SOY" style="text-transform:uppercase">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Tipo</mat-label>
                <mat-select formControlName="type">
                  <mat-option *ngFor="let t of types" [value]="t.value">{{ t.label }}</mat-option>
                </mat-select>
              </mat-form-field>
            </div>
            <div class="form-row">
              <mat-form-field appearance="outline">
                <mat-label>Preço Atual (R$)</mat-label>
                <input matInput type="number" formControlName="currentPrice" step="0.01">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Unidade</mat-label>
                <input matInput formControlName="unit" placeholder="Ex: saca 60kg">
              </mat-form-field>
              <mat-form-field appearance="outline">
                <mat-label>Região de Origem</mat-label>
                <input matInput formControlName="originRegion" placeholder="Ex: Mato Grosso">
              </mat-form-field>
            </div>
            <mat-form-field appearance="outline" class="full-width">
              <mat-label>Descrição</mat-label>
              <textarea matInput formControlName="description" rows="2"></textarea>
            </mat-form-field>
            <div class="form-actions">
              <button mat-raised-button color="primary" type="submit" [disabled]="form.invalid || saving">
                <mat-spinner *ngIf="saving" diameter="20"></mat-spinner>
                <mat-icon *ngIf="!saving">save</mat-icon>
                {{ saving ? 'Salvando...' : 'Salvar' }}
              </button>
            </div>
          </form>
        </mat-card-content>
      </mat-card>

      <!-- Filters -->
      <div class="filters">
        <mat-form-field appearance="outline">
          <mat-label>Buscar</mat-label>
          <input matInput [(ngModel)]="searchTerm" (input)="filterCommodities()" placeholder="Nome da commodity">
          <mat-icon matSuffix>search</mat-icon>
        </mat-form-field>
        <mat-form-field appearance="outline">
          <mat-label>Filtrar por tipo</mat-label>
          <mat-select [(ngModel)]="filterType" (selectionChange)="filterCommodities()">
            <mat-option value="">Todos</mat-option>
            <mat-option *ngFor="let t of types" [value]="t.value">{{ t.label }}</mat-option>
          </mat-select>
        </mat-form-field>
      </div>

      <!-- Table -->
      <mat-card>
        <mat-card-content>
          <div *ngIf="loading" class="loading-state">
            <mat-spinner diameter="40"></mat-spinner>
          </div>

          <table mat-table [dataSource]="filtered" *ngIf="!loading" class="commodity-table">
            <ng-container matColumnDef="code">
              <th mat-header-cell *matHeaderCellDef>Código</th>
              <td mat-cell *matCellDef="let c"><strong>{{ c.code }}</strong></td>
            </ng-container>

            <ng-container matColumnDef="name">
              <th mat-header-cell *matHeaderCellDef>Nome</th>
              <td mat-cell *matCellDef="let c">{{ c.name }}</td>
            </ng-container>

            <ng-container matColumnDef="type">
              <th mat-header-cell *matHeaderCellDef>Tipo</th>
              <td mat-cell *matCellDef="let c">
                <mat-chip>{{ getTypeLabel(c.type) }}</mat-chip>
              </td>
            </ng-container>

            <ng-container matColumnDef="price">
              <th mat-header-cell *matHeaderCellDef>Preço Atual</th>
              <td mat-cell *matCellDef="let c">
                R$ {{ c.currentPrice | number:'1.2-2' }} / {{ c.unit }}
              </td>
            </ng-container>

            <ng-container matColumnDef="variation">
              <th mat-header-cell *matHeaderCellDef>Variação</th>
              <td mat-cell *matCellDef="let c">
                <span [class.positive]="(c.priceVariation ?? 0) > 0"
                      [class.negative]="(c.priceVariation ?? 0) < 0">
                  <mat-icon style="font-size:16px;vertical-align:middle">
                    {{ (c.priceVariation ?? 0) >= 0 ? 'arrow_upward' : 'arrow_downward' }}
                  </mat-icon>
                  {{ c.priceVariationFormatted }}
                </span>
              </td>
            </ng-container>

            <ng-container matColumnDef="region">
              <th mat-header-cell *matHeaderCellDef>Região</th>
              <td mat-cell *matCellDef="let c">{{ c.originRegion ?? '-' }}</td>
            </ng-container>

            <ng-container matColumnDef="actions">
              <th mat-header-cell *matHeaderCellDef>Ações</th>
              <td mat-cell *matCellDef="let c">
                <button mat-icon-button color="primary" (click)="viewDetail(c)" matTooltip="Ver detalhes">
                  <mat-icon>bar_chart</mat-icon>
                </button>
                <button mat-icon-button color="accent" (click)="editCommodity(c)" matTooltip="Editar">
                  <mat-icon>edit</mat-icon>
                </button>
                <button mat-icon-button color="warn" (click)="deleteCommodity(c)" matTooltip="Remover">
                  <mat-icon>delete</mat-icon>
                </button>
              </td>
            </ng-container>

            <tr mat-header-row *matHeaderRowDef="displayedColumns"></tr>
            <tr mat-row *matRowDef="let row; columns: displayedColumns;" class="table-row"></tr>
          </table>
        </mat-card-content>
      </mat-card>
    </div>
  `,
  styles: [`
    .list-container { padding: 24px; max-width: 1400px; margin: 0 auto; }
    .page-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px; }
    .page-header h1 { display: flex; align-items: center; gap: 8px; margin: 0; color: #2e7d32; }
    .form-card { margin-bottom: 24px; }
    .form-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; }
    .full-width { width: 100%; }
    .form-actions { display: flex; justify-content: flex-end; margin-top: 8px; }
    .filters { display: flex; gap: 16px; margin-bottom: 16px; }
    .filters mat-form-field { width: 250px; }
    .loading-state { display: flex; justify-content: center; padding: 32px; }
    .commodity-table { width: 100%; }
    .table-row:hover { background: #f5f5f5; cursor: pointer; }
    .positive { color: #2e7d32; font-weight: 600; }
    .negative { color: #c62828; font-weight: 600; }
    mat-spinner { display: inline-block; }
  `]
})
export class CommodityListComponent implements OnInit {
  commodities: Commodity[] = [];
  filtered: Commodity[] = [];
  loading = true;
  saving = false;
  showForm = false;
  editingId?: number;
  searchTerm = '';
  filterType = '';

  form: FormGroup;
  displayedColumns = ['code', 'name', 'type', 'price', 'variation', 'region', 'actions'];

  types = Object.entries(COMMODITY_TYPE_LABELS).map(([value, label]) => ({ value, label }));

  constructor(
    private commodityService: CommodityService,
    private router: Router,
    private fb: FormBuilder,
    private snackBar: MatSnackBar
  ) {
    this.form = this.fb.group({
      name: ['', Validators.required],
      code: ['', Validators.required],
      type: ['GRAOS', Validators.required],
      currentPrice: [null, [Validators.required, Validators.min(0)]],
      unit: ['saca 60kg', Validators.required],
      originRegion: [''],
      description: [''],
      currency: ['BRL']
    });
  }

  ngOnInit(): void { this.load(); }

  load(): void {
    this.loading = true;
    this.commodityService.findAll().subscribe({
      next: data => { this.commodities = data; this.filtered = data; this.loading = false; },
      error: () => this.loading = false
    });
  }

  filterCommodities(): void {
    this.filtered = this.commodities.filter(c => {
      const matchesSearch = !this.searchTerm || c.name.toLowerCase().includes(this.searchTerm.toLowerCase());
      const matchesType = !this.filterType || c.type === this.filterType;
      return matchesSearch && matchesType;
    });
  }

  save(): void {
    if (this.form.invalid) return;
    this.saving = true;
    const data = this.form.value as Commodity;
    const obs = this.editingId
      ? this.commodityService.update(this.editingId, data)
      : this.commodityService.create(data);

    obs.subscribe({
      next: () => {
        this.snackBar.open('Salvo com sucesso!', 'OK', { duration: 3000 });
        this.saving = false;
        this.showForm = false;
        this.editingId = undefined;
        this.form.reset({ type: 'GRAOS', unit: 'saca 60kg', currency: 'BRL' });
        this.load();
      },
      error: err => {
        this.snackBar.open(err.error?.error ?? 'Erro ao salvar', 'OK', { duration: 4000 });
        this.saving = false;
      }
    });
  }

  editCommodity(c: Commodity): void {
    this.editingId = c.id;
    this.form.patchValue(c);
    this.showForm = true;
  }

  deleteCommodity(c: Commodity): void {
    if (!confirm(`Remover ${c.name}?`)) return;
    this.commodityService.delete(c.id!).subscribe({
      next: () => { this.snackBar.open('Removida!', 'OK', { duration: 2000 }); this.load(); },
      error: () => this.snackBar.open('Erro ao remover', 'OK', { duration: 3000 })
    });
  }

  viewDetail(c: Commodity): void { this.router.navigate(['/commodities', c.id]); }

  getTypeLabel(type: string): string {
    return COMMODITY_TYPE_LABELS[type as keyof typeof COMMODITY_TYPE_LABELS] ?? type;
  }
}
