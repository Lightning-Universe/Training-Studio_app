/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Params } from './Params';

export type TrialConfig = {
    best_model_score?: number;
    monitor?: string;
    best_model_path?: string;
    status?: string;
    params: Params;
    exception?: string;
};
