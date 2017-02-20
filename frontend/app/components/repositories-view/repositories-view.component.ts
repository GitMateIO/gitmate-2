import { Component } from '@angular/core';

import { ApiService } from './../../services';
import { RepoModel } from './../../models';

@Component({
  selector: 'view-repositories',
  template: '<repository *ngFor="let repo of repos" [repo]="repo"></repository>',
})
export class RepositoriesComponent {
  repos: RepoModel[] = [];
  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getRepos().subscribe(repos => this.repos = repos);
  }
}

