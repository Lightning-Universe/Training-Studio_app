/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StopTensorboardConfig } from '../models/StopTensorboardConfig';
import type { TensorboardConfig } from '../models/TensorboardConfig';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AppCommandService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Run Tensorboard
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public runTensorboardCommandRunTensorboardPost(
        requestBody: TensorboardConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/run_tensorboard',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Show Tensorboards
     * @returns any Successful Response
     * @throws ApiError
     */
    public showTensorboardsCommandShowTensorboardsPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/show_tensorboards',
        });
    }

    /**
     * Stop Tensorboard
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public stopTensorboardCommandStopTensorboardPost(
        requestBody: StopTensorboardConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/command/stop_tensorboard',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

}
