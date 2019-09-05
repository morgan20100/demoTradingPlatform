import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { CookieService } from 'ngx-cookie-service';

import { StreamPrice } from './models/streamPrice';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  baseUrl = 'http://127.0.0.1:8000/';

  token = this.cookieService.get('mr-token');
  headers = new HttpHeaders({
    'Content-Type': 'application/json'
  });

  baseMovieUrl = `${this.baseUrl}api/movies/`;
  baseStreamPriceUrl = `${this.baseUrl}api/streamPrice/`;

  constructor(
    private httpClient: HttpClient,
    private cookieService: CookieService
  ) {}

  getStreamPrices() {
    return this.httpClient.get<StreamPrice[]>(this.baseStreamPriceUrl, {
      headers: this.getAuthHeaders()
    });
  }

  loginUser(authData) {
    const body = JSON.stringify(authData);
    return this.httpClient.post(`${this.baseUrl}auth/`, body, {
      headers: this.headers
    });
  }

  registerUser(authData) {
    const body = JSON.stringify(authData);
    return this.httpClient.post(`${this.baseUrl}user/users/`, body, {
      headers: this.headers
    });
  }

  getAuthHeaders() {
    const token = this.cookieService.get('mr-token');
    return new HttpHeaders({
      'Content-Type': 'application/json',
      Authorization: `Token ${token}`
    });
  }
}
