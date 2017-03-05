export class UserModel {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
}

export class RepoModel {
  id: string;
  plugin: string;
  provider: string;
  full_name: string;
  active: boolean;
  user: number;
}

export class SettingModel {
  name: string;
  value: any;
  type: string;
  description: string;
}

export class PluginModel {
  name: string;
  active: boolean;
  settings: SettingModel[];
}
