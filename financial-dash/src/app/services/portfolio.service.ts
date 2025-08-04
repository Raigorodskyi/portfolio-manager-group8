import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class PortfolioService {
  private apiUrl = 'http://127.0.0.1:5000/api/total_value';

  constructor(private http: HttpClient) {}

  getTotalValue(): Observable<{ total_value: number; user_id: number }> {
    return this.http.get<{ total_value: number; user_id: number }>(this.apiUrl);
  }
}