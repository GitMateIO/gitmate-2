import { NgModule }       from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { MaterialModule  } from '@angular/material';
import { HttpModule } from '@angular/http';

import { AppComponent }   from './app.component';
import { ToolbarComponent } from './components/toolbar/toolbar.component';
import { ApiService  } from './services';

@NgModule({
  imports: [ BrowserModule, MaterialModule.forRoot(), HttpModule],
  declarations: [ AppComponent, ToolbarComponent ],
  bootstrap:    [ AppComponent ],
  providers: [ ApiService ],
})
export class AppModule { }
