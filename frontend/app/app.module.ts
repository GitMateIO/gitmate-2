import { NgModule }       from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { MaterialModule  } from '@angular/material';
import { HttpModule, XSRFStrategy, CookieXSRFStrategy } from '@angular/http';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent }   from './app.component';
import { ToolbarComponent } from './components/toolbar/toolbar.component';
import { ApiService  } from './services';
import { HomeComponent } from './components/home-view/home-view.component';
import { NotFoundComponent } from './components/not-found-view/not-found-view.component';
import { ProfileComponent } from './components/profile-view/profile-view.component';
import { RepositoriesComponent } from './components/repositories-view/repositories-view.component';
import { RepositoryComponent } from './components/repository/repository.component';

const appRoutes: Routes = [
  {path: 'home', component: HomeComponent},
  {path: 'profile', component: ProfileComponent},
  {path: 'repositories', component: RepositoriesComponent},
  {path: '', redirectTo: '/home', pathMatch: 'full' },
  {path: '**', component: NotFoundComponent},
];

@NgModule({
  imports: [ BrowserModule, MaterialModule.forRoot(), HttpModule, RouterModule.forRoot(appRoutes)],
  declarations: [
    AppComponent,
    ToolbarComponent,
    HomeComponent,
    NotFoundComponent,
    ProfileComponent,
    RepositoriesComponent,
    RepositoryComponent
  ],
  bootstrap:    [ AppComponent ],
  providers: [
    ApiService,
    {
      provide: XSRFStrategy,
      useValue: new CookieXSRFStrategy('csrftoken', 'X-CSRFToken')
    }
  ],
})
export class AppModule { }
