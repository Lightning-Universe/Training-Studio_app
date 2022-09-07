/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { CancelablePromise } from '../core/CancelablePromise';
import type { BaseHttpRequest } from '../core/BaseHttpRequest';

export class AppCommandService {

    constructor(public readonly httpRequest: BaseHttpRequest) {}

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

}
