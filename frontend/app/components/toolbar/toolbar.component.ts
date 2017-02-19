import { Component  } from '@angular/core';

import { ApiService } from './../../services';
import { UserModel } from './../../models';

@Component({
  selector: 'gm-toolbar',
  templateUrl: './static/app/components/toolbar/toolbar.component.html',
  styleUrls: ['./static/app/components/toolbar/toolbar.component.css'],
})
export class ToolbarComponent {
  user: UserModel;
  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getUser().subscribe(user => this.user = user);
  }

  userDefined() {
    return !(this.user == null);
  }

  loginGitHub() {
    window.location.href = '/auth/login/github';
  }

  logout() {
    window.location.href = '/logout';
  }
}

