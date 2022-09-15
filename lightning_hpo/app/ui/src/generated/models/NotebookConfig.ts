/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type NotebookConfig = {
    notebook_name: string;
    requirements: Array<string>;
    cloud_compute: string;
    stage?: string;
    desired_stage?: string;
    url?: string;
    start_time?: number;
};
