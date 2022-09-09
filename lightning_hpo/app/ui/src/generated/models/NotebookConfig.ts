/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type NotebookConfig = {
    notebook_name: string;
    requirements: Array<string>;
    cloud_compute: string;
    state?: string;
    desired_state?: string;
    url?: string;
};
