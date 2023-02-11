import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { requestAPI } from './handler';

/**
 * Initialization data for the jupyter-gopls extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'jupyter-gopls:plugin',
  autoStart: true,
  activate: (app: JupyterFrontEnd) => {
    console.log('JupyterLab extension jupyter-gopls is activated!');

    requestAPI<any>('get_example')
      .then(data => {
        console.log(data);
      })
      .catch(reason => {
        console.error(
          `The jupyter_gopls server extension appears to be missing.\n${reason}`
        );
      });
  }
};

export default plugin;
