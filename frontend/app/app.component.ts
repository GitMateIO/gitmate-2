import { Component } from '@angular/core';

@Component({
  selector: 'my-app',
  template: `

  <h1>Hello {{name}}</h1>
  <h2>Login</h2>
  <a href="http://localhost:8000/auth/login/github/">GitHub</a>
  <a href="http://localhost:8000/auth/login/gitlab/">GitLab</a>
  <a href="http://localhost:8000/auth/login/bitbucket/">BitBucket</a>

  `,
})
export class AppComponent  { name = 'Angular'; }
