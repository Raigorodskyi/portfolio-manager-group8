import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { OverviewComponent } from './overview/overview.component';

@Component({
  selector: 'app-root',
  imports: [ OverviewComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'financial-dash';
}
