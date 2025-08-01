import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { OverviewComponent } from './overview/overview.component';
import { NgChartsModule } from 'ng2-charts';

@Component({
  selector: 'app-root',
  imports: [ OverviewComponent, NgChartsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'financial-dash';
}
