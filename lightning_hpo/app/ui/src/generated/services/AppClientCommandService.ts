/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { DeleteDriveConfig } from '../models/DeleteDriveConfig';
import type { DeleteExperimentConfig } from '../models/DeleteExperimentConfig';
import type { DeleteSweepConfig } from '../models/DeleteSweepConfig';
import type { DownloadArtifactsConfig } from '../models/DownloadArtifactsConfig';
import type { DriveConfig } from '../models/DriveConfig';
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
     * Run Experiment
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

    /**
     * Create Drive
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public createDriveCommandCreateDrivePost(
        requestBody: DriveConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/create_drive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Delete Drive
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public deleteDriveCommandDeleteDrivePost(
        requestBody: DeleteDriveConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/delete_drive',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Drives
     * @returns any Successful Response
     * @throws ApiError
     */
    public showDrivesCommandShowDrivesPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_drives',
        });
    }

}
