import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import 'rxjs/add/operator/map';

import { UserModel, RepoModel, SettingModel } from './models';

@Injectable()
export class ApiService {
  constructor(private http: Http) {}

  getUser() {
    return this.http.get('/api/me').map(response => <UserModel>response.json());
  }

  getRepos() {
    return this.http.get('/api/repos').map(response => <RepoModel[]>response.json());
  }

  addRepo(url: string) {
    return this.http.patch(url, {'active': true}).map(response => <RepoModel>response.json());
  }

  removeRepo(url: string) {
    return this.http.patch(url, {'active': false}).map(response => <RepoModel>response.json());
  }

  getPlugins(repo_plugin_url: string) {
    return this.http.get(repo_plugin_url).map(response => <PluginModel[]>response.json().plugins);
  }
}
