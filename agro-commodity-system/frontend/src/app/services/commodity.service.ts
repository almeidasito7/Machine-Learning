import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { Commodity, CommodityType, PriceHistory } from '../models/commodity.model';

@Injectable({ providedIn: 'root' })
export class CommodityService {
  private readonly base = `${environment.apiUrl}/commodities`;

  constructor(private http: HttpClient) {}

  findAll(): Observable<Commodity[]> {
    return this.http.get<Commodity[]>(this.base);
  }

  findById(id: number): Observable<Commodity> {
    return this.http.get<Commodity>(`${this.base}/${id}`);
  }

  findByType(type: CommodityType): Observable<Commodity[]> {
    return this.http.get<Commodity[]>(`${this.base}/type/${type}`);
  }

  search(term: string): Observable<Commodity[]> {
    return this.http.get<Commodity[]>(`${this.base}/search`, { params: { term } });
  }

  create(commodity: Commodity): Observable<Commodity> {
    return this.http.post<Commodity>(this.base, commodity);
  }

  update(id: number, commodity: Commodity): Observable<Commodity> {
    return this.http.put<Commodity>(`${this.base}/${id}`, commodity);
  }

  updatePrice(id: number, price: number): Observable<Commodity> {
    return this.http.patch<Commodity>(`${this.base}/${id}/price`, { price });
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.base}/${id}`);
  }

  getPriceHistory(id: number, limit = 30): Observable<PriceHistory[]> {
    return this.http.get<PriceHistory[]>(`${this.base}/${id}/history`, {
      params: { limit: limit.toString() }
    });
  }
}
