import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [RouterLink, RouterLinkActive, MatToolbarModule, MatButtonModule, MatIconModule],
  template: `
    <mat-toolbar color="primary" class="navbar">
      <mat-icon class="logo-icon">eco</mat-icon>
      <span class="brand">AgroAI Commodities</span>
      <span class="spacer"></span>
      <button mat-button routerLink="/dashboard" routerLinkActive="active-link">
        <mat-icon>dashboard</mat-icon> Dashboard
      </button>
      <button mat-button routerLink="/commodities" routerLinkActive="active-link">
        <mat-icon>grain</mat-icon> Commodities
      </button>
      <button mat-button routerLink="/ai-chat" routerLinkActive="active-link">
        <mat-icon>smart_toy</mat-icon> IA Assistente
      </button>
    </mat-toolbar>
  `,
  styles: [`
    .navbar { gap: 8px; }
    .logo-icon { margin-right: 8px; font-size: 28px; }
    .brand { font-size: 1.2rem; font-weight: 600; letter-spacing: 0.5px; }
    .spacer { flex: 1; }
    .active-link { background: rgba(255,255,255,0.15) !important; border-radius: 4px; }
    button mat-icon { margin-right: 4px; }
  `]
})
export class NavbarComponent {}
