import { Injectable } from '@angular/core';
import { Http } from '@angular/http';
import 'rxjs/add/operator/map';

import { UserModel } from './models';

@Injectable()
export class ApiService {
  constructor(private http: Http) {}

  getUser() {
    return this.http.get('/api/me').map(response => <UserModel>response.json());
  }
}
