/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Distributions } from './Distributions';
import type { TrialConfig } from './TrialConfig';

export type SweepConfig = {
    id?: number;
    sweep_id: string;
    script_path: string;
    n_trials: number;
    simultaneous_trials: number;
    trials_done?: number;
    requirements: Array<string>;
    script_args: Array<string>;
    distributions: Record<string, Distributions>;
    url?: string;
    trials: Record<string, TrialConfig>;
    framework: string;
    cloud_compute: string;
    num_nodes?: number;
    logger: string;
    direction: string;
    status?: string;
};
