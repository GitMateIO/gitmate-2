export class UserModel {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
}

export class RepoModel {
  id: string;
  provider: string;
  full_name: string;
  active: boolean;
  user: number;
}
