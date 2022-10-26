/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { StopTensorboardConfig } from '../models/StopTensorboardConfig';
import type { TensorboardConfig } from '../models/TensorboardConfig';

import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AppApiService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

    /**
     * Run Tensorboard
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public runTensorboardApiRunTensorboardPost(
        requestBody: TensorboardConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/run/tensorboard',
            body: requestBody,
            mediaType: 'application/json',
            errors: {
                422: `Validation Error`,
            },
        });
    }

    /**
     * Stop Tensorboard
     * @param requestBody
     * @returns any Successful Response
     * @throws ApiError
     */
    public stopTensorboardApiStopTensorboardPost(
        requestBody: StopTensorboardConfig,
    ): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/stop/tensorboard',
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
    public showTensorboardsApiShowTensorboardsPost(): CancelablePromise<any> {
        return this.httpRequest.request({
            method: 'POST',
            url: '/api/show/tensorboards',
        });
    }

}
