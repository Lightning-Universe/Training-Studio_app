/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

export type ExperimentConfig = {
    name: string;
    best_model_score?: number;
    monitor?: string;
    best_model_path?: string;
    stage?: string;
    params: Record<string, (number | string | Array<number> | Array<string>)>;
    exception?: string;
    progress?: number;
    total_parameters?: string;
    start_time?: string;
    end_time?: string;
};
