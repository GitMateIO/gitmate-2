import { NgModule }       from '@angular/core';
import { BrowserModule }  from '@angular/platform-browser';
import { MaterialModule  } from '@angular/material';

import { AppComponent }   from './app.component';
import { ToolbarComponent } from './components/toolbar/toolbar.component';

@NgModule({
  imports: [ BrowserModule, MaterialModule.forRoot() ],
  declarations: [ AppComponent, ToolbarComponent ],
  bootstrap:    [ AppComponent ],
})
export class AppModule { }
