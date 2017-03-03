import { Component, Input } from '@angular/core';

import { ApiService } from './../../services';
import { RepoModel, PluginModel, SettingModel } from './../../models';

@Component({
  selector: 'plugins',
  templateUrl: './static/app/components/plugins/plugins.component.html',
  styleUrls: ['./static/app/components/plugins/plugins.component.css'],
})
export class PluginsComponent {
  @Input()
  repoid: string;
  plugins: PluginModel[];

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.apiService.getPlugins(this.repoid).subscribe(plugins => this.plugins = plugins);
  }
}
