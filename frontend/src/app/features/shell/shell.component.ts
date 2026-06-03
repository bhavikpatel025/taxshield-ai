import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [
    RouterOutlet,
    RouterLink,
    RouterLinkActive,
    MatButtonModule,
    MatIconModule,
    MatSidenavModule,
    MatToolbarModule
  ],
  template: `
    <mat-sidenav-container class="app-frame">
      <mat-sidenav mode="side" opened class="sidebar">
        <div class="brand">
          <mat-icon>shield</mat-icon>
          <span>TaxShield AI</span>
        </div>
        <nav>
          <a routerLink="/dashboard" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">
            <mat-icon>dashboard</mat-icon>
            Dashboard
          </a>
          <a routerLink="/dashboard/documents" routerLinkActive="active">
            <mat-icon>upload_file</mat-icon>
            Documents
          </a>
          <a routerLink="/dashboard/qa" routerLinkActive="active">
            <mat-icon>forum</mat-icon>
            Tax Q&A
          </a>
        </nav>
      </mat-sidenav>
      <mat-sidenav-content>
        <mat-toolbar class="topbar">
          <span></span>
          <div class="user">
            <mat-icon>account_circle</mat-icon>
            <span>{{ authService.currentUser()?.email }}</span>
            <button mat-icon-button type="button" aria-label="Sign out" (click)="authService.logout()">
              <mat-icon>logout</mat-icon>
            </button>
          </div>
        </mat-toolbar>
        <main class="content">
          <router-outlet />
        </main>
      </mat-sidenav-content>
    </mat-sidenav-container>
  `
})
export class ShellComponent {
  constructor(readonly authService: AuthService) {}
}
