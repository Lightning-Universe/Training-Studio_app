/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DataConfig } from '../models/DataConfig';
import type { DeleteDataConfig } from '../models/DeleteDataConfig';
import type { DeleteExperimentConfig } from '../models/DeleteExperimentConfig';
import type { DeleteSweepConfig } from '../models/DeleteSweepConfig';
import type { DownloadArtifactsConfig } from '../models/DownloadArtifactsConfig';
import type { ShowArtifactsConfig } from '../models/ShowArtifactsConfig';
import type { StopExperimentConfig } from '../models/StopExperimentConfig';
import type { StopSweepConfig } from '../models/StopSweepConfig';
import type { SweepConfig } from '../models/SweepConfig';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AppClientCommandService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Delete Sweep
     * Delete a Sweep.
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
     * Run a Sweep.
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
     * Show all Sweeps or the Experiments from a given Sweep.
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
     * Stop a Sweep.
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
     * Run Experiment
     * Run an Experiment.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public runExperimentCommandRunExperimentPost(
        requestBody: SweepConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/run_experiment',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Stop Experiment
     * Stop an Experiment.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public stopExperimentCommandStopExperimentPost(
        requestBody: StopExperimentConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/stop_experiment',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Experiments
     * Show Experiments.
     * @returns any Successful Response
     * @throws ApiError
     */
    public showExperimentsCommandShowExperimentsPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_experiments',
        });
    }

    /**
     * Delete Experiment
     * Delete an Experiment.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteExperimentCommandDeleteExperimentPost(
        requestBody: DeleteExperimentConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/delete_experiment',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Artifacts
     * Show artifacts.
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
     * Download an artifact.
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

    /**
     * Create Data
     * Create Data.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public createDataCommandCreateDataPost(
        requestBody: DataConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/create_data',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Data
     * Delete Data.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteDataCommandDeleteDataPost(
        requestBody: DeleteDataConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/delete_data',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Data
     * List all Data.
     * @returns any Successful Response
     * @throws ApiError
     */
    public showDataCommandShowDataPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_data',
        });
    }

}
