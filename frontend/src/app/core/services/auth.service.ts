import { HttpClient } from '@angular/common/http';
import { Injectable, computed, signal } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

import { environment } from '../../../environments/environment';
import { TokenResponse, User } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly accessTokenKey = 'taxshield.access_token';
  private readonly refreshTokenKey = 'taxshield.refresh_token';
  private readonly userKey = 'taxshield.user';
  private readonly userSignal = signal<User | null>(this.restoreUser());

  readonly currentUser = this.userSignal.asReadonly();
  readonly isAuthenticated = computed(() => Boolean(this.userSignal() && this.accessToken));

  constructor(private readonly http: HttpClient, private readonly router: Router) {}

  get accessToken(): string | null {
    return localStorage.getItem(this.accessTokenKey);
  }

  register(payload: { email: string; full_name: string; password: string }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiBaseUrl}/auth/register`, payload).pipe(
      tap((response) => this.setSession(response))
    );
  }

  login(payload: { email: string; password: string }): Observable<TokenResponse> {
    return this.http.post<TokenResponse>(`${environment.apiBaseUrl}/auth/login`, payload).pipe(
      tap((response) => this.setSession(response))
    );
  }

  logout(): void {
    const refreshToken = localStorage.getItem(this.refreshTokenKey);
    if (refreshToken) {
      this.http.post(`${environment.apiBaseUrl}/auth/logout`, { refresh_token: refreshToken }).subscribe();
    }
    localStorage.removeItem(this.accessTokenKey);
    localStorage.removeItem(this.refreshTokenKey);
    localStorage.removeItem(this.userKey);
    this.userSignal.set(null);
    this.router.navigateByUrl('/login');
  }

  private setSession(response: TokenResponse): void {
    localStorage.setItem(this.accessTokenKey, response.access_token);
    localStorage.setItem(this.refreshTokenKey, response.refresh_token);
    localStorage.setItem(this.userKey, JSON.stringify(response.user));
    this.userSignal.set(response.user);
  }

  private restoreUser(): User | null {
    const raw = localStorage.getItem(this.userKey);
    if (!raw) {
      return null;
    }
    try {
      return JSON.parse(raw) as User;
    } catch {
      localStorage.removeItem(this.userKey);
      return null;
    }
  }
}
