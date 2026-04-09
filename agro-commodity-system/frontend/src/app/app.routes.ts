import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  {
    path: 'dashboard',
    loadComponent: () => import('./components/dashboard/dashboard.component').then(m => m.DashboardComponent)
  },
  {
    path: 'commodities',
    loadComponent: () => import('./components/commodity-list/commodity-list.component').then(m => m.CommodityListComponent)
  },
  {
    path: 'commodities/:id',
    loadComponent: () => import('./components/commodity-detail/commodity-detail.component').then(m => m.CommodityDetailComponent)
  },
  {
    path: 'ai-chat',
    loadComponent: () => import('./components/ai-chat/ai-chat.component').then(m => m.AiChatComponent)
  },
  { path: '**', redirectTo: 'dashboard' }
];
