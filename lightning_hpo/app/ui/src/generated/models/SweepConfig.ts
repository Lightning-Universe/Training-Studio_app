/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Distributions } from './Distributions';
import type { TrialConfig } from './TrialConfig';

export type SweepConfig = {
    sweep_id: string;
    script_path: string;
    n_trials: number;
    simultaneous_trials: number;
    trials_done?: number;
    requirements: Array<string>;
    script_args: Array<string>;
    algorithm: string;
    distributions: Record<string, Distributions>;
    logger_url?: string;
    trials: Record<string, TrialConfig>;
    framework: string;
    cloud_compute?: string;
    num_nodes?: number;
    logger: string;
    direction: string;
    stage?: string;
    desired_stage?: string;
    disk_size?: number;
};
