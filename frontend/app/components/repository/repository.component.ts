import { Component, Input } from '@angular/core';

import { RepoModel } from './../../models';

@Component({
  selector: 'repository',
  templateUrl: './static/app/components/repository/repository.component.html',
  styleUrls: ['./static/app/components/repository/repository.component.css'],
})
export class RepositoryComponent {
  @Input()
  repo: RepoModel;

}
