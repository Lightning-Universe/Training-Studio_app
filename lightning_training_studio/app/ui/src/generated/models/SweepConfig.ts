/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */

import type { Distributions } from './Distributions';
import type { ExperimentConfig } from './ExperimentConfig';

export type SweepConfig = {
    sweep_id: string;
    script_path: string;
    total_experiments: number;
    parallel_experiments: number;
    total_experiments_done?: number;
    requirements: Array<string>;
    script_args: Array<string>;
    algorithm: string;
    distributions: Record<string, Distributions>;
    logger_url?: string;
    experiments: Record<string, ExperimentConfig>;
    framework: string;
    cloud_compute?: string;
    num_nodes?: number;
    logger: string;
    direction: string;
    stage?: string;
    desired_stage?: string;
    disk_size?: number;
    data: Record<string, string>;
    username?: string;
};
