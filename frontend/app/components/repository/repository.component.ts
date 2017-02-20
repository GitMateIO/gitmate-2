import { Component, Input } from '@angular/core';

import { ApiService } from './../../services';
import { RepoModel } from './../../models';

@Component({
  selector: 'repository',
  templateUrl: './static/app/components/repository/repository.component.html',
  styleUrls: ['./static/app/components/repository/repository.component.css'],
})
export class RepositoryComponent {
  @Input()
  repo: RepoModel;

  constructor(private apiService: ApiService) {}

  enable() {
    this.apiService.addRepo(this.repo.id).subscribe(repo => this.repo = repo);
  }

  disable() {
    this.apiService.removeRepo(this.repo.id).subscribe(repo => this.repo = repo);
  }
}
