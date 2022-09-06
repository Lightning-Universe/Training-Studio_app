/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type NotebookConfig = {
    id?: string;
    name: string;
    requirements: Array<string>;
    cloud_compute: string;
    status?: string;
    desired_state?: string;
};
