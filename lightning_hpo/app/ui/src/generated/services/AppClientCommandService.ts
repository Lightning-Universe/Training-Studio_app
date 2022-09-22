/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeleteSweepConfig } from '../models/DeleteSweepConfig';
import type { DownloadArtifactsConfig } from '../models/DownloadArtifactsConfig';
import type { NotebookConfig } from '../models/NotebookConfig';
import type { ShowArtifactsConfig } from '../models/ShowArtifactsConfig';
import type { StopNotebookConfig } from '../models/StopNotebookConfig';
import type { StopSweepConfig } from '../models/StopSweepConfig';
import type { SweepConfig } from '../models/SweepConfig';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AppClientCommandService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Delete Sweep
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteSweepCommandDeleteSweepPost(
        requestBody: DeleteSweepConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/delete_sweep',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Run Sweep
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public runSweepCommandRunSweepPost(
        requestBody: SweepConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/run_sweep',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Sweeps
     * @returns any Successful Response
     * @throws ApiError
     */
    public showSweepsCommandShowSweepsPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_sweeps',
        });
    }

    /**
     * Stop Sweep
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public stopSweepCommandStopSweepPost(
        requestBody: StopSweepConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/stop_sweep',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Run Notebook
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public runNotebookCommandRunNotebookPost(
        requestBody: NotebookConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/run_notebook',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Stop Notebook
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public stopNotebookCommandStopNotebookPost(
        requestBody: StopNotebookConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/stop_notebook',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Notebooks
     * @returns any Successful Response
     * @throws ApiError
     */
    public showNotebooksCommandShowNotebooksPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_notebooks',
        });
    }

    /**
     * Show Artifacts
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public showArtifactsCommandShowArtifactsPost(
        requestBody: ShowArtifactsConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_artifacts',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Download Artifacts
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public downloadArtifactsCommandDownloadArtifactsPost(
        requestBody: DownloadArtifactsConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/download_artifacts',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
