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
     * To delete a sweep, note that the artifacts will still be available after the operation is complete.
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
     *
     * To run a sweep, provide a script, the cloud compute to use, and an optional data.
     * Hyperparameters can be provided as lists or using distributions. Hydra multirun syntax is also supported.
     *
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
     * To show all sweeps and their statuses, or the experiments for a given sweep.
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
     * To stop all experiments in a sweep, note that currently sweeps cannot be resumed.
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
     * To run an experiment, provide a script, the cloud compute to use, and optional data.
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
     * To stop an experiment, note that currently experiments cannot be resumed.
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
     * To show experiments and their statuses.
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
     * To delete an experiment. The artifacts are still available after the operation is complete.
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
     * To show artifacts for experiments or sweeps.
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
     * Download artifacts for experiments or sweeps.
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
     * Add Dataset
     *
     * To create a data association, provide a public S3 bucket and an optional mount point.
     * The contents of the bucket can then be accessed through the file system in experiments and sweeps.
     *
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public addDatasetCommandAddDatasetPost(
        requestBody: DataConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/add_dataset',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Remove Dataset
     * To delete a data association, note this doesn't delete the data, but only the reference.
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public removeDatasetCommandRemoveDatasetPost(
        requestBody: DeleteDataConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/remove_dataset',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Datasets
     * To list all data associations.
     * @returns any Successful Response
     * @throws ApiError
     */
    public showDatasetsCommandShowDatasetsPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_datasets',
        });
    }

    /**
     * Show Logs
     * To show the logs of an experiment or sweep, use the option to follow the logs as they stream.
     * @returns any Successful Response
     * @throws ApiError
     */
    public showLogsCommandShowLogsPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_logs',
        });
    }

}
