/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type TrialConfig = {
    best_model_score?: number;
    monitor?: string;
    best_model_path?: string;
    stage?: string;
    params: Record<string, (number | string | Array<number> | Array<string>)>;
    exception?: string;
    progress?: number;
};
